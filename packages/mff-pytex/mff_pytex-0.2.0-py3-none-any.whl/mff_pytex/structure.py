"""Module containing basic structure of file."""

from datetime import date as datum
from typing import Optional
from typing_extensions import Self
from mff_pytex.utils import command, get_dir, PreambleProperty
import os

# TODO importing and another document structuring


class Preamble:
    """Preamble contains basic info about author and document.
    """

    title = PreambleProperty()
    author = PreambleProperty()
    date = PreambleProperty()

    def __init__(self,
                 title: Optional[str] = None,
                 author: Optional[str] = None,
                 date: Optional[datum] = None,
                 packages: list = []) -> None:
        """Initialize Preamble

        Args:
            title (str): Title of document, defaults None
            author (str): Author's name, defaults None
            date (date): Date of creation of document, defaults None
            packages (list[Package]): packages to use, defaults []
        """
        self.title = title
        self.author = author
        self.date = date
        self.packages = packages

    @property
    def packages(self) -> Optional[str]:
        text = Writing()
        for package in self._packages:
            text.write(str(package))
        return str(text)

    @packages.setter
    def packages(self, packages: list) -> None:
        self._packages = packages

    def __str__(self) -> str:
        """Returns Preamble as string in TeX form.

        Returns:
            str: Preamble in TeX form.
        """
        text = Writing()
        if self.packages != "":
            text.write(self.packages)
        text.write('')
        text.write(self.title)
        text.write(self.author)
        text.write(str(self.date))
        return str(text)


class Writing:
    _text = ""

    def __str__(self) -> str:
        return self._text

    def _writeline(self, text: str) -> None:
        """Write single line to the TeX file.

        Args:
            text (str): Line of text intended for insert to content.
        """
        self._text += f"{text}\n"

    def write(self, *lines: Optional[str]) -> None:
        """Write multiple lines to the TeX file.

        Args:
            *lines (str): Lines of text intended for insert to content.
        """
        for line in lines:
            if line is not None:
                self._writeline(line)

    def add(self, environment: Self) -> None:
        """Writes environment to the TeX file.

        Args:
            environment (Any): Figure to use.
        """
        self.write(str(environment))


class Environment(Writing):
    """Basic environment structure.

    Attributes:
        en_type (str): Type of environment
        _text (str): Content of environment,
    """

    def __init__(self, en_type: str, *params: str) -> None:
        """Initialize Environment.

        Args:
            en_type (str): Type of environment
            *params (str): Optional parameters for environment
        """
        self.en_type = en_type
        if params:
            self.write(command('begin', self.en_type, *params))
        else:
            self.write(command('begin', self.en_type))

    def __str__(self) -> str:
        """Returns content string encapsuled by environment.

        Returns:
            str: Content
        """
        return self._text + command('end', self.en_type) + '\n'

    def math(self, formula: str) -> None:
        self.write(f"\\[ {formula} \\]")


class Document(Environment):
    """Content of document."""

    def __init__(self) -> None:
        """Initialize document.
        """
        self._text = ""
        self.en_type = "document"
        self.write(command('begin', self.en_type))

    def tableofcontents(self) -> None:
        """Add a tableofcontents command to the TeX file."""
        self.write(command('tableofcontents'))

    def maketitle(self) -> None:
        """Add a maketitle command to the TeX file."""
        self.write(command('maketitle'))

    def newpage(self) -> None:
        """Add a newpage command to the TeX file."""
        self.write(command('newpage'))

    def clearpage(self) -> None:
        """Add a clearpage command to the TeX file."""
        self.write(command('clearpage'))


class TexFile:
    """Basic TeX file structure.

    Attributes:
        file_path (str): Path to initialized file.
        body (Body): Body of a file.
    """

    preamble = Preamble()
    document = Document()

    def __init__(self, file_name: str) -> None:
        """Initialize TexFile

        Args:
            file_name str: Name of file which will be created.
        """

        self.file_path = f"{get_dir()}/{file_name}.tex"

    def create(self, mode: str = 'w+') -> None:
        """Creates file and writes its content.

        Args:
            mode (str): mode of given file. Same as open() function.
        """
        tex = open(self.file_path, mode)
        tex.write(str(self.preamble))
        tex.write(str(self.document))
        tex.close()

    def make_pdf(self, mode: str = 'r') -> None:
        """Creates pdf file, if neccessary writes its content and create pdf document.

        Args:
            mode (str): mode of given file. Same as open() function.
        """
        if mode not in ['r']:
            self.create(mode)
        os.system(f"pdflatex {self.file_path}")
