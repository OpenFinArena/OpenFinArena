import contextvars
import pathlib

trace_folder_cv = contextvars.ContextVar('trace_folder', default=pathlib.Path(__file__).parent / 'traces')
