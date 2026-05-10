import argparse
import asyncio
import copy
import json
import logging
import pathlib
import re
from typing import List, Optional, Tuple, Union

import dateparser
import pandas as pd
import pydash
from deepeval.metrics.summarization.schema import Answers
from pydantic import BaseModel

from constants import (
    LLM_CONCURRENCY,
    MARKETS,
    get_ground_truth_folder,
    get_subsection_info,
    get_summary_length_tolerance_for_track,
)
from contexts import trace_folder_cv
from evaluation.llms.llm_util import chat_with_llm
from evaluation.llms.tools import NUM_COMPARATOR_TOOLS
from evaluation.other_util import (
    are_dates_near,
    compose_item_trace_id,
    find_best_matches,
    get_company_from_report_name,
    get_location_from_company_name,
    is_prediction_value_invalid,
    is_value_missing,
    parse_date,
    setup_logger,
)
from evaluation.prompts.evaluator_prompt import (
    A_PROMPT,
    C_PROMPT,
    I_PROMPT,
    R_PROMPT,
    compose_extraction_batch_input,
    compose_extraction_single_input,
)
from evaluation.prompts.prompt_util import compose_question
from evaluation.section_util import SType

logger = logging.getLogger(__name__)


class CriteriaResult(BaseModel):
    criteria_name: str
    mark: float
    full_mark: float
    reason: str


class AnalysisResult(BaseModel):
    verdicts: List[CriteriaResult]


class ItemResult(BaseModel):
    idx: int
    score: float


class BatchValueResult(BaseModel):
    items: List[ItemResult]


class SingleValueResult(BaseModel):
    score: float


def get_item_category(item: dict) -> str:
    if 'category' in item:
        return item['category']
    elif 'year' in item:
        return str(item['year'])
    else:
        return 'Value'


def get_item_weight(subsection_cfg: dict, subsection_no: str, field_name: str, field_category: str) -> float:
    subsection_meta = subsection_cfg[subsection_no]
    weight = subsection_meta['item_weights'][(field_name, field_category)]
    return weight


def get_question_level(question_type: str) -> str:
    question_type = SType[question_type]
    return question_type.to_level()

def get_question_level_back(question_type: str) -> str:
    # back_compatible_map = {'R1': 'E1', 'R2': 'E2', 'R3': 'E3', 'R4': 'E4', 'A': 'S', 'I': 'A'}
    back_compatible_map = {'E1': 'R1', 'E2': 'R2', 'E3': 'R3', 'E4': 'R4', 'S': 'A', 'A': 'I', 'A2': 'I2', 'A3': 'I3'}
    question_type = back_compatible_map[question_type] if question_type in back_compatible_map else question_type
    question_type = SType[question_type]
    return question_type.to_level()

def create_full_mark_detail(gold_item: dict, prediction_item: dict, subsection_meta: dict) -> dict:
    prediction_value = pydash.get(prediction_item, 'value')
    gold_value = gold_item['value']
    mark_details = {
        'section_no': subsection_meta['section_no'],
        'no': subsection_meta['no'],
        'type': subsection_meta['type'],
        'field': gold_item['name'],
        'year': str(gold_item.get('year') or ''),
        'category': get_item_category(gold_item),
        'gold': gold_value,
        'prediction': prediction_value,
        'mark': 100,
        'adjusted_mark': 100,
        'explanation': [],
    }
    return mark_details

def create_zero_mark_detail(gold_item: dict, subsection_meta: dict) -> dict:
    gold_value = gold_item['value']
    mark_details = {
        'section_no': subsection_meta['section_no'],
        'no': subsection_meta['no'],
        'type': subsection_meta['type'],
        'field': gold_item['name'],
        'year': str(gold_item.get('year') or ''),
        'category': get_item_category(gold_item),
        'gold': gold_value,
        'prediction': '',
        'mark': 0,
        'adjusted_mark': 0,
        'explanation': [],
    }
    return mark_details


def pre_evaluate_on_edge_cases(gold_item: dict, prediction_item: dict, subsection_meta: dict) -> dict:
    prediction_value = pydash.get(prediction_item, 'value')
    gold_value = gold_item['value']

    mark_details = None
    if is_value_missing(gold_value):
        mark_details = create_full_mark_detail(gold_item, prediction_item, subsection_meta)
    elif is_prediction_value_invalid(prediction_value):
         mark_details = create_zero_mark_detail(gold_item, subsection_meta)

    return mark_details


def filter_items_to_evaluate(task_dict: dict, subsection_meta: dict) -> Tuple[list, list]:
    prediction_by_item = pydash.key_by(
        task_dict['prediction'].get('items') or [], lambda i: (i['name'], str(i.get('year') or ''))
    )

    mark_details = []

    items_to_evaluate = []
    for idx, i in enumerate(task_dict['gold']['items']):
        item_name = i['name']
        item_year = str(i.get('year') or '')
        prediction_item = prediction_by_item.get((item_name, item_year)) or {}

        edge_mark_details = pre_evaluate_on_edge_cases(i, prediction_item, subsection_meta)
        if edge_mark_details:
            mark_details.append(edge_mark_details)
            continue

        items_to_evaluate.append(idx)

    return items_to_evaluate, mark_details


async def _evaluate_recognition_items(
    semaphore: asyncio.Semaphore, batch_items: list, subsection_meta: dict, trace_id: str, model: str = 'gpt-4.1'
) -> list:
    mark_details = []
    prompt = R_PROMPT.format(num=len(batch_items), input=compose_extraction_batch_input(batch_items))

    async with semaphore:
        res = await chat_with_llm(prompt, model=model, schema=BatchValueResult, trace_id=trace_id)

        for evaluation_result in res.items:
            evaluation_input = batch_items[evaluation_result.idx - 1]
            mark = 100 if evaluation_result.score else 0
            adjusted_mark = mark
            mark_details.append(
                {
                    'section_no': subsection_meta['section_no'],
                    'no': subsection_meta['no'],
                    'type': subsection_meta['type'],
                    'field': evaluation_input['name'],  # in 2024; position of xxx
                    'year': evaluation_input['year'],
                    'category': evaluation_input['category'],
                    'gold': evaluation_input['gold'],
                    'prediction': evaluation_input['prediction'],
                    'mark': mark,
                    'adjusted_mark': adjusted_mark,
                    'explanation': [],
                }
            )

    return mark_details

async def _evaluate_one_recognition_item(
    semaphore: asyncio.Semaphore, gold_item: dict, prediction_item: dict, subsection_meta: dict, model: str = 'gpt-4.1'
) -> dict:
    mark_details = pre_evaluate_on_edge_cases(gold_item, prediction_item, subsection_meta)
    if mark_details:
        return mark_details
    batched_mark_details = await _evaluate_recognition_items(
        semaphore,
        [
            {
                'question': gold_item['name'],
                'gold': gold_item['value'],
                'prediction': prediction_item['value'],
                'name': gold_item['name'],
                'year': str(gold_item.get('year') or ''),
                'category': get_item_category(gold_item),
            }
        ],
        subsection_meta,
        subsection_meta['no'],
        model=model,
    )
    return batched_mark_details[0]


async def evaluate_recognition_items(
    semaphore, items_to_evaluate: list, sub_section_meta: dict, batch_size: int = 5, model: str = 'gpt-4.1'
) -> list:
    batch_tasks = []
    for idx in range(0, len(items_to_evaluate), batch_size):
        batch_items = items_to_evaluate[idx : idx + batch_size]
        trace_id = f'{sub_section_meta["no"]}_part{len(batch_tasks) + 1}'
        batch_tasks.append(_evaluate_recognition_items(semaphore, batch_items, sub_section_meta, trace_id, model=model))

    batch_results = await asyncio.gather(*batch_tasks)

    mark_details = pydash.flatten(batch_results)

    return mark_details


async def evaluate_recognition_question(
    semaphore: asyncio.Semaphore, task_dict: dict, model: str = 'gpt-4.1'
) -> list:
    prediction_by_item = pydash.key_by(
        task_dict['prediction'].get('items') or [], lambda i: (i['name'], str(i.get('year') or ''))
    )

    subsection_meta = task_dict['meta']

    items_to_evaluate = []
    valid_gold_ids, mark_details = filter_items_to_evaluate(task_dict, subsection_meta)
    for idx in valid_gold_ids:
        gold_item = task_dict['gold']['items'][idx]
        item_name = gold_item['name']
        item_year = str(gold_item.get('year') or '')
        item_category = get_item_category(gold_item)
        prediction_item = prediction_by_item.get((item_name, item_year))
        question = f'Value of {item_name} in {item_year}' if item_year else f'Value of {item_name}'
        item_to_evaluate = {
            'question': question,
            'gold': gold_item['value'],
            'prediction': prediction_item['value'],
            'name': item_name,
            'year': item_year,
            'category': item_category,
        }
        items_to_evaluate.append(item_to_evaluate)

    if not items_to_evaluate:
        return mark_details

    evaluated_mark_details = await evaluate_recognition_items(
        semaphore, items_to_evaluate, subsection_meta, model=model
    )

    mark_details.extend(evaluated_mark_details)

    return mark_details


async def evaluate_recognition_obj_question(
    semaphore: asyncio.Semaphore, task_dict: dict, model: str = 'gpt-4.1'
) -> list:
    ori_gold_items = task_dict['gold']['items']
    ori_prediction_items = task_dict['prediction'].get('items') or []
    subsection_meta = task_dict['meta']

    mark_details = []

    primary_key = list(ori_gold_items[0]['value'].keys())[0]

    ori_idx_to_valid_idx = {}
    valid_gold_idx = 0
    gold_values = []
    for idx, gold_item in enumerate(ori_gold_items):
        if is_value_missing(gold_item['value'][primary_key]):
            for obj_key, obj_value in gold_item['value'].items():
                gold_point = {'name': obj_key, 'value': obj_value, 'category': gold_item['category']}
                # not sure which prediction item for pairing
                fake_prediction_point = {'name': obj_key, 'value': 'NAN'}
                mark_details.append(create_full_mark_detail(gold_point, fake_prediction_point, subsection_meta))
            continue
        gold_values.append(gold_item['value'][primary_key])
        ori_idx_to_valid_idx[idx] = valid_gold_idx
        valid_gold_idx += 1

    prediction_values = [i[primary_key] for i in ori_prediction_items]

    gold2pred = find_best_matches(gold_values, prediction_values)

    items_to_evaluate = []
    for ori_idx, gold_item in enumerate(ori_gold_items):
        if ori_idx not in ori_idx_to_valid_idx:
            continue
        idx = ori_idx_to_valid_idx[ori_idx]
        if idx not in gold2pred:
            for obj_key, obj_value in gold_item['value'].items():
                item_dict = {'name': obj_key, 'value': obj_value, 'category': gold_item['category']}
                mark_details.append(create_zero_mark_detail(item_dict, subsection_meta))
        else:
            prediction_item = ori_prediction_items[gold2pred[idx]]
            for obj_key, obj_value in gold_item['value'].items():
                prediction_obj_value = pydash.get(prediction_item, [obj_key]) or ''

                gold_point = {'name': obj_key, 'value': obj_value, 'category': gold_item['category']}
                prediction_point = {'name': obj_key, 'value': prediction_obj_value}

                edge_mark_details = pre_evaluate_on_edge_cases(gold_point, prediction_point, subsection_meta)
                if edge_mark_details:
                    mark_details.append(edge_mark_details)
                    continue

                if obj_key == 'Total Income':
                    numeric_mark_detail = await _evaluate_one_calculation_item(
                        semaphore, gold_point, prediction_point, subsection_meta, model=model
                    )
                    mark_details.append(numeric_mark_detail)
                    continue

                question = f'Value of {obj_key}_{idx}'
                item_to_evaluate = {
                    'question': question,
                    'gold': obj_value,
                    'prediction': prediction_obj_value,
                    'name': obj_key,
                    'year': '',
                    'category': gold_item['category'],
                }
                items_to_evaluate.append(item_to_evaluate)

    evaluated_mark_details = await evaluate_recognition_items(
        semaphore, items_to_evaluate, subsection_meta, model=model
    )
    mark_details.extend(evaluated_mark_details)
    return mark_details


async def _evaluate_one_calculation_item(
    semaphore: asyncio.Semaphore, gold_item: dict, prediction_item: dict, subsection_meta: dict, model: str = 'gpt-4.1'
) -> dict:

    mark_detail = pre_evaluate_on_edge_cases(gold_item, prediction_item, subsection_meta)
    if mark_detail:
        return mark_detail

    item_name = gold_item['name']
    item_year = str(gold_item.get('year') or '')
    item_category = get_item_category(gold_item)
    question = f'Value of {item_name} in {item_year}' if item_year else f'Value of {item_name}'
    item_to_evaluate = {
        'question': question,
        'gold': gold_item['value'],
        'prediction': prediction_item['value'],
        'name': item_name,
        'year': item_year,
    }

    prompt = C_PROMPT.format(input=compose_extraction_single_input(item_to_evaluate))

    async with semaphore:
        res = await chat_with_llm(
            prompt,
            model=model,
            tools=NUM_COMPARATOR_TOOLS,
            schema=SingleValueResult,
            trace_id=compose_item_trace_id(subsection_meta['no'], item_name, item_year),
        )
    mark = 100 if res.score else 0
    adjusted_mark = mark
    mark_detail = {
        'section_no': subsection_meta['section_no'],
        'no': subsection_meta['no'],
        'type': subsection_meta['type'],
        'field': item_name,  # in 2024; position of xxx
        'year': item_year,
        'category': item_category,
        'gold': item_to_evaluate['gold'],
        'prediction': item_to_evaluate['prediction'],
        'mark': mark,
        'adjusted_mark': adjusted_mark,
        'explanation': [],
    }

    return mark_detail


def length_penalty(prediction: str, gold: str, summary_length_tolerance: float) -> float:
    if not isinstance(gold, str) or not isinstance(prediction, str):
        raise ValueError('Both gold and prediction must be strings')

    if len(gold) == 0:
        raise ValueError('gold cannot be empty')

    len_ground_truth = len(gold)
    len_submitted = len(prediction)

    excess_ratio = abs(len_submitted - len_ground_truth) / len_ground_truth

    penalty = 5 / (5 + max(excess_ratio - summary_length_tolerance, 0))

    return penalty


async def _evaluate_one_abstraction_item(
    semaphore: asyncio.Semaphore,
    gold_item: dict,
    prediction_item: dict,
    sub_section_meta: dict,
    summary_length_tolerance: float,
    model: str = 'gpt-4.1'
) -> dict:

    mark_detail = pre_evaluate_on_edge_cases(gold_item, prediction_item, sub_section_meta)
    if mark_detail:
        return mark_detail

    item_name = gold_item['name']
    item_year = str(gold_item.get('year') or '')
    item_category = get_item_category(gold_item)

    prompt = A_PROMPT.format(questions=gold_item['marking'], text=prediction_item['value'])
    async with semaphore:
        res = await chat_with_llm(
            prompt,
            model=model,
            schema=Answers,
            trace_id=compose_item_trace_id(sub_section_meta['no'], item_name, item_year),
        )

    if len(res.answers) != len(gold_item['marking']):
        raise ValueError("Number of verdicts generated does not equal.")

    explanation = []
    correct = 0
    for idx, one in enumerate(res.answers):
        explanation.append({'prediction': one, 'gold': 'yes', 'question': gold_item['marking'][idx]})
        if one.lower() == 'yes':
            correct += 1

    mark = round(correct / len(res.answers) * 100, 2)
    penalty = length_penalty(prediction_item['value'], gold_item['value'], summary_length_tolerance)
    adjusted_mark = round(penalty * mark, 2)

    mark_detail = {
        'section_no': sub_section_meta['section_no'],
        'no': sub_section_meta['no'],
        'type': sub_section_meta['type'],
        'field': item_name,
        'year': item_year,
        'category': item_category,
        'gold': gold_item['value'],
        'prediction': prediction_item['value'],
        'mark': mark,
        'adjusted_mark': adjusted_mark,
        'explanation': explanation,
    }

    return mark_detail


async def _evaluate_one_interpretation_item(
    semaphore: asyncio.Semaphore,
    gold_item: dict,
    prediction_item: dict,
    sub_section_meta: dict,
    model: str = 'gpt-4.1',
) -> dict:
    item_name = gold_item['name']
    item_year = str(gold_item.get('year') or '')
    item_category = get_item_category(gold_item)

    prompt = I_PROMPT.format(
        question=compose_question(sub_section_name=sub_section_meta['name'], point_name=item_name),
        standard_answer=gold_item['value'],
        marking_criteria=gold_item['marking'],
        contestant_answer=prediction_item['value'],
    )
    async with semaphore:
        res = await chat_with_llm(
            prompt,
            model=model,
            schema=AnalysisResult,
            trace_id=compose_item_trace_id(sub_section_meta['no'], item_name, item_year),
        )

    scaled_res = [
        {
            'criteria_name': one.criteria_name,
            'mark': one.mark * 10,
            'full_mark': one.full_mark * 10,
            'reason': one.reason,
        }
        for one in res.verdicts
    ]

    mark = sum([one['mark'] for one in scaled_res])
    adjusted_mark = mark

    mark_detail = {
        'section_no': sub_section_meta['section_no'],
        'no': sub_section_meta['no'],
        'type': sub_section_meta['type'],
        'field': item_name,
        'year': item_year,
        'category': item_category,
        'gold': gold_item['value'],
        'prediction': prediction_item['value'],
        'mark': mark,
        'adjusted_mark': adjusted_mark,
        'explanation': scaled_res,
    }

    return mark_detail


async def evaluate_question_by_item(
    question_type: str,
    semaphore: asyncio.Semaphore,
    task_dict: dict,
    summary_length_tolerance: Optional[float] = None,
    model: str = 'gpt-4.1'
) -> list:
    """
    Create tasks for each item in the question.
    """

    prediction_by_item = pydash.key_by(
        task_dict['prediction'].get('items') or [], lambda i: (i['name'], str(i.get('year') or ''))
    )

    subsection_meta = task_dict['meta']

    valid_gold_ids, mark_details = filter_items_to_evaluate(task_dict, subsection_meta)

    batch_tasks = []
    for idx in valid_gold_ids:
        gold_item = task_dict['gold']['items'][idx]
        item_name = gold_item['name']
        item_year = str(gold_item.get('year') or '')
        prediction_item = prediction_by_item.get((item_name, item_year))

        if question_type == 'I':
            batch_tasks.append(
                _evaluate_one_interpretation_item(semaphore, gold_item, prediction_item, subsection_meta, model=model)
            )
        elif question_type == 'A':
            assert summary_length_tolerance is not None
            batch_tasks.append(
                _evaluate_one_abstraction_item(
                    semaphore, gold_item, prediction_item, subsection_meta, summary_length_tolerance, model=model
                )
            )
        elif question_type == 'C':
            batch_tasks.append(
                _evaluate_one_calculation_item(semaphore, gold_item, prediction_item, subsection_meta, model=model)
            )
        else:
            raise ValueError(f'Invalid question type: {question_type}')

    evaluated_mark_details = await asyncio.gather(*batch_tasks)
    mark_details.extend(evaluated_mark_details)

    return mark_details


async def evaluate_numeric_question(
    semaphore: asyncio.Semaphore, task_dict: dict, model: str = 'gpt-4.1'
) -> list:
    return await evaluate_question_by_item('C', semaphore, task_dict, model=model)


async def evaluate_abstraction_question(
    semaphore: asyncio.Semaphore, task_dict: dict, summary_length_tolerance: float, model: str = 'gpt-4.1'
) -> list:
    return await evaluate_question_by_item(
        'A', semaphore, task_dict, summary_length_tolerance=summary_length_tolerance, model=model
    )


async def evaluate_interpretation_question(
    semaphore: asyncio.Semaphore, task_dict: dict, model: str = 'gpt-4.1'
) -> list:
    return await evaluate_question_by_item('I', semaphore, task_dict, model=model)


async def evaluate_top_window_with_date_question(
    semaphore: asyncio.Semaphore, task_dict: dict, summary_length_tolerance: float, model: str = 'gpt-4.1'
) -> list:
    ori_gold_items = task_dict['gold']['items']
    ori_prediction_items = task_dict['prediction'].get('items') or []
    subsection_meta = task_dict['meta']

    mark_details = []

    mark_tasks = []

    ori_gold_items_by_year = pydash.group_by(ori_gold_items, ['year'])
    ori_prediction_items_by_year = pydash.group_by(ori_prediction_items, ['year'])
    for year, same_year_gold_items in ori_gold_items_by_year.items():
        same_year_prediction_items = ori_prediction_items_by_year.get(year) or []
        gold_item_by_name = pydash.key_by(same_year_gold_items, ['name'])
        prediction_item_by_name = pydash.key_by(same_year_prediction_items, ['name'])
        for window_type in ['Positive', 'Negative']:
            gold_window_objs = []
            prediction_window_objs = []
            for rank in range(1, 4):
                date_key = f'Top {rank} {window_type} Window Date'
                summary_key  = f'Top {rank} {window_type} Window Summary'

                gold_date_item = gold_item_by_name[date_key]
                gold_summary_item = gold_item_by_name[summary_key]
                prediction_date_item = prediction_item_by_name.get(date_key) or {}
                prediction_summary_item = prediction_item_by_name.get(summary_key) or {}

                gold_date_string = pydash.get(gold_item_by_name, [date_key, 'value']) or ''
                if is_value_missing(gold_date_string):
                    # not sure which prediction item for pairing
                    fake_prediction_date_item = {**prediction_date_item, 'name': date_key, 'value': 'NAN'}
                    fake_prediction_summary_item = prediction_summary_item.copy()
                    fake_prediction_summary_item['value'] = 'NAN'
                    mark_details.append(
                        create_full_mark_detail(gold_date_item, fake_prediction_date_item, subsection_meta)
                    )
                    mark_details.append(
                        create_full_mark_detail(gold_summary_item, fake_prediction_summary_item, subsection_meta)
                    )
                    continue

                date_obj = dateparser.parse(gold_date_string)
                assert date_obj, f'Invalid gold date format: {gold_date_string}'
                gold_window_obj = {
                    'key': date_obj,
                    'date': gold_item_by_name[date_key],
                    'summary': gold_item_by_name[summary_key],
                }
                date_string = pydash.get(prediction_item_by_name, [date_key, 'value']) or ''
                date_obj = parse_date(date_string)
                if date_obj is None:
                    logger.warning(f'Invalid prediction date format: {date_string}')
                prediction_window_obj = {
                    'key': date_obj,
                    'date': prediction_date_item,
                    'summary': prediction_summary_item,
                }
                gold_window_objs.append(gold_window_obj)
                prediction_window_objs.append(prediction_window_obj)

            gold_values = [wo['key'] for wo in gold_window_objs]
            prediction_values = [wo['key'] for wo in prediction_window_objs]

            gold2pred = find_best_matches(gold_values, prediction_values, similarity_func=are_dates_near)

            for idx, gold_window_obj in enumerate(gold_window_objs):
                gold_date_item = gold_window_obj['date']
                gold_summary_item = gold_window_obj['summary']

                if idx not in gold2pred:
                    mark_details.append(create_zero_mark_detail(gold_date_item, subsection_meta))
                    mark_details.append(create_zero_mark_detail(gold_summary_item, subsection_meta))
                else:
                    prediction_window_obj = prediction_window_objs[gold2pred[idx]]
                    prediction_date_item = prediction_window_obj['date']
                    prediction_summary_item = prediction_window_obj['summary']

                    mark_details.append(create_full_mark_detail(gold_date_item, prediction_date_item, subsection_meta))

                    mark_tasks.append(
                        _evaluate_one_abstraction_item(
                            semaphore,
                            gold_summary_item,
                            prediction_summary_item,
                            subsection_meta,
                            summary_length_tolerance,
                            model=model
                        )
                    )

    mark_details.extend(await asyncio.gather(*mark_tasks))

    return mark_details


async def evaluate_top_windown_with_car_question(
    semaphore: asyncio.Semaphore, task_dict: dict, summary_length_tolerance: float, model: str = 'gpt-4.1'
) -> list:
    ori_gold_items = task_dict['gold']['items']
    ori_prediction_items = task_dict['prediction'].get('items') or []
    subsection_meta = task_dict['meta']

    mark_tasks = []

    ori_gold_items_by_year = pydash.group_by(ori_gold_items, ['year'])
    ori_prediction_items_by_year = pydash.group_by(ori_prediction_items, ['year'])
    for year, same_year_gold_items in ori_gold_items_by_year.items():
        same_year_prediction_items = ori_prediction_items_by_year.get(year) or []
        gold_item_by_name = pydash.key_by(same_year_gold_items, ['name'])
        prediction_item_by_name = pydash.key_by(same_year_prediction_items, ['name'])
        for window_type in ['Positive', 'Negative']:
            for rank in range(1, 4):
                date_key = f'Top {rank} {window_type} Window Date'
                car_key = f'Top {rank} {window_type} Window CAR'
                summary_key = f'Top {rank} {window_type} Window Summary'

                gold_date_item = gold_item_by_name[date_key]
                gold_car_item = gold_item_by_name[car_key]
                gold_summary_item = gold_item_by_name[summary_key]
                prediction_date_item = prediction_item_by_name.get(date_key) or {}
                prediction_car_item = prediction_item_by_name.get(car_key) or {}
                prediction_summary_item = prediction_item_by_name.get(summary_key) or {}

                mark_tasks.append(
                    _evaluate_one_recognition_item(
                        semaphore, gold_date_item, prediction_date_item, subsection_meta, model=model
                    )
                )
                mark_tasks.append(
                    _evaluate_one_calculation_item(
                        semaphore, gold_car_item, prediction_car_item, subsection_meta, model=model
                    )
                )
                mark_tasks.append(
                    _evaluate_one_abstraction_item(
                        semaphore,
                        gold_summary_item,
                        prediction_summary_item,
                        subsection_meta,
                        summary_length_tolerance,
                        model=model
                    )
                )
    mark_details = await asyncio.gather(*mark_tasks)
    return mark_details

async def evaluate_one_subsection(
    semaphore: asyncio.Semaphore, task_dict: dict, summary_length_tolerance: float, model: str = 'gpt-4.1'
):
    subsection_no = task_dict['gold']['no']
    subsection_type = task_dict['meta']['type']
    logger.info(f'Evaluating sub_section {subsection_no}')

    subsection_type = SType[subsection_type]

    if subsection_type == SType.I:
        sub_section_mark_details = await evaluate_interpretation_question(semaphore, task_dict, model=model)
    elif subsection_type == SType.I2:
        sub_section_mark_details = await evaluate_top_window_with_date_question(
            semaphore, task_dict, summary_length_tolerance=summary_length_tolerance, model=model
        )
    elif subsection_type == SType.I3:
        sub_section_mark_details = await evaluate_top_windown_with_car_question(
            semaphore, task_dict, summary_length_tolerance=summary_length_tolerance, model=model
        )
    elif subsection_type == SType.A:
        sub_section_mark_details = await evaluate_abstraction_question(
            semaphore, task_dict, summary_length_tolerance=summary_length_tolerance, model=model
        )
    elif subsection_type in [SType.C, SType.C2, SType.C3, SType.R1, SType.R3]:
        sub_section_mark_details = await evaluate_numeric_question(semaphore, task_dict, model=model)
    elif subsection_type in [SType.R2]:
        sub_section_mark_details = await evaluate_recognition_question(semaphore, task_dict, model=model)
    elif subsection_type in [SType.R4]:
        sub_section_mark_details = await evaluate_recognition_obj_question(semaphore, task_dict, model=model)
    else:
        raise ValueError(f'Invalid question type: {subsection_type}')

    return sub_section_mark_details


async def evaluate_one_report(
    semaphore: asyncio.Semaphore,
    company: str,
    location: str,
    subsection_cfg: dict,
    ground_truth_path: Union[str, pathlib.Path],
    prediction_path: Union[str, pathlib.Path, None],
    save_folder: Union[str, pathlib.Path],
    summary_length_tolerance: float,
    model: str = 'gpt-4.1',
    overwrite: bool = False,
) -> pd.DataFrame:
    save_folder = pathlib.Path(save_folder)
    save_folder = save_folder / location
    save_folder.mkdir(parents=True, exist_ok=True)
    case_name = company

    csv_path = save_folder / f'{case_name}.csv'
    if csv_path.exists() and not overwrite:
        logger.info(f'Skip evaluation for {case_name} because the csv file already exists.')
        df_mark = pd.read_csv(csv_path)
    else:
        logger.info(f'Evaluating {case_name}...')
        trace_folder = save_folder / 'debug' / case_name
        trace_folder_cv.set(trace_folder)

        ground_truth_input = json.loads(pathlib.Path(ground_truth_path).read_text())
        prediction_input = json.loads(pathlib.Path(prediction_path).read_text()) if prediction_path else {}

        prediction_input_by_subsection = pydash.key_by(prediction_input.get('converted', []), 'no')

        batch_tasks = []
        for gold_dict in ground_truth_input['converted']:
            subsection_no = gold_dict['no']
            prediction_dict = prediction_input_by_subsection.get(subsection_no) or {}
            subsection_meta = subsection_cfg[subsection_no]
            task_dict = {'gold': gold_dict, 'prediction': prediction_dict, 'meta': subsection_meta}
            batch_tasks.append(
                evaluate_one_subsection(semaphore, task_dict, summary_length_tolerance, model=model)
            )
        mark_details = [
            md for subsection_mark_details in await asyncio.gather(*batch_tasks) for md in subsection_mark_details
        ]
        df_mark = pd.DataFrame(mark_details)
        df_mark.insert(0, 'location', location)
        df_mark.insert(0, 'company', company)
        df_mark.to_csv(csv_path, index=False)

    df_mark = add_weighted_mark(df_mark, subsection_cfg) # compute weighted mark on the fly
    logger.info(f'Evaluation for {case_name} completed.')
    return df_mark


def add_weighted_mark(df_company: pd.DataFrame, subsection_cfg: dict) -> pd.DataFrame:
    am_pos = df_company.columns.get_loc('adjusted_mark')
    df_company.insert(
        am_pos + 1,
        'weighted_mark',
        df_company.apply(
            lambda x: round(
                x['adjusted_mark'] / 100 * get_item_weight(subsection_cfg, x['no'], x['field'], x['category']),
                2
            ),
            axis=1),
    )

    return df_company


def get_markets_with_order(track: str) -> List[str]:
    markets = copy.copy(MARKETS)
    if track in ['findocresearch', 'findeepresearch']:
        sg_idx = markets.index('Singapore')
        au_idx = markets.index('Australia')
        markets[sg_idx] = 'Australia'
        markets[au_idx] = 'Singapore'

    return markets


def print_mark_as_csv(mark_dict: dict, prediction_name: str, track: str):
    if prediction_name:
        prediction_name = f'[{prediction_name}]'

    markets = get_markets_with_order(track)

    print(f'=== {prediction_name}Overall ===')
    headers = ['overall']
    values = [mark_dict.get('overall', '')]
    print(','.join(headers))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Markets ===')
    values = [mark_dict.get(m, '') for m in markets]
    print(','.join(markets))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Sections ===')
    sections = [k for k in mark_dict if re.search(r'^S\d$', k)]
    values = [mark_dict.get(s, '') for s in sections]
    print(','.join(sections))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Levels ===')
    levels =  [k for k in mark_dict if re.search(r'^level\d$', k)]
    values = [mark_dict.get(l, '') for l in levels]
    print(','.join(levels))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print(f'=== {prediction_name}Overall(Normalized) ===')
    headers = ['overall']
    values = [mark_dict.get('overall_normalized', '')]
    print(','.join(headers))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Markets(Normalized) ===')
    values = [mark_dict.get(f'{m}_normalized', '') for m in markets]
    print(','.join(markets))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Sections(Normalized) ===')
    sections = [k for k in mark_dict if re.search(r'^S\d$', k)]
    values = [mark_dict.get(f'{s}_normalized', '') for s in sections]
    print(','.join(sections))
    print(','.join(str(v).split('/')[0] for v in values))
    print()

    print('=== Levels(Normalized) ===')
    levels =  [k for k in mark_dict if re.search(r'^level\d$', k)]
    values = [mark_dict.get(f'{l}_normalized', '') for l in levels]
    print(','.join(levels))
    print(','.join(str(v).split('/')[0] for v in values))
    print()


def save_mark_as_xlsx(
    df_mark_detail: pd.DataFrame,
    subsection_cfg: dict,
    subsection_total_score: int,
    output_path: Union[str, pathlib.Path],
    track: str,
) -> dict:
    mark_dict = {}

    output_path = pathlib.Path(output_path)
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    normalized_writer = pd.ExcelWriter(output_path.with_stem(output_path.stem + '_normalized'), engine='xlsxwriter')

    # Overall
    df_total_mark = (
        df_mark_detail.groupby(['company', 'location'])['weighted_mark'].sum().reset_index(name='total_mark')
    )
    company_count = df_total_mark.shape[0]
    overall_mark = df_total_mark['total_mark'].sum() / company_count
    df_overall = pd.DataFrame([round(overall_mark, 2)], columns=['overall'])
    df_overall.to_excel(writer, sheet_name='Overall', index=False)
    df_overall_normalized = pd.DataFrame([round(overall_mark / subsection_total_score * 100, 1)], columns=['overall'])
    df_overall_normalized.to_excel(normalized_writer, sheet_name='Overall', index=False)
    mark_dict['overall'] = f'{overall_mark:.2f}/{subsection_total_score:.2f}'
    mark_dict['overall_normalized'] = f'{overall_mark / subsection_total_score * 100:.1f}/{100:.1f}'

    # Location
    location_marks = []
    location_normalized_marks = []
    markets = get_markets_with_order(track)
    for location in markets:
        df_location = df_total_mark[df_total_mark['location'] == location]
        if df_location.shape[0] == 0:
            location_mark = 0
        else:
            location_mark = df_location['total_mark'].sum() / df_location.shape[0]
        location_marks.append(round(location_mark, 2))
        location_normalized_marks.append(round(location_mark / subsection_total_score * 100, 1))
        mark_dict[location] = f'{location_mark:.2f}/{subsection_total_score:.2f}'
        mark_dict[f'{location}_normalized'] = f'{location_mark / subsection_total_score * 100:.1f}/{100:.1f}'
    df_location = pd.DataFrame([location_marks], columns=markets)
    df_location.to_excel(writer, sheet_name='Location Level', index=False)
    df_location_normalized = pd.DataFrame([location_normalized_marks], columns=markets)
    df_location_normalized.to_excel(normalized_writer, sheet_name='Location Level', index=False)

    # Section
    section_info = {
        subsection_meta['section_no']: subsection_meta['section_weight'] for subsection_meta in subsection_cfg.values()
    }
    section_mark_dict = {}
    section_normalized_mark_dict = {}
    for section_no, df_section in df_mark_detail.groupby('section_no'):
        section_mark = df_section['weighted_mark'].sum() / company_count
        section_full_mark = section_info[section_no]
        section_mark_dict[section_no] = round(section_mark, 2)
        section_normalized_mark_dict[section_no] = round(section_mark / section_full_mark * 100, 1)
        mark_dict[section_no] = f'{section_mark:.2f}/{section_full_mark:.2f}'
        mark_dict[f'{section_no}_normalized'] = f'{section_mark / section_full_mark * 100:.1f}/{100:.1f}'
    df_section = pd.DataFrame([section_mark_dict])
    df_section.to_excel(writer, sheet_name='Section Level', index=False)
    df_section_normalized = pd.DataFrame([section_normalized_mark_dict])
    df_section_normalized.to_excel(normalized_writer, sheet_name='Section Level', index=False)

    # Level
    level_info = pydash.group_by(subsection_cfg, lambda n: get_question_level(subsection_cfg[n]['type']))
    level_mark_dict = {}
    level_normalized_mark_dict = {}
    level_series = df_mark_detail['type'].map(get_question_level)
    for question_level, df_level in df_mark_detail.groupby(level_series):
        level_mark = df_level['weighted_mark'].sum() / company_count
        level_full_mark = sum(subsection_cfg[no]['weight'] for no in level_info[question_level])
        level_mark_dict[question_level] = round(level_mark, 2)
        level_normalized_mark_dict[question_level] = round(level_mark / level_full_mark * 100, 1)
        mark_dict[question_level] = f'{level_mark:.2f}/{level_full_mark:.2f}'
        mark_dict[f'{question_level}_normalized'] = f'{level_mark / level_full_mark * 100:.1f}/{100:.1f}'

    df_level = pd.DataFrame([level_mark_dict])
    df_level.to_excel(writer, sheet_name='Level', index=False)
    df_level_normalized = pd.DataFrame([level_normalized_mark_dict])
    df_level_normalized.to_excel(normalized_writer, sheet_name='Level', index=False)

    # Details
    df_mark_detail.to_excel(writer, sheet_name='Details', index=False)
    df_mark_detail.to_excel(normalized_writer, sheet_name='Details', index=False)

    writer.close()
    normalized_writer.close()

    return mark_dict


async def evaluate(
    prediction_folder: Union[str, pathlib.Path],
    save_folder: Union[str, pathlib.Path],
    model: str = 'gpt-4.1',
    track: str = 'findeepresearch',
    prediction_name: str = '',
    overwrite: bool = False,
):
    logger.info(f'Begin to evaluate for {prediction_folder}')

    track_subsection_cfg, track_subsection_total_score = get_subsection_info(track)
    ground_truth_folder = get_ground_truth_folder(track)
    summary_length_tolerance = get_summary_length_tolerance_for_track(track)

    prediction_folder = pathlib.Path(prediction_folder)
    save_folder = pathlib.Path(save_folder)

    ground_truth_files = list(ground_truth_folder.rglob('*.json'))
    prediction_files = list(prediction_folder.rglob('*.json'))

    prediction_by_company = pydash.key_by(prediction_files, lambda p: p.stem)

    semaphore = asyncio.Semaphore(LLM_CONCURRENCY)

    batch_tasks = []
    missing_companies = []
    for ground_truth_file in ground_truth_files:
        company = get_company_from_report_name(ground_truth_file.stem)
        location = get_location_from_company_name(company, track)
        prediction_file = prediction_by_company.get(company)
        if not prediction_file:
            logger.warning(f'🚨Missing prediction file for {company}..')
            missing_companies.append(company)

        batch_tasks.append(
            evaluate_one_report(
                semaphore,
                company,
                location,
                track_subsection_cfg,
                ground_truth_file,
                prediction_file,
                save_folder,
                summary_length_tolerance,
                model=model,
                overwrite=overwrite,
            )
        )
    df_mark_detail_lst = await asyncio.gather(*batch_tasks)
    df_mark_detail = pd.concat(df_mark_detail_lst)

    content_mark_dict = save_mark_as_xlsx(
        df_mark_detail,
        track_subsection_cfg,
        track_subsection_total_score,
        save_folder / f'{prediction_name}_evaluation.xlsx',
        track
    )

    print_mark_as_csv(content_mark_dict, prediction_name, track)


def main():
    setup_logger()
    parser = argparse.ArgumentParser(description='Evaluation Tool for FindocResearch or FinDeepResearch')
    parser.add_argument('--prediction_folder', type=str, required=True, help='Path to prediction folder')
    parser.add_argument('--save_folder', type=str, required=True, help='Path to save evaluation results')
    parser.add_argument('--track', type=str, required=True, help='findocresearch or findeepresearch')
    parser.add_argument('--model', type=str, default='gpt-4.1', help='Model name used for evaluation')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing results')

    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(
        evaluate(
            prediction_folder=args.prediction_folder,
            save_folder=args.save_folder,
            model=args.model,
            track=args.track,
            prediction_name='demo',
            overwrite=args.overwrite
        )
    )


if __name__ == '__main__':
    main()
