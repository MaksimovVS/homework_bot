class TokenError(Exception):
    """Raised when the token is not available in the environment."""

    def __init__(self, message='Invalid or unavailable tokens'):
        self.message = message
        super().__init__(self.message)
