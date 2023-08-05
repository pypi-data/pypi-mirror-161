from vayaAuto.option import Option


class Section(dict):

    def __init__(self, name):
        super(Section, self).__init__()
        self._name = name
        # self.options = {}

    def add_option(self, name):
        # value_type = type(self.VAYA_CONFIG[self._name][name])
        option = Option(name)
        # self.options.update({name: option})
        self[name] = option

    # def keys(self):
    #     return self.options.keys()
    #     # return self.__dict__.keys()
    #
    # def items(self):
    #     return self.options.items()
        # return self.__dict__.items()

    # def __iter__(self):
    #
    #     for (name, option) in self.options.items():
    #         yield name, option
    #
    # def __hash__(self):
    #     return hash(tuple(sorted(self.options)))

    # def __setitem__(self, key, value):
    #     # if value.lower() not in self.BOOLEAN_STATES:
    #     #     raise ValueError('Not a boolean: %s' % value)
    #     # return self.BOOLEAN_STATES[value.lower()]
    #     self.options[key] = value
    #
    # def __getitem__(self, key):
    #     return self.options[key]

    # def __str__(self):
    #     return f"{self.options}"
    #
    # def __repr__(self):
    #     return f"{self.options}"