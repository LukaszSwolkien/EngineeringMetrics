class IAException(Exception):
    """General error raised for all problems in operation."""

    def __init__(self, status_code=None, text=None, url=None):
        self.status_code = status_code
        self.text = text
        self.url = url

    def __str__(self):
        """Return a string representation of the error."""
        t = "JiraError HTTP %s" % self.status_code
        if self.url:
            t += " url: %s" % self.url
        if self.text:
            t += "\n\ttext: %s" % self.text

        return t