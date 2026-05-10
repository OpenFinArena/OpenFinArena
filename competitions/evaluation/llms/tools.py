import json
import logging
import math

logger = logging.getLogger(__name__)


NUM_COMPARATOR_TOOLS = [
    {
        'type': 'function',
        'name': 'compare_within_tolerance',
        'description': "Use this function when two numbers are not the same and want to check if they are equal within a tolerance.",
        'parameters': {
            'type': 'object',
            'properties': {
                'calculated_answer': {
                    'type': 'number',
                    'description': 'calculated answer',
                },
                'correct_answer': {
                    'type': 'number',
                    'description': 'correct answer',
                },
            },
            'required': ['calculated_answer', 'correct_answer'],
        },
    },
]


def compare_within_tolerance(calculated_answer: float, correct_answer: float) -> bool:
    if math.isclose(abs(calculated_answer), abs(correct_answer), rel_tol=0.01, abs_tol=0.005):
        return True
    else:
        return False


def call_function(name, kwargs):
    logger.info(f'Calling function {name} with kwargs {kwargs}')
    if name == 'compare_within_tolerance':
        r = json.dumps({'is_equal_within_tolerance': compare_within_tolerance(**kwargs)})
    else:
        raise ValueError(f'Unsupported function name: {name}')
    logger.info(f'Function {name} returned: {r}')
    return r
