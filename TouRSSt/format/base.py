class TouRSStFormatterBase:
    """Base class for formatting RSS items."""

    def __init__(self):
        pass

    def format(self, item, feed):
        raise "This is an abstract baseclass."
