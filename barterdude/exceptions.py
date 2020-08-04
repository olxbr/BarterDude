class FlowException(Exception):
    pass


class StopFailFlowException(FlowException):
    pass


class StopSuccessFlowException(FlowException):
    pass


class RestartFlowException(FlowException):
    pass
