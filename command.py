import os
from configobj import ConfigObj


class Command(object):
    def __init__(self, filename):
        self.dict = ConfigObj(filename, unrepr=True)

    def getCommandText(self, name):
        if self.dict.has_key(name):
            return self.dict.get(name)
        else:
            return name


if __name__ == '__main__':
    pass

