class Layer(object):
    def __repr__(self):
        return "%-13s" % (self.name())

    def build(self):
        pass

    def entrypoint(self):
        pass

    def name(self):
        return self.__class__.__name__.lower()
