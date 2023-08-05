

class Option(object):

    def __init__(self, name, value_type=None):
        self._name = name
        self._type = value_type
        self._value = ''

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, str):
            self._value = value
        else:
            raise ValueError(f'Expect str got a {type(value)}')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def isOn(self):
        if self._value == 'true':
            return True
        else:
            return False

    def isOff(self):
        return not self.isOn()

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

# if value.lower() not in self.BOOL_TO_STR:
    #     raise ValueError('Not a boolean: %s' % value)
    # return self.BOOL_TO_STR[value.lower()]