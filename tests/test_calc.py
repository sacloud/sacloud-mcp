import pytest
from src.py_template.calc import add

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
