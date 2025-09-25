from dataclasses import dataclass
from typing import Dict, List, Optional


"""
Representación de una traza de pasos en la simulación de un AFD.

Consiste de una lista de objetos `TraceStep` que representan cada paso
en la simulación. Cada objeto `TraceStep` tiene los siguientes campos:

* `from_state`: el estado desde el que se hace la transición
* `symbol`: el símbolo que se lee en la transición (None para el estado inicial)
* `to_state`: el estado al que se llega después de la transición

La clase `TraceResult` representa el resultado de la simulación de un AFD.
Tiene los siguientes campos:

* `accepted`: indica si la cadena es aceptada por el AFD
* `final_state`: el estado final en el que se queda después de la simulación
* `steps`: la traza de pasos que se realizaron durante la simulación
"""


@dataclass
class TraceStep:
    """Representa un paso en la simulación de un AFD."""

    from_state: str
    """El estado desde el que se hace la transición."""

    to_state: str
    """El estado al que se llega después de la transición."""
    
    symbol: Optional[str] = None
    """El símbolo que se lee en la transición (None para el estado inicial)."""



@dataclass
class TraceResult:
    """Representa el resultado de la simulación de un AFD."""

    accepted: bool
    """Indica si la cadena es aceptada por el AFD."""

    final_state: str
    """El estado final en el que se queda después de la simulación."""

    steps: List[TraceStep]
    """La traza de pasos que se realizaron durante la simulación."""


class AFD:
    def __init__(self, states: List[str], alphabet: List[str],
                 initial: str, finals: List[str],
                 transitions: Dict[str, Dict[str, str]]):
        """
        Constructor del AFD.
        :param states: Lista de estados (Q)
        :param alphabet: Lista de símbolos, alfabeto (Σ)
        :param initial: Estado inicial (q0)
        :param finals: Lista de estados de aceptación (F)
        :param transitions: Función de transición δ[state][symbol] = next_state
        """
        self.states = states
        self.alphabet = alphabet
        self.initial = initial
        self.finals = finals
        self.transitions = transitions

    def validate(self) -> bool:
        """Valida que el AFD esté bien definido."""
        # Validar que el inicial esté en los estados
        if self.initial not in self.states:
            raise ValueError(f"El estado inicial {self.initial} no está en los estados.")

        # Validar que los estados finales existan
        for f in self.finals:
            if f not in self.states:
                raise ValueError(f"El estado final {f} no está en los estados.")

        # Validar que cada estado tenga transiciones para cada símbolo
        for state in self.states:
            if state not in self.transitions:
                raise ValueError(f"El estado {state} no tiene transiciones definidas.")
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    raise ValueError(f"Falta transición de {state} con símbolo {symbol}.")
                if self.transitions[state][symbol] not in self.states:
                    raise ValueError(f"Transición inválida: {state} --{symbol}--> "
                                     f"{self.transitions[state][symbol]} no es un estado válido.")

        return True

    def simulate(self, cadena: str) -> TraceResult:
        """
        Simula la ejecución del AFD sobre una cadena.
        Devuelve si es aceptada y la traza de pasos.
        """
        current = self.initial
        steps: List[TraceStep] = [TraceStep(from_state=current, symbol=None, to_state=current)]

        for symbol in cadena:
            if symbol not in self.alphabet:
                raise ValueError(f"Símbolo '{symbol}' no está en el alfabeto {self.alphabet}.")
            next_state = self.transitions[current][symbol]
            steps.append(TraceStep(from_state=current, symbol=symbol, to_state=next_state))
            current = next_state

        accepted = current in self.finals
        return TraceResult(accepted=accepted, final_state=current, steps=steps)
