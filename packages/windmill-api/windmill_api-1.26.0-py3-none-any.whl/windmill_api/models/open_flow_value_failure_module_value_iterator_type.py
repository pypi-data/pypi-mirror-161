from enum import Enum


class OpenFlowValueFailureModuleValueIteratorType(str, Enum):
    STATIC = "static"
    JAVASCRIPT = "javascript"

    def __str__(self) -> str:
        return str(self.value)
