from argparse import Action, _copy_items

class AppendNewline(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # append new line if not present
        if values[-2:] != '\n':
            setattr(namespace, self.dest, values + '\n')


# todo: understand from https://sumit-ghosh.com/articles/parsing-dictionary-key-value-pairs-kwargs-argparse-python/ # noqa
class ParseKwargs(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for key, val in values:
            getattr(namespace, self.dest)[key] = val


class ParseKwargsAppend(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for key, val in values:
            if key in getattr(namespace, self.dest):
                getattr(namespace, self.dest)[key].append(val)
            else:
                getattr(namespace, self.dest)[key] = [val]


class AppendKwargs(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = _copy_items(items)
        items.append({key: val for key, val in values})
        setattr(namespace, self.dest, items)


class OrderAction(Action):
    def __init__(self, option_strings, dest, nargs=0, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None):

        super().__init__(
            option_strings=option_strings, dest=dest, nargs=nargs,
            default=default, type=type, choices=choices, required=required,
            help=help, metavar=metavar
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # setattr(namespace, self.dest, values)
        order = getattr(namespace, 'order') if hasattr(namespace, 'order') else []
        order.extend([(self.dest, val) for val in values] or [(self.dest, None)])
        setattr(namespace, 'order', order)


# BooleanOptionalAction class until widely available in official argparse
# module. todo: remove when available
class BooleanOptionalAction(Action):
    def __init__(self, option_strings, dest, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None):

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith('--'):
                option_string = '--no-' + option_string[2:]
                _option_strings.append(option_string)

        if help is not None and default is not None:
            help += " (default: %(default)s)"

        super().__init__(
            option_strings=_option_strings, dest=dest, nargs=0,
            default=default, type=type, choices=choices, required=required,
            help=help, metavar=metavar
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith(
                '--no-'
            ))

    def format_usage(self):
        return ' | '.join(self.option_strings)

