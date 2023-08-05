from enum import Enum


class GetHubFlowByIdResponse200FlowValueModulesItemValueType(str, Enum):
    SCRIPT = "script"
    FLOW = "flow"
    RAWSCRIPT = "rawscript"
    FORLOOPFLOW = "forloopflow"

    def __str__(self) -> str:
        return str(self.value)
