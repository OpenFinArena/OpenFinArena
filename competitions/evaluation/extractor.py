import argparse
import asyncio
import copy
import json
import logging
import pathlib
import random
import re
from typing import List, Optional, Tuple, Union

import json5
import pandas as pd
import pydash
import regex
from deepeval.metrics.summarization.schema import Questions
from tabulate import tabulate

from constants import (
    COMPANY_CFG_FINDEEPRESEARCH,
    COMPANY_CFG_FINDOCRESEARCH,
    FY,
    GOLD_FOLDER_FINDOCRESEARCH,
    NEXT_FY_COMPANY_LIST,
    GOLD_FOLDER_FINDEEPRESEARCH,
    LLM_CONCURRENCY,
    SPLIT_REGEX_MAP,
    get_subsection_info,
)
from contexts import trace_folder_cv
from evaluation.llms.llm_util import chat_with_llm
from evaluation.other_util import compose_item_trace_id, get_location_from_company_name, is_value_missing, setup_logger
from evaluation.prompts.criteria_prompt import CRITERIA_PROMPT, S_Q_PROMPT, S_Q_PROMPT_NEWS
from evaluation.prompts.extractor_prompt import (
    SPLIT_PROMPT,
    compose_fields,
    compose_json_structure,
    compose_report_desp,
)
from evaluation.prompts.prompt_util import compose_question
from evaluation.section_util import SType, get_prompt_template_by_type, get_subsection_structure_regex_lst

logger = logging.getLogger(__name__)


def find_section_no(input_string: str) -> str:
    m = re.search(r'#[^#\d]+(\d)\D+', input_string)
    if m:
        return 'S' + m.group(1)
    raise ValueError(f'Cannot find section no from "{input_string}"')


def parse_json_lst(pred_str: str) -> list:
    # First match content enclosed in a JSON comment block
    json_comment_pattern = regex.compile(r'```json\s*({.*?})\s*```', regex.DOTALL)
    json_comment_match = json_comment_pattern.search(pred_str)
    json_string_candidates = []
    if json_comment_match:
        try:
            json_string = json_comment_match.group(1)
            json_string_candidates = [json_string]
        except json.JSONDecodeError:
            logger.debug(f'Failed to decode JSON from comment block: {json_comment_match.group(1)}')

    # If no JSON comment block is found, continue searching for JSON strings
    if not json_string_candidates:
        pattern = regex.compile(r'\{(?:(?R)|[^{}]*)++\}|\[(?:(?R)|[^[{}\]]*)++\]')

        json_string_candidates = pattern.findall(pred_str)

    json_dict = None
    if json_string_candidates:
        for json_string in json_string_candidates:
            try:
                tmp_dict = json5.loads(json_string)
                is_valid = isinstance(tmp_dict, list) and (
                    (len(tmp_dict) > 0 and isinstance(tmp_dict[0], dict)) or (not tmp_dict)
                )
                if is_valid:
                    json_dict = tmp_dict
                    break
            except:
                pass

    if json_dict is None:
        raise ValueError(f'Cannot find valid JSON from response: {pred_str}')

    return json_dict


def parse_header(header: str):
    return header.upper().strip().replace('*', '')


def remove_citations(md_string: str, company_name: str):
    removed_items = []

    def replacer(match):
        removed_items.append(match.group(0))
        return ''

    new_md_string = re.sub(r'\(\[[^\]]+\]\([^)]+\)\)', replacer, md_string)
    if not removed_items:
        new_md_string = re.sub(r'#+\s*\**(?:Works cited|引用的著作).+', replacer, md_string, flags=re.I | re.DOTALL)
    if not removed_items:
        new_md_string = re.sub(r'^\*\*Sources:\*\*.+', replacer, md_string, flags=re.MULTILINE | re.DOTALL)

    if removed_items:
        logger.info(f'Removed citations for {company_name}:')
        for item in removed_items:
            logger.info(f'  -{item}')
    else:
        logger.info(f'No citations found for {company_name}.')

    return new_md_string


def _subsection_content_format_score(
    subsection_no: str,
    subsection_content: str,
    company_name: str,
    subsection_cfg: dict,
) -> float:
    expected_fields = subsection_cfg[subsection_no]['fields']
    subsection_type = subsection_cfg[subsection_no]['type']

    # 1. Check if markdown table exists in content
    table_pattern = r'\|.*\|'
    if not re.search(table_pattern, subsection_content):
        return 0.0

    # Extract all markdown tables from content
    lines = subsection_content.split('\n')
    table_lines = [line.replace('**', '') for line in lines if '|' in line and not re.search(r'^[|\-: ]+$', line)]

    if not table_lines:
        return 0.0

    # 2. Check if important markdown row headers and columns exist
    table_content = '\n'.join(table_lines)

    column_regex_lst = get_subsection_structure_regex_lst(subsection_type, company_name)

    field_tolerance_map = {
        'Diluted EPS (LFY)': 'Diluted EPS',
        'P/E Ratio (LFY)': 'P/E Ratio',
        'Income tax expense (benefit)': 'Income tax expense'
    }

    # Check field presence
    found_fields = 0
    for field in expected_fields:
        if subsection_no != 'S5.1':
            field = field_tolerance_map.get(field, field)
            if field == 'R&D Investments':
                field_regex = r'R\\?&D Investments'
            else:
                field_regex = re.escape(field)
            # tolerance
            field_regex = rf'^\s*\|\s*{field_regex}[^|]*\|'
            if re.search(field_regex, table_content, re.I | re.M):
                found_fields += 1
        else:
            if field == 'Total Income':
                field_regex = r'\|\s*Total Income[^|]*\|'
            else:
                field_regex = rf'\|\s*{re.escape(field)}\s*\|'
            if re.search(field_regex, table_lines[0], re.I):
                found_fields += 1

    # Check category presence (columns)
    found_categories = 0
    for category in column_regex_lst:
        # For categories like "2024", "2023", search for them in table headers
        if re.search(category, table_lines[0].strip(), re.I):
            found_categories += 1

    # Calculate score based on field and category coverage
    field_score = found_fields / len(expected_fields)
    category_score = found_categories / len(column_regex_lst)

    final_score = round((field_score + category_score) / 2, 2)

    return final_score


def apply_penalty_on_format_score(company: str, format_score: dict, penalty: dict) -> dict:
    subsection_table_details = format_score['subsection_tables']
    if penalty:
        for subsection_no, penalty in penalty.items():
            subsection_table_details[subsection_no] = max(0, subsection_table_details[subsection_no] - penalty)
            logger.info(f'Penalty applied on {company} {subsection_no}')

    format_score['overall'] = (
        sum(format_score['section_headers'].values())
        + sum(format_score['subsection_headers'].values())
        + sum(subsection_table_details.values())
    )
    return format_score


def calculate_format_score(content_lst: list, company: str, subsection_cfg: dict) -> dict:
    section_header_details = {}
    subsection_header_details = {}
    subsection_table_details = {}
    tracked_section_header = ''

    content_by_subsection_no = pydash.key_by(content_lst, 'subsection_no')
    for subsection_no, subsection_meta in subsection_cfg.items():
        content_dict = content_by_subsection_no.get(subsection_no, {})

        current_section_header = subsection_meta['section_name']
        if current_section_header != tracked_section_header:
            tracked_section_header = current_section_header
            predicted_section_header = parse_header(content_dict.get('section_header', ''))
            gold_section_header = parse_header(current_section_header)
            section_no = re.search(r'\d', subsection_meta['section_no']).group()
            section_score_regex = rf'(?:Section|S)\s*{section_no}.*{re.escape(gold_section_header)}$'
            if re.search(section_score_regex, predicted_section_header, re.I):
                section_header_details[section_no] = 1.0
            else:
                section_header_details[section_no] = 0.0

        predicted_subsection_header = parse_header(content_dict.get('subsection_header', ''))
        gold_subsection_header = parse_header(subsection_meta['name'])
        subsection_score_regex = rf'{re.escape(subsection_meta["no"])}.*{re.escape(gold_subsection_header)}$'
        if re.search(subsection_score_regex, predicted_subsection_header, re.I):
            subsection_header_details[subsection_no] = 1.0
        else:
            subsection_header_details[subsection_no] = 0.0
        subsection_table_details[subsection_no] = _subsection_content_format_score(
            subsection_no, content_dict.get('subsection_content', ''), company, subsection_cfg
        )

    format_score = {
        'overall': (
            sum(section_header_details.values())
            + sum(subsection_header_details.values())
            + sum(subsection_table_details.values())
        ),
        'section_headers': section_header_details,
        'subsection_headers': subsection_header_details,
        'subsection_tables': subsection_table_details,
    }

    return format_score


def split_md_to_sections_by_main_section(
    md_string: str,
    company_name: str,
    subsection_cfg: dict,
    title_style: str = 'hashtag'  # asterisk
) -> Tuple[list, dict]:
    section_infos = pydash.group_by(subsection_cfg, lambda n: subsection_cfg[n]['section_no'])

    expected_sections = len(section_infos)
    expected_subsections = len(subsection_cfg)

    regex_map = SPLIT_REGEX_MAP

    result_by_subsection_no = {}
    penalty_by_subsection_no = {}
    main_sections = re.split(regex_map[title_style]['section_split'], md_string)
    main_sections = [ms.strip() for ms in main_sections if ms.strip()]
    if len(main_sections) == expected_sections + 1:
        if (
            re.search(r'Research Report:', main_sections[0], re.I)
            or re.search(SPLIT_REGEX_MAP[title_style]['section_header'], main_sections[0].re.I) is None
        ):
            logger.warning(f'{main_sections[0]} is dropped for {company_name}')
            main_sections = main_sections[1:]
    error_msg = f'Incorrect number of main sections: {len(main_sections)} for {company_name}'
    assert len(main_sections) == expected_sections, error_msg
    for main_section in main_sections:
        section_header_m = re.search(regex_map[title_style]['section_header'], main_section)
        section_header = section_header_m.group(1).strip()
        section_no = re.search(r'\d', section_header).group()
        section_no = f'S{section_no}'

        subsection_title_style = title_style
        subsections = re.split(regex_map[title_style]['subsection_split'], main_section)
        # in case subsection style is different from section style
        alter_style = [s for s in SPLIT_REGEX_MAP if s != title_style][0]
        alter_subsections = re.split(regex_map[alter_style]['subsection_split'], main_section)
        if len(alter_subsections) > len(subsections):
            subsections = alter_subsections
            subsection_title_style = alter_style
            logger.warning(f'Style mismatch detected for subsections inside {section_no}')

        if len(subsections) - 1 < len(section_infos[section_no]):
            # handle missing subsections
            # section header might be loss but it does not affect format score judgement
            table_necks = re.findall(r'^[|\-:\s]+$', main_section, re.M)
            table_necks = [n for n in table_necks if '|' in n and '-' in n]
            if len(table_necks) == len(section_infos[section_no]):
                subsection_no_lst = [f'{section_no}.{idx}' for idx in range(1, len(table_necks) + 1)]
                updated_subsections = []
                for idx, one_subsection in enumerate(subsections):
                    table_necks = re.findall(r'^[|\-:\s]+$', one_subsection, re.M)
                    table_necks = [n for n in table_necks if '|' in n and '-' in n]
                    if not table_necks:
                        logger.warning(f'{one_subsection} is dropped for {company_name}')
                        continue

                    # ensure there is no subsection headers or only header in 1st subsection
                    sub_section_lines = one_subsection.split('\n')
                    revised_subsections = _group_lines_into_subsections(
                        sub_section_lines, subsection_no_lst, title_style, subsection_header_exists=idx != 0
                    )
                    updated_subsections.extend(revised_subsections)
                    subsection_no_lst = subsection_no_lst[len(revised_subsections):]
                if len(updated_subsections) >= len(subsections):
                    subsections = updated_subsections
        else:
            subsections = subsections[1:]
            m = re.search(r'\n## Conclusion$', subsections[-1], re.M)
            if m:
                logger.warning(f'{subsections[-1][m.start():]} is dropped')
                subsections[-1] = subsections[-1][:m.start()]

        for subsection in subsections:
            if re.search(r'(?:^#+\s*(?:Conclusion|Summary|Final Conclusion))|(?:^\*+\s*Note)', subsection.strip()):
                logger.warning(f'{subsection} is dropped')
                continue
            subsection_header_m = re.search(regex_map[subsection_title_style]['subsection_header'], subsection.strip())
            subsection_header = subsection_header_m.group(1).strip()
            subsection_no = re.search(r'\d\.\d', subsection_header).group()
            subsection_no = 'S' + subsection_no
            if subsection_no in result_by_subsection_no:
                penalty_by_subsection_no[subsection_no] = 1
                logger.warning(f'Duplicate subsection found: {subsection_no} of {company_name}')
            result_by_subsection_no[subsection_no] = {
                'section_header': section_header,
                'subsection_header': subsection_header,
                'subsection_no': subsection_no,
                'subsection_content': subsection,
            }

    result = list(result_by_subsection_no.values())
    assert len(result) == expected_subsections, f'Incorrect number of subsections: {len(result)} for {company_name}'
    return result, penalty_by_subsection_no


def split_md_to_sections_iteratively(
    md_string: str, company_name: str, expected_subsections: int = 18
) -> Tuple[list, dict]:
    result_by_subsection_no = {}
    penalty_by_subsection_no = {}

    lines = md_string.split('\n')
    subsection_lines = []
    tracked_section_no = ''
    tracked_section_header = ''
    tracked_subsection_no = ''
    tracked_subsection_header = ''

    for ln in lines:
        ln = ln.strip()
        section_no_m = re.search(r'^#+[^#\d]+(\d)\s*:?([^#\d]+)$', ln) or re.search(
            r'^Section +(\d)\s*:?([^#\d]+)$', ln
        )
        subsection_no_m = re.search(r'^#*[^#|\d]+(\d\.\d)\s*:?([^#|\d]*)$', ln)

        if section_no_m:
            section_no = section_no_m.group(1)
            section_header = section_no_m.group(2).strip()
            section_header = f'Section {section_no}: {section_header}'
            section_no = f'S{section_no}'
            if subsection_lines:
                subsection_content = '\n'.join(subsection_lines)
                if tracked_subsection_no:
                    if tracked_subsection_no in result_by_subsection_no:
                        penalty_by_subsection_no[tracked_subsection_no] = 1
                        logger.warning(f'Duplicate subsection found: {tracked_subsection_no} of {company_name}')
                    result_by_subsection_no[tracked_subsection_no] = {
                        'section_header': tracked_section_header,
                        'subsection_header': tracked_subsection_header,
                        'subsection_no': tracked_subsection_no,
                        'subsection_content': subsection_content,
                    }
                elif tracked_section_no and all(
                    not rsn.startswith(tracked_section_no) for rsn in result_by_subsection_no
                ):
                    # filling missing 1st subsection
                    result_by_subsection_no[tracked_subsection_no] = {
                        'section_header': tracked_section_header,
                        'subsection_header': '',
                        'subsection_no': f'{tracked_section_no}.1',
                        'subsection_content': subsection_content,
                    }
                elif len(subsection_content.strip()):
                    logger.warning(f'{subsection_content} is dropped')
            subsection_lines = []
            tracked_section_no = section_no
            tracked_section_header = section_header
            tracked_subsection_no = ''
            tracked_subsection_header = ''
        elif subsection_no_m:
            subsection_no = subsection_no_m.group(1)
            subsection_no = f'S{subsection_no}'
            subsection_header = subsection_no_m.group(2).strip()
            subsection_header = f'{subsection_no}: {subsection_header}'

            first_subsection = subsection_no == f'{tracked_section_no}.1'

            if subsection_lines and not first_subsection:
                subsection_content = '\n'.join(subsection_lines)
                if tracked_subsection_no:
                    if tracked_subsection_no in result_by_subsection_no:
                        penalty_by_subsection_no[tracked_subsection_no] = 1
                        logger.warning(f'Duplicate subsection found: {tracked_subsection_no} of {company_name}')
                    result_by_subsection_no[tracked_subsection_no] = {
                        'section_header': tracked_section_header,
                        'subsection_header': tracked_subsection_header,
                        'subsection_no': tracked_subsection_no,
                        'subsection_content': subsection_content,
                    }
                elif len(subsection_content.strip()):
                    logger.warning(f'{subsection_content} is dropped')
                subsection_lines = [ln]
            elif subsection_lines and first_subsection:
                subsection_lines = [ln]
            else:
                subsection_lines.append(ln)

            tracked_subsection_no = subsection_no
            tracked_subsection_header = subsection_header
        else:
            subsection_lines.append(ln)

    if subsection_lines:
        subsection_content = '\n'.join(subsection_lines)
        if tracked_subsection_no:
            if tracked_subsection_no in result_by_subsection_no:
                penalty_by_subsection_no[tracked_subsection_no] = 1
                logger.warning(f'Duplicate subsection found: {tracked_subsection_no} of {company_name}')
            result_by_subsection_no[tracked_subsection_no] = {
                'section_header': tracked_section_header,
                'subsection_header': tracked_subsection_header,
                'subsection_no': tracked_subsection_no,
                'subsection_content': subsection_content,
            }
        elif len(subsection_content.strip()):
            logger.warning(f'{subsection_content} is dropped')

    result = list(result_by_subsection_no.values())
    assert len(result) == expected_subsections, f'Incorrect number of subsections: {len(result)} for {company_name}'
    return result, penalty_by_subsection_no


async def split_md_to_sections_llm(
    semaphore: asyncio.Semaphore,
    md_string: str,
    company_name: str,
    subsection_cfg: dict,
    model: str = 'gpt-4.1'
):
    expected_subsections = len(subsection_cfg)

    prompt = SPLIT_PROMPT.format(
        input_markdown=md_string.replace('"', r'\"'),
        subsections=compose_report_desp(subsection_cfg)
    )
    async with semaphore:
        subsection_list_string = await chat_with_llm(prompt, model=model, trace_id='split')
    subsections = parse_json_lst(subsection_list_string)

    result_by_subsection_no = {}
    penalty_by_subsection_no = {}
    for subsection in subsections:
        if subsection['subsection_no'] not in result_by_subsection_no:
            result_by_subsection_no[subsection['subsection_no']] = subsection
        else:
            penalty_by_subsection_no[subsection['subsection_no']] = 1
            ori_subsection = result_by_subsection_no[subsection['subsection_no']] = subsection
            if len(ori_subsection) < len(subsection):
                logger.warning(f'{ori_subsection} is dropped for {company_name}')
                result_by_subsection_no[subsection['subsection_no']] = subsection

    result = list(result_by_subsection_no.values())
    if len(result) != expected_subsections:
        logger.warning(f'Incorrect number of subsections: {len(result)} for {company_name}')
    return result, penalty_by_subsection_no


def _group_lines_into_subsections(
    lines: list, subsection_no_lst: list, title_style: str, subsection_header_exists: bool = False
) -> list:
    """
    Works only if without any subsection headers or only with the 1st subsection header
    """
    revised_subsections = []
    prev_neck = -1
    for ln_idx, ln in enumerate(lines):
        if '-' in ln and '|' in ln and re.search(r'^[|\-:\s]+$', ln):
            if prev_neck > 0:
                add_subsection_header = revised_subsections or not subsection_header_exists
                table_lines = lines[prev_neck - 1:ln_idx - 1] if add_subsection_header else lines[:ln_idx - 1]
                subsection_no = subsection_no_lst[len(revised_subsections)]
                # skip adding header for 1st found subsection with header
                if add_subsection_header:
                    header_line = f'### {subsection_no} ' if title_style == 'hashtag' else f'** {subsection_no} **'
                    table_lines = [header_line] + table_lines
                revised_subsections.append('\n'.join(table_lines))
            prev_neck = ln_idx
    if 0 < prev_neck < len(lines) - 1:
        table_lines = lines[prev_neck - 1:]
        subsection_no = subsection_no_lst[len(revised_subsections)]
        header_line = f'### {subsection_no} ' if title_style == 'hashtag' else f'** {subsection_no} **'
        table_lines = [header_line] + table_lines
        revised_subsections.append('\n'.join(table_lines))

    return revised_subsections


def insert_mocked_subsections(md_string: str, subsection_cfg: dict) -> str:
    table_necks = re.findall(r'^[|\-:\s]+$', md_string, re.M)
    table_necks = [n for n in table_necks if n.strip() and '|' in n and '-' in n]
    suspected_headers = re.findall(r'^#+', md_string)
    if len(table_necks) != len(subsection_cfg) or suspected_headers:
        return md_string

    subsection_no_lst = list(subsection_cfg.keys())
    lines = md_string.split('\n')
    revised_subsections = _group_lines_into_subsections(lines, subsection_no_lst, 'hashtag')

    if revised_subsections:
        return '\n'.join(revised_subsections)

    return md_string


def find_all_main_section_info(md_string: str) -> Tuple[list, str]:
    main_section_title_style = 'hashtag'
    main_section_headers = re.findall(r'(?:^|\n)#+[^#\d]+\d[^#\d]+\n', md_string)
    if len(main_section_headers) == 0:
        # ^#*[^#|\d]+(\d\.\d)\s*:?([^#|\d]*)$
        # (?:^|\n)#*[^#|\d]+?(\d\.\d)\s*:?([^#|\d\n]*)\n
        main_section_headers = re.findall(r'(?:^|\n)\*+[^*\d]+\d[^*\d]+\*+\s*\n', md_string)
        main_section_title_style = 'asterisk'

    return main_section_headers, main_section_title_style


def split_md_to_sections_by_rules(
    md_string: str,
    company_name: str,
    subsection_cfg: dict,
    method: str = 'auto'  # auto, top_down, bottom_up
) -> Tuple[list, dict]:
    expected_sections = len(pydash.group_by(subsection_cfg, lambda n: subsection_cfg[n]['section_no']))
    expected_subsections = len(subsection_cfg)

    main_section_headers, main_section_title_style = find_all_main_section_info(md_string)

    if method == 'top_down':
        return split_md_to_sections_by_main_section(
            md_string, company_name, subsection_cfg, title_style=main_section_title_style
        )
    elif method == 'bottom_up':
        if len(main_section_headers) == 0:
            subsection_headers = re.findall(r'(?:^|\n)#*[^#|\d]+?\d\.\d\s*:?[^#|\d\n]*\n', md_string)
            if len(subsection_headers) == 0:
                md_string = insert_mocked_subsections(md_string, subsection_cfg)
        return split_md_to_sections_iteratively(md_string, company_name, expected_subsections)
    else:
        if len(main_section_headers) == expected_sections:
            try:
                return split_md_to_sections_by_main_section(
                    md_string, company_name, subsection_cfg, title_style=main_section_title_style
                )
            except AttributeError as ae:
                return split_md_to_sections_iteratively(md_string, company_name, expected_subsections)
        else:
            if len(main_section_headers) == 0:
                subsection_headers = re.findall(r'(?:^|\n)#*[^#|\d]+?\d\.\d\s*:?[^#|\d\n]*\n', md_string)
                if len(subsection_headers) == 0:
                    md_string = insert_mocked_subsections(md_string, subsection_cfg)
            return split_md_to_sections_iteratively(md_string, company_name, expected_subsections)


async def split_md_to_sections(
    md_string: str,
    company_name: str,
    subsection_cfg: dict,
    rule_method: str = 'auto',
    llm_augmented: bool = False,
    llm_model: str = 'gpt-4.1',
    semaphore: Optional[asyncio.Semaphore] = None
) -> Tuple[list, dict]:
    try:
        return split_md_to_sections_by_rules(md_string, company_name, subsection_cfg, method=rule_method)
    except Exception as e:
        if llm_augmented:
            logger.warning(f'Failed to split md for {company_name}: {e}')
            logger.warning('Trying llm method to split md...')
            return await split_md_to_sections_llm(semaphore, md_string, company_name, subsection_cfg, model=llm_model)
        else:
            raise e


async def generate_abstraction_questions(
    semaphore: asyncio.Semaphore,
    item_dict: dict,
    sub_section_no: str,
    company_name: str,
    abstraction_question_num: int = 5,
    model: str = 'gpt-4.1',
    template=S_Q_PROMPT
) -> list:
    logger.info(f"Generating abstraction questions for {company_name}'s sub section: {sub_section_no} {item_dict['name']}")
    input_text = item_dict['value']
    if is_value_missing(input_text):
        return []

    assert (
        abstraction_question_num // 2 + 1 < abstraction_question_num
    ), 'Please specify a large enough number of abstraction questions'
    prompt = template.format(
        input_text=input_text, min_num=abstraction_question_num // 2 + 1, max_num=abstraction_question_num
    )
    async with semaphore:
        res = await chat_with_llm(
            prompt,
            model=model,
            schema=Questions,
            trace_id=compose_item_trace_id(sub_section_no, item_dict['name'], str(item_dict.get('year') or '')),
        )
    return res.questions


async def generate_interpretation_criteria(
    semaphore: asyncio.Semaphore,
    item_dict: dict,
    subsection_no: str,
    company_name: str,
    subsection_cfg: dict,
    model: str = 'gpt-4.1'
) -> str:
    logger.info(f"Generating interpretation criteria for {company_name}'s sub section: {subsection_no} {item_dict['name']}")
    subsection_obj = subsection_cfg[subsection_no]

    if is_value_missing(item_dict['value']):
        return ''

    prompt = CRITERIA_PROMPT.format(
        question=compose_question(sub_section_name=subsection_obj['name'], point_name=item_dict['name']),
        answer=item_dict['value'],
    )
    async with semaphore:
        res = await chat_with_llm(
            prompt, model=model, temperature=0.7, trace_id=compose_item_trace_id(subsection_no, item_dict['name'])
        )
    m = re.search(r'<marking>(.+)</marking>', res, flags=re.DOTALL)
    if not m:
        raise ValueError(f'Cannot find marking criteria from response: {res}')
    res = m.group(1).strip()
    return res

async def _convert_sub_section_md_to_json(
    semaphore: asyncio.Semaphore,
    subsection_no: str,
    subsection_content: str,
    subsection_table_score: float,
    company_name: str,
    subsection_cfg: dict,
    model: str = 'gpt-4.1'
) -> dict:
    logger.info(f"Extracting from {company_name}'s sub section: {subsection_no}")
    subsection_obj = copy.copy(subsection_cfg[subsection_no])
    subsection_type = subsection_obj['type']
    prompt_template = get_prompt_template_by_type(subsection_type, subsection_table_score)
    prompt = prompt_template.format(
        input_markdown=subsection_content.replace('"', r'\"'),  # quotes affects json parsing later
        fields=compose_fields(subsection_obj['fields']),
        json_structure=compose_json_structure(subsection_obj['fields']),
    )
    async with semaphore:
        item_list_string = await chat_with_llm(prompt, model=model, trace_id=subsection_no)
    item_list = parse_json_lst(item_list_string)

    result = {'no': subsection_no, 'items': item_list}

    return result


async def convert_md_to_json(
    semaphore: asyncio.Semaphore,
    file_path: Union[str, pathlib.Path],
    company_name: str,
    subsection_cfg: dict,
    batch_size: int = 15,
    model: str = 'gpt-4.1'
) -> dict:
    file_path = pathlib.Path(file_path)
    md_string = file_path.read_text()

    result = []
    md_string = remove_citations(md_string, company_name)
    sub_sections, penalty = await split_md_to_sections(
        md_string, company_name, subsection_cfg, llm_augmented=True, semaphore=semaphore, llm_model=model
    )
    format_score = calculate_format_score(sub_sections, company_name, subsection_cfg)
    for start in range(0, len(sub_sections), batch_size):
        batch_tasks = []
        for subsection_dict in sub_sections[start:start + batch_size]:
            subsection_no = subsection_dict['subsection_no']
            subsection_content = subsection_dict['subsection_content']
            subsection_table_score = format_score['subsection_tables'][subsection_no]
            batch_tasks.append(
                _convert_sub_section_md_to_json(
                    semaphore,
                    subsection_no,
                    subsection_content,
                    subsection_table_score,
                    company_name,
                    subsection_cfg,
                    model=model
                )
            )
        batch_results = await asyncio.gather(*batch_tasks)
        result.extend(batch_results)

    format_score = apply_penalty_on_format_score(company=company_name, format_score=format_score, penalty=penalty)
    return {'converted': result, 'format_score': format_score}


async def _supplement_marking_meta_sub_section(
    semaphore: asyncio.Semaphore, subsection_dict: dict, company_name: str, subsection_cfg: dict, model: str = 'gpt-4.1'
) -> dict:
    subsection_no = subsection_dict['no']
    subsection_obj = subsection_cfg[subsection_no]
    subsection_type = subsection_obj['type']
    subsection_type = SType[subsection_type]

    if subsection_type in [SType.I2, SType.I3]:
        for item_dict in subsection_dict['items']:
            if 'marking' not in item_dict and re.search(r'summary', item_dict['name'], flags=re.I):
                item_dict['marking'] = await generate_abstraction_questions(
                    semaphore, item_dict, subsection_no, company_name, model=model, template=S_Q_PROMPT_NEWS
                )
    elif subsection_type in [SType.A]:
        for item_dict in subsection_dict['items']:
            if 'marking' not in item_dict:
                item_dict['marking'] = await generate_abstraction_questions(
                    semaphore, item_dict, subsection_no, company_name, model=model
                )
    elif subsection_type in [SType.I]:
        for item_dict in subsection_dict['items']:
            if 'marking' not in item_dict:
                item_dict['marking'] = await generate_interpretation_criteria(
                    semaphore, item_dict, subsection_no, company_name, subsection_cfg, model=model
                )

    return subsection_dict


async def supplement_marking_meta(
    semaphore: asyncio.Semaphore,
    input_lst: list,
    company_name: str,
    subsection_cfg: dict,
    batch_size: int = 15,
    model: str = 'gpt-4.1'
) -> list:
    result = []
    for start in range(0, len(input_lst), batch_size):
        batch_tasks = []
        for sub_section_dict in input_lst[start : start + batch_size]:
            batch_tasks.append(
                _supplement_marking_meta_sub_section(
                    semaphore, sub_section_dict, company_name, subsection_cfg, model=model
                )
            )
        batch_results = await asyncio.gather(*batch_tasks)
        result.extend(batch_results)

    return result


def get_ori_company_name(track: str, case_name: str) -> str:
    if track == 'findeepresearch':
        return COMPANY_CFG_FINDEEPRESEARCH[case_name]['company']
    elif track == 'findocresearch':
        return COMPANY_CFG_FINDOCRESEARCH[case_name]['company']
    else:
        raise ValueError(f'Unknown track: {track}')


def fix_year_inconsistency(
    company_name: str, subsection_dict: dict, subsection_cfg: dict, is_gold: bool, track: str
) -> dict:
    subsection_no = subsection_dict['no']
    subsection_obj = subsection_cfg[subsection_no]
    item_list = subsection_dict['items']
    subsection_categories = subsection_obj['categories']
    if subsection_categories == ['FY', 'FY-1']:
        true_company = get_ori_company_name(track, company_name)
        expected_years = [FY + 1, FY] if true_company in NEXT_FY_COMPANY_LIST else [FY, FY - 1]
    elif subsection_categories == ['FY', 'FY-1', 'FY-2']:
        true_company = get_ori_company_name(track, company_name)
        expected_years = [FY + 1, FY, FY - 1] if true_company in NEXT_FY_COMPANY_LIST else [FY, FY - 1, FY - 2]
    else:
        return subsection_dict

    # exclude extra empty year error
    current_years = sorted(
        list(set(item['year'] for item in item_list if item['year'] != '' and str(item['year']).isdigit())),
        reverse=True,
    )

    # gold processing
    if is_gold:
        error_msg =(
            f'Sub section: '
            f'{subsection_no} {company_name} years inconsistent: {current_years} vs {expected_years}'
        )
        assert current_years == expected_years, error_msg
        for item in item_list:
            order = current_years.index(item['year'])
            item['category'] = subsection_categories[order]

    return subsection_dict


def update_converted_lst(
    company_name: str, converted_lst: list, subsection_cfg: dict, is_gold: bool, track: str
) -> list:
    updated_converted_lst = []

    for subsection_dict in converted_lst:
        subsection_no = subsection_dict['no']
        item_list = subsection_dict['items']
        subsection_obj = subsection_cfg[subsection_no]
        subsection_type = subsection_obj['type']

        subsection_dict = fix_year_inconsistency(company_name, subsection_dict, subsection_cfg, is_gold, track)

        subsection_type = SType[subsection_type]

        if subsection_type == SType.R4 and is_gold:
            subsection_fields = subsection_obj['fields']
            sample_size = len(subsection_obj['categories'])
            if sample_size < len(item_list):
                random.seed(42)
                item_list = random.sample(item_list, sample_size)
            else:
                empty_item = {k: 'N/A' for k in subsection_fields}
                item_list += [empty_item.copy() for _ in range(sample_size - len(item_list))]
            updated_item_list = []
            for item_dict, item_category in zip(item_list, subsection_obj['categories']):
                if 'name' in item_dict:
                    updated_item_list.append(
                        {'name': item_dict['name'], 'value': item_dict['value'], 'category': item_category}
                    )
                else:
                    updated_item_list.append({'name': item_category, 'value': item_dict, 'category': item_category})
            updated_section_dict = {'no': subsection_no, 'items': updated_item_list}
            updated_converted_lst.append(updated_section_dict)
        else:
            updated_converted_lst.append(subsection_dict)

    return updated_converted_lst


def verify_item_total_score(converted_lst: list, subsection_cfg: dict, expected_score: int):
    total_score = 0
    for subsection_dict in converted_lst:
        item_weights = subsection_cfg[subsection_dict['no']]['item_weights']
        subsection_type = subsection_cfg[subsection_dict['no']]['type']
        subsection_type = SType[subsection_type]
        for item_idx, item_dict in enumerate(subsection_dict['items']):
            if 'category' in item_dict:
                if subsection_type == SType.R4:
                    item_score = 0
                    for nested_item_name in item_dict['value']:
                        nested_item_key = (nested_item_name, item_dict['category'])
                        sub_item_score = item_weights[nested_item_key]
                        item_score += sub_item_score
                else:
                    item_key = (item_dict['name'], item_dict['category'])
                    item_score = item_weights[item_key]
            elif 'year' in item_dict:
                item_key = (item_dict['name'], str(item_dict['year']))
                item_score = item_weights[item_key]
            else:
                item_key = (item_dict['name'], 'Value')
                item_score = item_weights[item_key]

            total_score += item_score

    assert total_score == expected_score


async def extract_one_markdown(
    semaphore: asyncio.Semaphore,
    file_path: Union[str, pathlib.Path],
    save_folder: Union[str, pathlib.Path],
    is_gold: bool = False,
    model: str = 'gpt-4.1',
    track: str = 'findeepresearch',
    overwrite: bool = False
) -> dict:
    """
    Extract structured information from markdown files and optionally generate marking criteria.

    Writes output JSON files with the following structure:
    For prediction (is_gold=False):
    {
        "converted": {
            [
                {
                    "no": "S1.1",  # Section number
                    "items": [
                        {
                            "name": "Field name",
                            "value": "Extracted value"
                        }
                    ]
                }
            ]
        },
        "format_score": {
            "overall": 42,
            "section_headers": {},
            "subseciton_headers": {},
            "subsection_tables": {}
        }
    }

    For ground truth (is_gold=True):
    [
        {
            "no": "S1.1",  # Section number
            "items": [
                {
                    "name": "Field name",
                    "value": "Extracted value",
                    "marking": [  # Marking criteria based on section type:
                        # Abstraction (A): ["yes/no/idk" questions]
                        # Interpretation (I): "evaluation criteria"
                    ]
                }
            ]
        }
    ]

    Args:
        semaphore: Semaphore to limit the number of concurrent tasks
        file_path: Path to the markdown file to process
        save_folder: Path to the folder where the output JSON files will be saved
        is_gold: If True, generates additional marking criteria for ground truth data
            If False, only extracts basic structure (default: False)
        model: llm model to use for extraction (default: 'gpt-4.1')
        track: findocresearch or findeepresearch
        overwrite: If True, overwrites existing JSON files (default: False)

    Returns:
        format mark detail.
    """

    track_subsection_cfg, track_subsection_total_score = get_subsection_info(track)

    file_path = pathlib.Path(file_path)
    company_name = file_path.stem

    location = get_location_from_company_name(company_name, track)

    save_folder = pathlib.Path(save_folder)
    save_folder.mkdir(parents=True, exist_ok=True)
    trace_folder = save_folder / 'debug' / file_path.stem

    trace_folder_cv.set(trace_folder)

    save_path = save_folder / f'{file_path.stem}.json'

    if save_path.exists() and not overwrite:
        logger.info(f'Output file already exists: {save_path}')
        converted_result = json.loads(save_path.read_text())
    else:
        try:
            converted_result = await convert_md_to_json(
                semaphore, file_path, company_name, track_subsection_cfg, model=model
            )
        except Exception as e:
            logger.error(f'Error processing {file_path}: {e}', exc_info=True)
            return {'company': company_name, 'location': location, 'format_mark': {}}  # {} indicates failure

    format_mark_details = {'overall_format_mark': converted_result['format_score']['overall']}
    for component in ['section_headers', 'subsection_headers', 'subsection_tables']:
        for key, mark in converted_result['format_score'][component].items():
            if component == 'section_headers' and re.search(r'^\d+$', key):
                key = f'S{key}_format_mark'
            elif component == 'subsection_tables':
                key = f'{key.strip()}_table_format_mark'
            else:
                key = f'{key}_format_mark'
            format_mark_details[key] = mark

    converted_result['converted'] = update_converted_lst(
        company_name, converted_result['converted'], track_subsection_cfg, is_gold, track
    )

    if not is_gold:
        save_path.write_text(json.dumps(converted_result, indent=4))
        logger.info(f'{company_name} Prediction Format Mark: {format_mark_details["overall_format_mark"]:.2f}')
    else:
        converted_lst = converted_result['converted']
        verify_item_total_score(converted_lst, track_subsection_cfg, track_subsection_total_score)
        converted_lst = await supplement_marking_meta(
            semaphore, converted_lst, company_name, track_subsection_cfg, model=model
        )
        converted_result['converted'] = converted_lst
        logger.info(f'{company_name} Gold Format Mark: {format_mark_details["overall_format_mark"]:.2f}')
        save_path.write_text(json.dumps(converted_result, indent=4))

    return {'company': company_name, 'location': location, 'format_mark': format_mark_details}


def print_mark_as_table(mark_dict: dict):
    table_data = [[key.capitalize(), value] for key, value in mark_dict.items()]
    print(tabulate(table_data, headers=['Category', 'Format Mark'], tablefmt='grid'))


def save_mark_as_xlsx(format_details: List[dict], track: str, output_path: Union[str, pathlib.Path]) -> dict:
    failed_companies = []
    for fd in format_details:
        if not fd['format_mark']:
            failed_companies.append(fd['company'])
    if failed_companies:
        raise RuntimeError(f'Format mark cannot be calculated due to failing companies: {failed_companies}')

    for fd in format_details:
        fd.update(fd.pop('format_mark'))
    df_mark_details = pd.DataFrame(format_details)
    subsection_cfg, _ = get_subsection_info(track)

    mark_dict = {}

    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    # section headers + subsection headers + subsection tables
    section_infos = pydash.group_by(subsection_cfg, lambda n: subsection_cfg[n]['section_no'])
    total_mark = len(section_infos) + len(subsection_cfg) * 2

    company_count = df_mark_details.shape[0]
    overall_mark = round(df_mark_details['overall_format_mark'].sum() / company_count, 2)

    df_overall = pd.DataFrame([overall_mark], columns=['overall'])
    df_overall.to_excel(writer, sheet_name='Overall', index=False)
    mark_dict['overall'] = f'{overall_mark}/{total_mark:.2f}'

    # Details
    df_mark_details.to_excel(writer, sheet_name='Details', index=False)

    writer.close()

    return mark_dict


async def extract_prediction_markdown(
    prediction_folder: str,
    save_folder: str,
    model: str = 'gpt-4.1',
    track: str = 'findeepresearch',
    overwrite: bool = False,
):
    logger.info(f'Begin to convert predicted markdowns to jsons at {prediction_folder}')

    prediction_folder = pathlib.Path(prediction_folder)
    save_folder = pathlib.Path(save_folder)
    prediction_files = list(prediction_folder.rglob('[!.]*.md'))

    semaphore = asyncio.Semaphore(LLM_CONCURRENCY)

    batch_tasks = []
    for prediction_file in prediction_files:
        batch_tasks.append(
            extract_one_markdown(
                semaphore, prediction_file, save_folder, is_gold=False, model=model, track=track, overwrite=overwrite
            )
        )
    format_details = await asyncio.gather(*batch_tasks)

    mark_dict = save_mark_as_xlsx(format_details, track, save_folder / 'format_evaluation.xlsx')
    print_mark_as_table(mark_dict)


async def extract_gold_markdown(track: str, phase: str = '', model: str = 'gpt-4.1', overwrite: bool = False):
    if track == 'findeepresearch':
        gold_folder = GOLD_FOLDER_FINDEEPRESEARCH / 'markdown'
        save_folder = GOLD_FOLDER_FINDEEPRESEARCH / 'converted'
    elif track == 'findocresearch':
        gold_folder = GOLD_FOLDER_FINDOCRESEARCH / 'markdown'
        save_folder = GOLD_FOLDER_FINDOCRESEARCH / 'converted'
    else:
        raise ValueError(f'Unsupported track: {track}')

    semaphore = asyncio.Semaphore(LLM_CONCURRENCY)

    gold_files = list(gold_folder.glob('**/[!.]*.md'))  # exclude structure_template.md
    already_converted_files = list(save_folder.glob('**/[!.]*.json'))

    if not len(gold_files):
        raise ValueError(f'No ground truth found. Please provide ground truth markdowns first and put them to {gold_folder}')

    if not overwrite:
        md_stems = {md.stem for md in gold_files}
        json_stems = {js.stem for js in already_converted_files}
        if md_stems == json_stems:
            return

    logger.info(f'Begin to convert ground truth markdowns to jsons for {track}')
    batch_tasks = []
    for gold_file in gold_files:
        batch_tasks.append(
            extract_one_markdown(
                semaphore, gold_file, save_folder, is_gold=True, model=model, track=track, overwrite=overwrite
            )
        )
    format_details = await asyncio.gather(*batch_tasks)

    mark_dict = save_mark_as_xlsx(format_details, track, save_folder / 'format_evaluation.xlsx')
    print_mark_as_table(mark_dict)


def add_common_args(parser):
    parser.add_argument('--track', type=str, required=True, help='findocresearch or findeepresearch')
    parser.add_argument('--model', type=str, default='gpt-4.1', help='Model name')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing results')


def main():
    setup_logger()
    parser = argparse.ArgumentParser(description='Extraction Tools')

    subparsers = parser.add_subparsers(dest='subtask', required=True)
    pred_parser = subparsers.add_parser(
        'prediction',
        help='Convert predictions for FinDocResearch or FinDeepResearch'
    )
    pred_parser.add_argument('--prediction_folder', type=str, required=True, help='Path to prediction folder')
    pred_parser.add_argument('--save_folder', type=str, required=True, help='Path to save evaluation results')
    add_common_args(pred_parser)

    gold_parser = subparsers.add_parser(
        'gold',
        help='Convert ground truths for FinDocResearch of FinDeepResearch'
    )
    add_common_args(gold_parser)

    args = parser.parse_args()

    if args.subtask == 'prediction':
        asyncio.get_event_loop().run_until_complete(
            extract_prediction_markdown(
                prediction_folder=args.prediction_folder,
                save_folder=args.save_folder,
                model=args.model,
                track=args.track,
                overwrite=args.overwrite
            )
        )
    else:
        asyncio.get_event_loop().run_until_complete(
            extract_gold_markdown(
                track=args.track,
                model=args.model,
                overwrite=args.overwrite
            )
        )


if __name__ == '__main__':
    main()
