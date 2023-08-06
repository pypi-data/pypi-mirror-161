"""Utilities for bibliography."""

from typing import Optional
from dataclasses import dataclass
from mff_pytex.utils import File

@dataclass
class Bib:
    """Abstract class for bibliography

    Attributes:
        name: intern name of given bibliography
    """
    name: str

    def __str__(self) -> str:
        """Generate a record of given bibliography

        Returns:
            str: Bib record
        """
        text = '@' + self.__class__.__name__.lower() + '{'
        for field in self.__dataclass_fields__:
            if getattr(self, field) is not None:
                if field == 'name':
                    text += f"{getattr(self, field)},\n"
                elif field == 'typ':
                    text += f"  {field}e = \"{str(getattr(self, field))}\" ,\n"
                else:
                    text += f"  {field} = \"{str(getattr(self, field))}\" ,\n"
        return text + '}'


@dataclass
class Article(Bib):
    """An article from a magazine or a journal.

    Attributes:
        title (str)
        year (int)
        author (str)
        journal (str)
        month (str, optional)
        note: (str, optional)
        number: (str, optional)
        pages: (str, optional)
        volume: (str, optional)
    """
    title: str
    year: int
    author: str
    journal: str
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    pages: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class Book(Bib):
    """A published book

    Attributes:
        title (str)
        year (int)
        author (str)
        publisher (str)
        address (str, optional)
        edition (str, optional)
        editor (str, optional)
        month (str, optional)
        note (str, optional)
        number (int, optional)
        series (str, optional)
        volume (str, optional)
    """
    title: str
    year: int
    author: str
    publisher: str
    address: Optional[str] = None
    edition: Optional[str] = None
    editor: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    series: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class Booklet(Bib):
    """A bound work without a named publisher or sponsor.

    Attributes:
        title (str)
        author (str, optional)
        howpublished (str, optional)
        year (int, optional)
        month (str, optional)
        note (str, optional)
    """
    title: str
    author: Optional[str] = None
    howpublished: Optional[str] = None
    year: Optional[int] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Conference(Bib):
    """Equal to inproceedings

    Attributes:
        author (str)
        title (str)
        booktitle (str)
        year (int)
        editor (str, optional)
        number (int, optional)
        volume (str, optional)
        series (str, optional)
        address (str, optional)
        page (str, optional)
        month (str, optional)
        organization (str, optional)
        publisher (str, optional)
        note (str, optional)
    """
    author: str
    title: str
    booktitle: str
    year: int
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    address: Optional[str] = None
    page: Optional[str] = None
    month: Optional[str] = None
    organization: Optional[str] = None
    publisher: Optional[str] = None
    note: Optional[str] = None


@dataclass
class InBook(Bib):
    """A section of a book without its own title.

    Attributes:
        title (str)
        year (int)
        author (str)
        publisher (str)
        pages (str)
        chapter (str, optional)
        address (str, optional)
        edition (str, optional)
        editor (str, optional)
        month (str, optional)
        note (str, optional)
        number (int, optional)
        series (str, optional)
        volume (str, optional)
    """
    title: str
    year: int
    author: str
    publisher: str
    pages: str
    chapter: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    editor: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None
    number: Optional[int] = None
    series: Optional[str] = None
    volume: Optional[str] = None


@dataclass
class InCollection(Bib):
    """A section of a book having its own title.

    Attributes:
        author (str)
        title (str)
        booktitle (str)
        year (int)
        publisher (str)
        editor (str, optional)
        number (int, optional)
        volume (str, optional)
        series (str, optional)
        typ (str, optional)
        chapter (str, optional)
        pages (str, optional)
        address (str, optional)
        edition (str, optional)
        month (str, optional)
        note (str, optional)
    """
    author: str
    title: str
    booktitle: str
    year: int
    publisher: str
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    typ: Optional[str] = None
    chapter: Optional[str] = None
    pages: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


class InProceedings(Conference):
    """An article in a conference proceedings.

    Attributes:
        author (str)
        title (str)
        booktitle (str)
        year (int)
        editor (str, optional)
        number (int, optional)
        volume (str, optional)
        series (str, optional)
        address (str, optional)
        page (str, optional)
        month (str, optional)
        organization (str, optional)
        publisher (str, optional)
        note (str, optional)
    """
    pass


@dataclass
class Manual(Bib):
    """Technical manual

    Attributes:
        title (str)
        author (str, optional)
        organization (str, optional)
        address (str, optional)
        edition (str, optional)
        month (str, optional)
        year (int, optional)
        note (str, optional)
    """
    title: str
    author: Optional[str] = None
    organization: Optional[str] = None
    address: Optional[str] = None
    edition: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    note: Optional[str] = None


@dataclass
class MasterThesis(Bib):
    """Master's thesis

    Attributes:
        author (str)
        title (str)
        school (str)
        year (int)
        typ (str, optional)
        address (str, optional)
        month (str, optional)
        note (str, optional)
    """
    author: str
    title: str
    school: str
    year: int
    typ: Optional[str] = None
    address: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Misc(Bib):
    """Template useful for other kinds of publication

    Attributes:
        author (str, optional)
        title (str, optional)
        howpublished (str, optional)
        month (str, optional)
        year (int, optional)
        note (str, optional)
    """
    author: Optional[str] = None
    title: Optional[str] = None
    howpublished: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    note: Optional[str] = None


class PhdThesis(MasterThesis):
    """Ph.D. thesis

    Attributes:
        author (str)
        title (str)
        school (str)
        year (int)
        typ (str, optional)
        address (str, optional)
        month (str, optional)
        note (str, optional)
    """
    pass


@dataclass
class Proceedings(Bib):
    """The proceedings of a conference.

    Attributes:
        title (str)
        year (int)
        editor (str, optional)
        number (int, optional)
        volume (str, optional)
        series (str, optional)
        address (str, optional)
        month (str, optional)
        organization (str, optional)
        publisher (str, optional)
        note (str, optional)
    """
    title: str
    year: int
    editor: Optional[str] = None
    number: Optional[int] = None
    volume: Optional[str] = None
    series: Optional[str] = None
    address: Optional[str] = None
    month: Optional[str] = None
    organization: Optional[str] = None
    publisher: Optional[str] = None
    note: Optional[str] = None


@dataclass
class TechReport(Bib):
    """Technical report from educational, commercial or standardization institution.

    Attributes:
        author (str)
        title (str)
        institution (str)
        year (int)
        typ (str, optional)
        number (int, optional)
        address (str, optional)
        month (str, optional)
        note (str, optional)
    """
    author: str
    title: str
    institution: str
    year: int
    typ: Optional[str] = None
    number: Optional[int] = None
    address: Optional[str] = None
    month: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Unpublished(Bib):
    """An unpublished article, book, thesis, etc.

    Attributes:
        author (str)
        title (str)
        note (str)
        month (str, optional)
        year (int, optional)
    """
    author: str
    title: str
    note: str
    month: Optional[str] = None
    year: Optional[int] = None


class Bibliography(File):
    """Bib file

    Attributes:
        bib_list (list[Bib]): bibliography list.
    """
    file_type = 'bib'
    bib_list: list[Bib] = []

    def create(self, mode: str = 'w+') -> None:
        bib = open(self.file_path, mode)
        bib.write(*map(str, self.bib_list))
        bib.close()
