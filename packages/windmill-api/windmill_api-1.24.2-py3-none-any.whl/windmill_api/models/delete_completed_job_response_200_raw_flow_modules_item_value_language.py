from enum import Enum


class DeleteCompletedJobResponse200RawFlowModulesItemValueLanguage(str, Enum):
    DENO = "deno"
    PYTHON3 = "python3"

    def __str__(self) -> str:
        return str(self.value)
