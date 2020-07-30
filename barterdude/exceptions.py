class StopFailFlowException(Exception):
    pass


class StopSuccessFlowException(Exception):
    pass


class RestartFlowException(Exception):
    pass


ALL_FLOW = (
    StopFailFlowException, StopSuccessFlowException, RestartFlowException)
