import json
import logging
import pathlib
from typing import Any, Optional

from pydantic import BaseModel

from contexts import trace_folder_cv
from env import TRACE_ENABLED

logger = logging.getLogger(__name__)


class Tracer:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id

    def log_step(self, step_name: str, data: Any):
        """Logs data to a uniquely named file within the run's trace directory."""

        if self.trace_id is None or not TRACE_ENABLED:
            return

        use_trace_folder = pathlib.Path(trace_folder_cv.get())
        use_trace_folder.mkdir(parents=True, exist_ok=True)
        file_path = use_trace_folder / f'{self.trace_id}_{step_name}.txt'

        try:
            if isinstance(data, (dict, list)):
                try:
                    file_path.write_text(json.dumps(data, indent=4))
                except TypeError:
                    file_path.write_text(str(data))
            elif isinstance(data, BaseModel):
                file_path.write_text(data.model_dump_json(indent=4))
            else:
                file_path.write_text(str(data))
        except Exception as e:
            logger.info(f"❌ Failed to log '{self.trace_id}_{step_name}': {e}")
