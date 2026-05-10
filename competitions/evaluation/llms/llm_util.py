import asyncio
import json
import logging
import random
from typing import Optional, Union

from openai import APIConnectionError, AsyncOpenAI, InternalServerError
from pydantic import BaseModel, ValidationError

from env import OPENAI_KEY
from evaluation.llms.tools import call_function
from evaluation.llms.trace_util import Tracer

logger = logging.getLogger(__name__)


try:
    from evaluation.llms.cache_util import llm_cache
except ImportError:
    logger.info('Using dummy llm cache...')

    def llm_cache(func):
        """
        Dummy fallback decorator
        """
        return func


# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 3,
    errors: tuple = (ValidationError,APIConnectionError,InternalServerError),
):
    """Retry a function with exponential backoff."""

    async def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return await func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )
                logger.info(f'Retrying in {delay} seconds due to {e}')
                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                await asyncio.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


@retry_with_exponential_backoff
async def chat_with_openai(
    prompt: str,
    model: str = 'gpt-4.1',
    temperature: float = 0.0,
    tools: Optional[list] = None,
    schema: Optional[BaseModel] = None,
    trace_id: Optional[str] = None,
    max_output_tokens: int = 16384,
) -> Union[Optional[str], BaseModel]:
    openai_client = AsyncOpenAI(api_key=OPENAI_KEY)
    param_by_model = {}
    if model != 'gpt-5':
        param_by_model['temperature'] = temperature

    tracer = Tracer(trace_id)

    tracer.log_step('1_prompt', prompt)

    if not tools:
        if schema:
            response = await openai_client.responses.parse(
                model=model,
                input=[{'role': 'user', 'content': prompt}],
                max_output_tokens=max_output_tokens,
                text_format=schema,
                **param_by_model,
            )
            tracer.log_step('2_response_raw', response.output_text)
            tracer.log_step('2_response_parsed', response.output_parsed)
            return response.output_parsed
        else:
            response = await openai_client.responses.create(
                model=model,
                input=[{'role': 'user', 'content': prompt}],
                max_output_tokens=max_output_tokens,
                **param_by_model,
            )
            tracer.log_step('2_response_raw', response.output_text)
            return response.output_text
    else:
        input_list = [{'role': 'user', 'content': prompt}]

        if not schema:
            response = await openai_client.responses.create(
                model=model, input=input_list, tools=tools, max_output_tokens=max_output_tokens, **param_by_model
            )
        else:
            response = await openai_client.responses.parse(
                model=model,
                input=input_list,
                text_format=schema,
                tools=tools,
                max_output_tokens=max_output_tokens,
                **param_by_model,
            )
        input_list += response.output

        function_outputs = []
        for item in response.output:
            if item.type == 'function_call':
                name = item.name
                kwargs = json.loads(item.arguments)
                result = call_function(name, kwargs)
                function_outputs.append({'type': 'function_call_output', 'call_id': item.call_id, 'output': result})

                tracer.log_step(f'2_function_call_input_{name}', kwargs)
                tracer.log_step(f'2_function_call_output_{name}', result)

        if not function_outputs:
            if not schema:
                tracer.log_step('2_response_raw', response.output_text)
                return response.output_text
            else:
                tracer.log_step('2_response_raw', response.output_text)
                tracer.log_step('2_response_parsed', response.output_parsed)
                return response.output_parsed

        input_list += function_outputs
        if not schema:
            response = await openai_client.responses.create(
                model=model, input=input_list, tools=tools, max_output_tokens=max_output_tokens, **param_by_model
            )
            tracer.log_step('3_response_raw', response.output_text)
            return response.ouput_text
        else:
            response = await openai_client.responses.parse(
                model=model,
                input=input_list,
                text_format=schema,
                tools=tools,
                max_output_tokens=max_output_tokens,
                **param_by_model,
            )
            if not response.output_text:
                logger.error(f'Empty response on {prompt}.')
                raise InternalServerError
            tracer.log_step('3_response_raw', response.output_text)
            tracer.log_step('3_response_parsed', response.output_parsed)
            return response.output_parsed


@llm_cache
async def chat_with_llm(
    prompt: str,
    model: str = 'gpt-4.1',
    temperature: float = 0.0,
    tools: Optional[list] = None,
    schema: Optional[BaseModel] = None,
    trace_id: Optional[str] = None,
) -> Union[Optional[str], BaseModel]:
    if model.startswith('gpt-'):
        return await chat_with_openai(
            prompt=prompt,
            model=model,
            temperature=temperature,
            tools=tools,
            schema=schema,
            trace_id=trace_id,
        )
    else:
        raise NotImplementedError
