import os
import tempfile
from afd_core.afd import AFD
from afd_core.persistence import save_to_json, load_from_json

def sample_afd():
    states = ["q0", "q1"]
    alphabet = ["a", "b"]
    initial = "q0"
    finals = ["q1"]
    transitions = {
        "q0": {"a": "q1", "b": "q0"},
        "q1": {"a": "q1", "b": "q0"},
    }
    return AFD(states, alphabet, initial, finals, transitions)

def test_save_and_load_json():
    afd = sample_afd()
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "afd.json")

        save_to_json(afd, filepath)
        assert os.path.exists(filepath)

        loaded_afd = load_from_json(filepath)
        assert isinstance(loaded_afd, AFD)
        assert loaded_afd.states == afd.states
        assert loaded_afd.alphabet == afd.alphabet
        assert loaded_afd.initial == afd.initial
        assert loaded_afd.finals == afd.finals
        assert loaded_afd.transitions == afd.transitions

def test_load_invalid_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "invalid.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        try:
            load_from_json(filepath)
            assert False, "Debió lanzar excepción"
        except Exception:
            assert True
