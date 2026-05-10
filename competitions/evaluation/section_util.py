from enum import Enum, auto
from typing import List, Union

from constants import FY, NEXT_FY_COMPANY_LIST
from evaluation.prompts import extractor_prompt


class SType(Enum):
    # field/numeric value for 3 fiscal years
    R1 = auto()
    # field/value
    R2 = auto()
    # field/numeric value for 3 fiscal years with currency and multiplier
    R3 = auto()
    # field/dict value
    R4 = auto()
    # calculation, field/value for 3 fiscal years
    C = auto()
    # calculation, field/value for two calendar years
    C2 = auto()
    # calculation, field/value
    C3 = auto()
    # summary, field/value for 2 fiscal years
    A = auto()
    # field/value
    I = auto()
    # top(date, summary)/value for two calendar years
    I2 = auto()
    # top(date, car, summary)/value for two calendar years
    I3 = auto()

    def to_level(self):
        if self.name.startswith('R'):
            return 'level1'
        elif self.name.startswith('C'):
            return 'level2'
        elif self.name.startswith('A'):
            return 'level3'
        elif self.name.startswith('I'):
            return 'level4'
        else:
            raise ValueError(f'Unknown question type: {self.name}')


def get_subsection_structure_regex_lst(subsection_type: Union[str, SType], company_name: str) -> List[str]:
    if isinstance(subsection_type, str):
        subsection_type = SType[subsection_type]
    if subsection_type in [SType.R1, SType.C]:
        if company_name in NEXT_FY_COMPANY_LIST:
            column_regex_lst = [rf'\|[^|]*{FY+1}[^|]*\|', rf'\|[^|]*{FY}[^|]*\|', rf'\|[^|]*{FY-1}[^|]*\|$']
        else:
            column_regex_lst = [rf'\|[^|]*{FY}[^|]*\|', rf'\|[^|]*{FY-1}[^|]*\|', rf'\|[^|]*{FY-2}[^|]*\|$']
    elif subsection_type in [SType.R2, SType.I, SType.C3]:
        column_regex_lst = [r'\|[^|]*Value|Answer[^|]*\|$']
    elif subsection_type == SType.R3:
        if company_name in NEXT_FY_COMPANY_LIST:
            column_regex_lst = [
                rf'\|[^|]*{FY+1}[^|]*\|',
                rf'\|[^|]*{FY}[^|]*\|',
                rf'\|[^|]*{FY-1}[^|]*\|',
                r'\|[^|]*Multiplier[^|]*\|',
                r'\|[^|]*Currency[^|]*\|$'
            ]
        else:
            column_regex_lst = [
                rf'\|[^|]*{FY}[^|]*\|',
                rf'\|[^|]*{FY-1}[^|]*\|',
                rf'\|[^|]*{FY-2}[^|]*\|',
                r'\|[^|]*Multiplier[^|]*\|',
                r'\|[^|]*Currency[^|]*\|$',
            ]
    elif subsection_type == SType.R4:
        column_regex_lst = ['.']
    elif subsection_type == SType.A:
        if company_name in NEXT_FY_COMPANY_LIST:
            column_regex_lst = [rf'\|[^|]*{FY+1}[^|]*\|', rf'\|[^|]*{FY}[^|]*\|$']
        else:
            column_regex_lst = [rf'\|[^|]*{FY}[^|]*\|', rf'\|[^|]*{FY-1}[^|]*\|$']
    elif subsection_type in [SType.I2, SType.I3, SType.C2]:
        column_regex_lst = [rf'\|[^|]*{FY}[^|]*\|', rf'\|[^|]*{FY-1}[^|]*\|']
    else:
        raise ValueError(f'Unknown subsection type: {subsection_type}')

    return column_regex_lst


def get_prompt_template_by_type(type_string: str, table_score: float = 1):
    if isinstance(type_string, str):
        type_string = SType[type_string]
    if type_string in [SType.R1, SType.A, SType.C, SType.C2, SType.I2, SType.I3]:
        # year value
        return extractor_prompt.RAI_PROMPT if table_score > 0 else extractor_prompt.RAI_PROMPT_GENERAL
    elif type_string in [SType.R2, SType.I, SType.C3]:
        # value only
        return extractor_prompt.R2_PROMPT if table_score > 0 else extractor_prompt.R2_PROMPT_GENERAL
    elif type_string == SType.R3:
        # value + multiplier + currency
        return extractor_prompt.R3_PROMPT if table_score > 0 else extractor_prompt.R3_PROMPT_GENERAL
    elif type_string == SType.R4:
        # custom category
        return extractor_prompt.R4_PROMPT if table_score > 0 else extractor_prompt.R4_PROMPT_GENERAL
    else:
        raise ValueError(f'Unrecognized type_string: {type_string}')
