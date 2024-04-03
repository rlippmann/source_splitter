"""Source file exceptions."""


class SSParseFailed(RuntimeError):
    """Parse failed exception."""

    def __init__(self, message: str) -> None:
        """Initialize a ParseFailed exception.

        Args:
            message (str): The message of the exception.

        Returns:
            None
        """
        super().__init__(message)


class SSNoLanguageFound(RuntimeError):
    """No language found exception."""

    def __init__(self, message: str) -> None:
        """Initialize a NoLanguageFound exception.

        Args:
            message (str): The message of the exception.

        Returns:
            None
        """
        super().__init__(message)
