from docopt import DocoptExit

from torque.constants import BLUEPRINT_SOURCE_TYPE_API_MAP


# generic/shared validations
class CommandInputValidator:
    @staticmethod
    def validate_commit_and_branch_specified(branch: str, commit: str):
        if commit and branch is None:
            raise DocoptExit("Since commit is specified, branch is required")


class BlueprintInputValidator:
    @staticmethod
    def validate_source(value: str):
        types = list(BLUEPRINT_SOURCE_TYPE_API_MAP.keys())
        if value not in types:
            raise DocoptExit(f"--source value must be in {types}")


class SandboxListValidator:
    @staticmethod
    def validate_filter(value: str):
        if value not in ["my", "all", "auto"]:
            raise DocoptExit("--filter value must be in [my, all, auto]")


class SandboxStartInputValidator:
    @staticmethod
    def validate_timeout(timeout: str):
        if timeout is not None:
            try:
                timeout = int(timeout)
            except ValueError:
                raise DocoptExit("Timeout must be a number")

            if timeout < 0:
                raise DocoptExit("Timeout must be positive")

    @staticmethod
    def validate_duration(duration: str):
        if duration is not None:
            try:
                duration = int(duration)
                if duration <= 0:
                    raise DocoptExit("Duration must be positive")
            except ValueError:
                raise DocoptExit("Duration must be a number")

    @staticmethod
    def validate_source(args: dict):
        types = list(BLUEPRINT_SOURCE_TYPE_API_MAP.keys())
        value = args.get("--source", None)
        if not value:
            return

        if value not in types:
            raise DocoptExit(f"--source value must be in {types}")

        if value == "torque" and any([args["--branch"], args["--commit"]]):
            raise DocoptExit("If blueprint source is 'torque', neither --branch nor --commit must be specified")
