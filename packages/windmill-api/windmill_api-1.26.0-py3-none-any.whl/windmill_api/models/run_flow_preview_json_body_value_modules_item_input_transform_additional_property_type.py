from enum import Enum


class RunFlowPreviewJsonBodyValueModulesItemInputTransformAdditionalPropertyType(str, Enum):
    STATIC = "static"
    JAVASCRIPT = "javascript"

    def __str__(self) -> str:
        return str(self.value)
