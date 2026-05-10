import logging
import re
from datetime import datetime
from typing import List, Callable

import dateparser
import numpy as np
from scipy.optimize import linear_sum_assignment
from thefuzz import fuzz

from constants import COMPANY_CFG_FINDEEPRESEARCH, COMPANY_CFG_FINDOCRESEARCH, COMPANY_LIST_FINDEEPRESEARCH, COMPANY_LIST_FINDOCRESEARCH

logger = logging.getLogger(__name__)


def scaled_fuzz_token_sort_ratio(input1: str, input2: str) -> float:
    return fuzz.token_sort_ratio(input1, input2) / 100

def are_dates_near(date_obj1: datetime, date_obj2: datetime) -> float:
    if date_obj1 and date_obj2:
        if date_obj1 == date_obj2:
            return 1
        if abs((date_obj1 - date_obj2).days) < 3:
            return 1e-3 - abs((date_obj1 - date_obj2).days) / 1e6
    return 0

def find_best_matches(
    list1: List[any], list2: List[any], similarity_func: Callable = scaled_fuzz_token_sort_ratio, threshold: float = 0
) -> dict:
    num1, num2 = len(list1), len(list2)
    size = max([num1, num2])
    cost_matrix = np.full((size, size), 1.0)

    for i, name1 in enumerate(list1):
        for j, name2 in enumerate(list2):
            score = similarity_func(name1, name2)
            cost_matrix[i, j] = 1 - score

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    match = {}

    for r, c in zip(row_ind, col_ind):
        if r >= num1 or c >= num2:
            continue
        score = 1 - cost_matrix[r, c]
        if score > threshold:
            match[r] = c

    return match


def is_value_missing(value: str) -> bool:
    value = re.sub(r'[.*\/]', '', value)
    return value.upper().strip() in ['NA', '']


def is_prediction_value_invalid(value: str) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.upper() in ['']
    return False


def compose_item_trace_id(sub_section_no: str, item_name: str, item_year: str = '') -> str:
    item_name = item_name.replace('/', '_')
    if not item_year:
        return f'{sub_section_no}_{item_name}'
    else:
        return '_'.join([sub_section_no, item_name, item_year])


def get_company_from_report_name(report_name: str):
    return report_name


def get_location_from_company_name(company_name: str, track: str):
    if track == 'findocresearch':
        assert company_name in COMPANY_LIST_FINDOCRESEARCH, f'Incorrect company name: {company_name}'
        location = COMPANY_CFG_FINDOCRESEARCH[company_name]['location']
        return location
    elif track == 'findeepresearch':
        assert company_name in COMPANY_LIST_FINDEEPRESEARCH, f'Incorrect company name: {company_name}'
        location = COMPANY_CFG_FINDEEPRESEARCH[company_name]['location']
        return location
    else:
        raise ValueError(f'Incorrect track: {track}')


def parse_date(date_string: str) -> datetime:
    date_obj = dateparser.parse(date_string)
    if date_obj is None:
        pattern1 = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b'
        pattern2 = r'\d+-\d+-\d+'
        date_pattern = '|'.join(f'(?:{p})' for p in [pattern1, pattern2])
        date_m = re.search(date_pattern, date_string, re.I)
        if date_m:
            date_obj = dateparser.parse(date_m.group())
    if date_obj is None:
        date_string = re.sub(r'\([^)]+\)', '', date_string).strip()
        date_obj = dateparser.parse(date_string)

    return date_obj


def setup_logger() -> None:
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
