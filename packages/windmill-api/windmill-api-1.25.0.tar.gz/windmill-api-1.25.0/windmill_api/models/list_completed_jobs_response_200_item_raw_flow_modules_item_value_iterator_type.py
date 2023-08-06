from enum import Enum


class ListCompletedJobsResponse200ItemRawFlowModulesItemValueIteratorType(str, Enum):
    STATIC = "static"
    JAVASCRIPT = "javascript"

    def __str__(self) -> str:
        return str(self.value)
