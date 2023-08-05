from enum import Enum


class GetScriptByHashResponse200Language(str, Enum):
    PYTHON3 = "python3"
    DENO = "deno"

    def __str__(self) -> str:
        return str(self.value)
