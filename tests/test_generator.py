import pytest
from afd_core.afd import AFD
from afd_core.generator import generate_strings

@pytest.fixture
def afd_even_zeros():
    # AFD que acepta cadenas con número par de '0'
    states = ["q0", "q1"]
    alphabet = ["0", "1"]
    initial = "q0"
    finals = ["q0"]
    transitions = {
        "q0": {"0": "q1", "1": "q0"},
        "q1": {"0": "q0", "1": "q1"},
    }
    return AFD(states, alphabet, initial, finals, transitions)

def test_generate_basic(afd_even_zeros):
    strings = generate_strings(afd_even_zeros, limit=5)
    assert isinstance(strings, list)
    assert "" in strings  # cadena vacía aceptada porque q0 es final
    assert "11" in strings
    assert "00" in strings

def test_generate_limit(afd_even_zeros):
    strings = generate_strings(afd_even_zeros, limit=3)
    assert len(strings) == 3

def test_generate_no_accepting():
    afd = AFD(
        states=["q0"],
        alphabet=["a"],
        initial="q0",
        finals=[],  # ningún estado de aceptación
        transitions={"q0": {"a": "q0"}}
    )
    result = generate_strings(afd, limit=5)
    assert result == []
