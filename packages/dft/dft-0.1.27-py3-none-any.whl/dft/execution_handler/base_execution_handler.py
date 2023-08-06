from typing import Dict


class BaseExecutionHandler:
    def set_context(self, context: Dict[str, any]):
        self.context = context
