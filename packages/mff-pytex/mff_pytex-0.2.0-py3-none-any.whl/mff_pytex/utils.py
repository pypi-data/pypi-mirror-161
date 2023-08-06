"""Basic utils for work with LaTeX documents."""


from datetime import date as datum
from typing import Any, Optional
import sys
from os import path


def get_dir() -> str:
    """Returns directory where main file has been executed.

    Returns:
        str: Directory name where is main file
    """
    return str(path.dirname(str(sys.modules['__main__'].__file__)))


def get_path() -> str:
    """Returns path to main file.

    Returns:
        str: Path to main file
    """
    return str(path.abspath(str(sys.modules['__main__'].__file__)))


def command(comm: str, main: Optional[str] = None, *params) -> str:
    """Template for creating commands.

    If main is None, than return '\\command'.
    If main is not none, but any optional parameter given, than return '\\command{main}'
    If main and optional parameters given, than return '\\command[param1, param2, ...]{main}'

    Args:
        comm (str): Name of command
        main (str): Main parameter of command, defaults None
        *params (str): Optional parameters of command

    Returns:
        str: string of given command by given parameters.
    """
    if main is None:
        return f"\\{comm}"
    elif params:
        return f"\\{comm}[{', '.join(params)}]{{{main}}}"
    else:
        return f"\\{comm}{{{main}}}"


def doublecommand(comm: str, main: str, second: Optional[str], opt: bool = False) -> str:
    """Template for creating doublecommands.

    Commands lokks like this \\comm{main} {second}

    Args:
        comm (str): Name of command
        main (str): First parameter
        second (str): Second parameter
        opt (bool): Set if the second parameter is optional

    Returns:
        str: string of given command by given parameters.
    """
    if second is None:
        return f"\\{comm}{{{main}}}"
    elif opt:
        return f"\\{comm}{{{main}}} [{second}]"
    else:
        return f"\\{comm}{{{main}}} {{{second}}}"


class TemplateProperty:
    """Abstract descriptor class.

    Example:
        class Example:
            attr = TemplateProperty()

    Attributes:
        public_name (str): public name of attribute.
        protected_name (str): protected name of attribute.
    """
    def __set_name__(self, owner, name: str) -> None:
        """Initialize given attribute by name.

        Args:
            owner: Class with given attribute.
            name (str): Name of attribute.
        """
        self.public_name = name
        self.private_name = f'_{name}'

class PreambleProperty(TemplateProperty):
    """Template for preamble attribute properties.

        Example:
            class Example:
                attr = PreambleProperty()

            obj = Example()
            obj.attr = 'name' # set attr as 'name' string

            print(obj.attr) # return attribute as TeX command string.
        """

    def __get__(self, obj, objtype=None) -> Optional[str]:
        """Getter template.

        Args:
            obj: Object that use this template for given property.
            objtype: type of object.

        Returns:
            str: String in form of TeX command for this attribute.
        """
        value = getattr(obj, self.private_name)
        return command(self.public_name, str(value)) if value is not None else None

    def __set__(self, obj, value) -> None:
        """Setter template.

        Args:
            obj: Object that use this template for given property.
            value: New value of attribute.
        """
        setattr(obj, self.private_name, value)
