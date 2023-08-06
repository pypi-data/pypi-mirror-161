"""Tables and lists utilities and support for pandas dataframe."""

from typing import Any, Optional, Union
from collections.abc import Sequence
from mff_pytex.utils import command, Environment
from mff_pytex.exeptions import WrongTypeListError
from pandas import DataFrame


class Table:
    """Table structure. Converts pandas' dataframe to TeX table.
    Note:
        Requires booktabs package to import, add with autopackage management.

    Attributes:
        df (DataFrame): Dataframe containing table.
        styles: Contains parameters for to_latex method of DataFrame. More info in pandas docs.

    """

    def __init__(self, dataframe: DataFrame, **styles: Any) -> None:
        """Initialize Table.

        Args:
            df (DataFrame): Dataframe containing table.
            **styles (Any): Parameters for to_latex method of DataFrame.
        """
        self.df = dataframe
        self.styles = styles

    def __str__(self) -> str:
        return self.df.to_latex(**self.styles)


class List(Environment):
    """List structure. Convert python lists to TeX lists."""

    def __init__(self, arr: Union[Sequence, dict], en_type: str = 'itemize') -> None:
        """Initialize List.

        Args:
            arr (Sequence | Dict): Sequence which is iterated. Only dictionary is compactible with 'descrition'.
            en_type (str): Type of list
        """
        self.en_type = en_type
        if self.en_type == 'description' and not isinstance(arr, dict):
            WrongTypeListError()
        self.write(command('begin', self.en_type))
        self.items(arr)

    def item(self, content: str, label: Optional[str] = None):
        """Add one item in content.

        Args:
            content (str): Main text.
            label (str): Label of item.
        """
        if label is None:
            self.write(f'\\item {content}')
        else:
            self.write(f'\\item[{label}] {content}')

    def items(self, arr: Union[Sequence, dict]) -> None:
        """Includes given Sequence of dictionary in content.

        Args:
            arr (Sequence | Dict): Sequence which is iterated. Only dictionary is compactible with 'descrition'.
            en_type (str): Type of list
        """
        if self.en_type == 'description' and not isinstance(arr, dict):
            WrongTypeListError()

        if isinstance(arr, dict):
            for key, value in arr.items():
                self.item(str(value), str(key))
        else:
            for item in arr:
                self.item(str(item))


class NestedList(List):
    # TODO all
    pass
