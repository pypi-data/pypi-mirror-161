#!/usr/bin/env python

"""Tests for `mff_pytex` package."""

import pytest
from src.mff_pytex.utils import command


# def test_document():
#     figure = structure.Document()
#     figure.clearpage()
#     f = open('tests/temp2.tex', 'w')
#     f.write(str(figure))
#     f.close()
#     assert cmp('tests/temp2.tex', 'tests/temp.tex')

def test_command_makefile():
    """Test if command makefile works properly"""
    assert command('makefile') == "\\makefile"

def test_command_begin_document():
    """Test if command begin works properly"""
    assert command('begin', 'document') == "\\begin{document}"

def test_command_usepackage():
    """Test if command usepackage properly"""
    assert command('usepackage', 'inputenc', 'utf8') == "\\usepackage[utf8]{inputenc}"
