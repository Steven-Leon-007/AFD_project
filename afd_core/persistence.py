# afd_core/persistence.py
import json
from typing import Dict, Any
from .afd import AFD


def save_to_json(afd: AFD, filepath: str) -> None:
    """
    Guarda un AFD en un archivo JSON.
    
    :param afd: instancia de AFD
    :param filepath: ruta del archivo destino
    """
    data = {
        "version": "1.0",
        "states": afd.states,
        "alphabet": afd.alphabet,
        "initial": afd.initial,
        "finals": afd.finals,
        "transitions": afd.transitions
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_from_json(filepath: str) -> AFD:
    """
    Carga un AFD desde un archivo JSON.
    
    :param filepath: ruta del archivo origen
    :return: instancia de AFD
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)

    afd = AFD(
        states=data["states"],
        alphabet=data["alphabet"],
        initial=data["initial"],
        finals=data["finals"],
        transitions=data["transitions"]
    )
    afd.validate()  # Validamos el AFD cargado
    return afd
