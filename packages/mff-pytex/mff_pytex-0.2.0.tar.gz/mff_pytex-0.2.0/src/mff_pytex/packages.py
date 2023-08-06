"""Predefined packages to use, if you want to use specific modules in MFF Pytex"""


from mff_pytex.utils import command


class Package:
    def __init__(self, name: str, *params: str) -> None:
        self.name = name
        self.optional = params

    def __str__(self) -> str:
        return command('usepackage', self.name, *self.optional)

# TODO Autoimport packages by used environments and commands
