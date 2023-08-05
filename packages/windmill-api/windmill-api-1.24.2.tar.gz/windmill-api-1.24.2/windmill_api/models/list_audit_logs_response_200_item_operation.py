from enum import Enum


class ListAuditLogsResponse200ItemOperation(str, Enum):
    JOBSRUN = "jobs.run"
    SCRIPTSCREATE = "scripts.create"
    SCRIPTSUPDATE = "scripts.update"
    USERSCREATE = "users.create"
    USERSDELETE = "users.delete"
    USERSSETPASSWORD = "users.setpassword"
    USERSUPDATE = "users.update"
    USERSLOGIN = "users.login"
    USERSTOKENCREATE = "users.token.create"
    USERSTOKENDELETE = "users.token.delete"
    VARIABLESCREATE = "variables.create"
    VARIABLESDELETE = "variables.delete"
    VARIABLESUPDATE = "variables.update"

    def __str__(self) -> str:
        return str(self.value)
