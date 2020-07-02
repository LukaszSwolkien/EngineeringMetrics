class IAException(Exception):
    """General error raised for all problems in operation."""

    def __init__(self, status_code=None, text=None, url=None):
        self.status_code = status_code
        self.text = text
        self.url = url

    def __str__(self):
        """Return a string representation of the error."""
        t='IAException'
        if self.status_code:
            t += f" - status code: {self.status_code}"
        if self.url:
            t += f" url: {self.url}"
        if self.text:
            t += f"\ntext: {self.text}"

        return t
