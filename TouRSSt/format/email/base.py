import TouRSSt.format.base

class TouRSStFormatterEmailBase(TouRSSt.format.base.TouRSStFormatterBase):
    def __init__(self):
        TouRSSt.format.base.TouRSStFormatterBase.__init__(self)

    def format(self, item, feed):
        raise "This is an abstract baseclass."
