UNCOMMITTED_BRANCH_NAME = "tmp-torque-"
DEFAULT_TIMEOUT = 30
FINAL_SB_STATUSES = ["Active", "Active With Error", "Ended", "Ended With Error", "Terminating", "Terminating Failed"]
DONE_STATUS = "Done"

BLUEPRINT_SOURCE_TYPE_API_MAP = {"git": "git_repository", "torque": "qtorque"}


class ConstantBase:
    def __new__(cls, *args, **kwargs):
        raise TypeError("Constants class cannot be instantiated")


class TorqueConfigKeys(ConstantBase):
    TOKEN = "token"
    SPACE = "space"
    ACCOUNT = "account"
