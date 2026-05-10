import os
import pathlib

from dotenv import load_dotenv

env_file = pathlib.Path(__file__).parent / '.env'


load_dotenv(env_file)

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

assert OPENAI_KEY, 'Please provide a valid OPENAI_KEY to run the evaluation.'

TRACE_ENABLED = os.environ.get('TRACE_ENABLED') == 'true'
