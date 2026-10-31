from enum import Enum


class AuditActionType(str, Enum):
    USER_REGISTER = "user.register"
    USER_LOGIN = "user.login"
    USER_PASSWORD_CHANGE = "user.password_change"


class AuditActorType(str, Enum):
    USER = "user"
    SERVICE = "service"


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
