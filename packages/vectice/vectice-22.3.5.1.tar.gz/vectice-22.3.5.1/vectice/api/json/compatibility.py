class CompatibilityOutput:
    def __init__(self, message: str, status: str, *args, **kwargs):
        self._message = message
        self._status = status

    @property
    def message(self):
        return self._message

    @property
    def status(self):
        return self._status
