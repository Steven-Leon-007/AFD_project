import pytest
from afd_core.afd import AFD
from afd_core.types import TraceResult

@pytest.fixture
def simple_afd():
    # AFD que acepta cadenas con un número impar de '1'
    states = ["q0", "q1"]
    alphabet = ["0", "1"]
    initial = "q0"
    finals = ["q1"]
    transitions = {
        "q0": {"0": "q0", "1": "q1"},
        "q1": {"0": "q1", "1": "q0"},
    }
    return AFD(states, alphabet, initial, finals, transitions)

def test_validate_valid(simple_afd):
    assert simple_afd.validate() is True

def test_validate_invalid_initial():
    with pytest.raises(ValueError, match="AFD inválido"):
        AFD(["q0"], ["a"], "qX", ["q0"], {"q0": {"a": "q0"}})

def test_simulate_accept(simple_afd):
    result: TraceResult = simple_afd.simulate("1")
    assert result.accepted is True
    assert result.final_state == "q1"

def test_simulate_reject(simple_afd):
    result: TraceResult = simple_afd.simulate("11")
    assert result.accepted is False
    assert result.final_state == "q0"

def test_simulate_invalid_symbol(simple_afd):
    with pytest.raises(ValueError):
        simple_afd.simulate("2")
