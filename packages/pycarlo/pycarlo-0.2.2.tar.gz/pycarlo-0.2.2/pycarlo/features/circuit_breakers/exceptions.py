class CircuitBreakerPipelineException(Exception):
    pass


class CircuitBreakerPollException(Exception):
    def __init__(self, msg='Polling timed out or contains a malformed log.', *args):
        super().__init__(msg, *args)
