# afd_core/afd.py
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TraceStep:
    from_state: str
    symbol: Optional[str]  # None para el estado inicial
    to_state: str


@dataclass
class TraceResult:
    accepted: bool
    final_state: str
    steps: List[TraceStep]


class AFD:
    def __init__(self, states: List[str], alphabet: List[str],
                 initial: str, finals: List[str],
                 transitions: Dict[str, Dict[str, str]]):
        """
        Constructor del AFD.
        :param states: Lista de estados (Q)
        :param alphabet: Lista de símbolos (Σ)
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
