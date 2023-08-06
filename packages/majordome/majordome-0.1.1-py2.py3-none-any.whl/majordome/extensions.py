# -*- coding: utf-8 -*-


class ExtendedDict(dict):
    def get_nested(self, *args):
        """ Recursive access of nested dictionary. """
        if not self:
            raise KeyError("Dictionary is empty")

        if not args or len(args) < 1:
            raise ValueError("No arguments were provided")

        value = self.get(args[0])

        return value if len(args) == 1 else \
            ExtendedDict(value).get_nested(*args[1:])
