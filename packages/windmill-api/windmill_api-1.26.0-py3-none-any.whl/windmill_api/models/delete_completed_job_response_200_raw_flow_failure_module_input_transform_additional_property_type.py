from enum import Enum


class DeleteCompletedJobResponse200RawFlowFailureModuleInputTransformAdditionalPropertyType(str, Enum):
    STATIC = "static"
    JAVASCRIPT = "javascript"

    def __str__(self) -> str:
        return str(self.value)
