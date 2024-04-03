"""Tests for source splitter languages."""

from src.source_splitter.ss_languages import SSPythonSourceFile, SSJavaScriptSourceFile


def test_sspython() -> None:
    """Test for python."""
    p = SSPythonSourceFile("src/source_splitter/ss_sourcefile.py")

    num_classes = len(p.classes)
    num_methods = len(p.methods)
    assert num_classes == 4
    assert num_methods == 15
    num_functions = len(p.functions)
    assert num_functions == 1
    assert len(p.imports) == 5
    assert len(p.comments) == num_classes + num_methods + (2 * num_functions) + 10
    assert len(p.literals) == 3


def test_bigpython():
    """Use requests.session to test."""
    p = SSPythonSourceFile("./tests/test_files/request_sessions.py")

    num_classes = len(p.classes)
    num_methods = len(p.methods)
    assert num_classes == 2
    assert num_methods == 25
    num_functions = len(p.functions)
    assert num_functions == 3
    assert len(p.subfunctions) == 0
    assert len(p.imports) == 16
    # hash comments + class docstrings  method docstrings + function docstrings + file docstring
    # __init__ and the other magic methods don't have docstrings
    assert len(p.comments) == 120 + num_classes + (num_methods - 5) + num_functions + 1

    # assert len(p.literals) == 0


def test_js():
    """Use js node.js observer to test."""
    j = SSJavaScriptSourceFile("./tests/test_files/node_js_observer.js")
    num_classes = len(j.classes)
    num_methods = len(j.methods)
    assert num_classes == 2
    assert num_methods == 13
    num_functions = len(j.functions)
    assert len(j.comments) == 19
    assert num_functions == 15
    assert len(j.literals) == 31
