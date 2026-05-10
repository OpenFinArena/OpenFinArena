import json
import pathlib
from itertools import product
from typing import Optional

COMPANY_CFG_FINDOCRESEARCH = json.loads(
    (pathlib.Path(__file__).parent / 'resources/findocresearch_companies.json').read_text()
)
COMPANY_LIST_FINDOCRESEARCH = list(COMPANY_CFG_FINDOCRESEARCH)

COMPANY_CFG_FINDEEPRESEARCH = json.loads(
    (pathlib.Path(__file__).parent / 'resources/findeepresearch_companies.json').read_text()
)
COMPANY_LIST_FINDEEPRESEARCH = list(COMPANY_CFG_FINDEEPRESEARCH)

GOLD_FOLDER_FINDOCRESEARCH = pathlib.Path(__file__).parent / 'data/ground_truth/findocresearch_track'
GOLD_FOLDER_FINDEEPRESEARCH = pathlib.Path(__file__).parent / 'data/ground_truth/findeepresearch_track'


FY = 2024
MARKETS = ['USA', 'UK', 'China', 'Hong Kong', 'Australia', 'Singapore', 'Malaysia', 'Indonesia']
NEXT_FY_COMPANY_LIST = ['Singapore Airlines Ltd', 'Singapore Shipping Corporation Ltd']


LLM_CONCURRENCY = 10


def flatten_cfg(prefix='findeepresearch'):
    cfg = json.loads((pathlib.Path(__file__).parent / f'resources/{prefix}_weights.json').read_text())

    flattened_dict = {}

    for section_no, section_cfg in cfg.items():
        section_n = section_cfg['name']
        tracked_subsections = []
        for sub_no, sub_cfg in section_cfg['details'].items():
            sub_cfg = sub_cfg.copy()
            item_num_only_weights = sub_cfg.pop('item_weights')
            item_weights = {}
            item_keys = list(product(sub_cfg['fields'], sub_cfg['categories']))
            items_count = len(item_keys)
            if isinstance(item_num_only_weights, int):
                item_weights = {item_key: item_num_only_weights for item_key in item_keys}
            else:
                assert (
                    len(item_num_only_weights) == items_count
                ), f'Number of item weights does not match number of items in {section_no} {sub_no}'
                for item_key, item_weight in zip(item_keys, item_num_only_weights):
                    item_weights[item_key] = item_weight

            flattened_dict[sub_no] = {
                **sub_cfg,
                'no': sub_no,
                'weight': sum(item_weights.values()),
                'item_weights': item_weights,
                'section_name': section_n,
                'section_no': section_no,
            }
            tracked_subsections.append(flattened_dict[sub_no])

        section_weight = sum(sub_cfg['weight'] for sub_cfg in tracked_subsections)
        for sub_cfg in tracked_subsections:
            sub_cfg['section_weight'] = section_weight

    return cfg, flattened_dict


SECTION_CFG_FINDOCRESEARCH, SUB_SECTION_CFG_FINDOCRESEARCH = flatten_cfg(prefix='findocresearch')
SECTION_CFG_FINDEEPRESEARCH, SUB_SECTION_CFG_FINDEEPRESEARCH = flatten_cfg(prefix='findeepresearch')


def get_subsection_info(prefix='findeepresearch'):
    if prefix == 'findocresearch':
        return SUB_SECTION_CFG_FINDOCRESEARCH, 240
    elif prefix == 'findeepresearch':
        return SUB_SECTION_CFG_FINDEEPRESEARCH, 350
    else:
        raise ValueError(f'Invalid prefix: {prefix}')


def get_ground_truth_folder(prefix='findeepresearch', phase: Optional[str] = None):
    if prefix == 'findocresearch':
        ground_truth_folder = GOLD_FOLDER_FINDOCRESEARCH / 'converted'
    elif prefix == 'findeepresearch':
        ground_truth_folder = GOLD_FOLDER_FINDEEPRESEARCH / 'converted'
    else:
        raise ValueError(f'Invalid prefix: {prefix}')

    return ground_truth_folder


SPLIT_REGEX_MAP = {
    'hashtag': {
        'section_split': r'(?=(?:^|\n)#+[^#\d]+\d[^#\d]+\n)',
        'section_header': r'^#+([^#]+?)\n',
        'subsection_split': rf'(?=(?:(?:\n#+[^#\d]+\d\.\d[^#\d\n]*\n)|(?:\n#+[^#\d]+\d\.\d[^#\n]+\((?:[^)]*{FY}|as of[^)]+)\)(?:\*\*)? *\n)))',
        'subsection_header': rf'^#+((?:[^#\d]+?\d\.\d[^#\d\n]*)|(?:[^#\d]+?\d\.\d[^#\n]+\((?:[^)]*{FY}|as of[^)]+)\)(?:\*\*)?)) *\n',
    },
    'asterisk': {
        'section_split': r'(?=(?:^|\n)\*+[^*\d]+\d[^*\d]+\*+\s*\n)',
        'section_header': r'^\*+([^*]+?)\*+\s*\n',
        'subsection_split': r'(?=\n\*+[^*]+\d\.\d[^*]+\*+)',
        'subsection_header': r'^\*+([^*]+\d\.\d[^*]+)\*+',
    },
}


def get_summary_length_tolerance_for_track(track: str) -> float:
    return 2.5 if track == 'findocresearch' else 10000
