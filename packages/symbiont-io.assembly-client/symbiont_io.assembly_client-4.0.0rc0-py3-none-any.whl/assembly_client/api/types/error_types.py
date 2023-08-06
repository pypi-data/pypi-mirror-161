import logging

logger = logging.getLogger(__name__)

CONTRACT_REQUEST_SERVER_ERROR = "ContractRequestServerError"


class BaseError(Exception):
    def __init__(self, code, error_type, message, inner=None):
        self.message = message
        self.inner = inner
        self.code = code
        self.error_type = error_type

    def log(self):
        logger.warning(str(self))

    def log_error(self):
        logger.error(str(self))

    def to_json(self):
        return {
            "code": self.code,
            "type": self.error_type,
            "message": self.message,
            "data": str(self.inner)
            if isinstance(self.inner, Exception)
            else self.inner,
        }


class VmError(BaseError):
    def __str__(self):
        messages = [
            self.__class__.__name__,
            "Message: {}".format(self.message),
            "Inner Exception: {}".format(self.inner),
        ]
        if self.inner is not None and hasattr(self.inner, "__traceback__"):
            tb = traceback.extract_tb(self.inner.__traceback__)
            if tb:
                messages.append("traceback: {}".format(str(tb)))

        return "\n".join(messages)


class BaseContractError(VmError):
    """execution time error, type thrown by user code"""

    def __init__(self, message, inner=None):
        status_code = 500
        # determine the class that is extending BaseContractError to figure out the status code
        # this avoids changing the errors_type module in every language version
        sub_class_name = getattr(getattr(self, "__class__", None), "__name__", None)
        if sub_class_name == "ContractError":
            status_code = 400

        super().__init__(
            status_code, CONTRACT_REQUEST_SERVER_ERROR, f"{message}", inner=inner
        )


class ContractError(BaseContractError):
    """execution time error, type thrown by user code"""

    def __init__(self, message, inner=None):
        super().__init__(message, inner=inner)


class DuplicatePublishError(VmError):
    """for when a user publishes the same contract a second time"""

    def __init__(self, contract_ref):
        super().__init__(
            404,
            type(self).__name__,
            "attempted publish but contract already published: '{}'".format(
                contract_ref
            ),
        )
