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
        self.states = states
        self.alphabet = alphabet
        self.initial = initial
        self.finals = finals
        self.transitions = transitions
        
        # Validar el AFD al crearlo
        if not self.validate():
            raise ValueError("AFD inválido")

    def validate(self) -> bool:
        """Valida que el AFD sea correcto y completo."""
        try:
            # Verificar que el estado inicial esté en states
            if self.initial not in self.states:
                raise ValueError(f"Estado inicial '{self.initial}' no está en la lista de estados")
            
            # Verificar que todos los estados finales estén en states
            for final in self.finals:
                if final not in self.states:
                    raise ValueError(f"Estado final '{final}' no está en la lista de estados")
            
            # Verificar que la función de transición esté completa
            for state in self.states:
                if state not in self.transitions:
                    raise ValueError(f"Falta definir transiciones para el estado '{state}'")
                
                for symbol in self.alphabet:
                    if symbol not in self.transitions[state]:
                        raise ValueError(f"Falta transición desde '{state}' con símbolo '{symbol}'")
                    
                    next_state = self.transitions[state][symbol]
                    if next_state not in self.states:
                        raise ValueError(f"Transición desde '{state}' con '{symbol}' lleva a estado inexistente '{next_state}'")
            
            return True
            
        except ValueError:
            return False

    def simulate(self, cadena: str) -> TraceResult:
        """Simula la ejecución de una cadena en el AFD."""
        steps = []
        current_state = self.initial
        
        # Paso inicial
        steps.append(TraceStep(from_state="", to_state=current_state, symbol=None))
        
        # Procesar cada símbolo
        for symbol in cadena:
            if symbol not in self.alphabet:
                raise ValueError(f"Símbolo '{symbol}' no está en el alfabeto")
            
            from_state = current_state
            current_state = self.transitions[current_state][symbol]
            steps.append(TraceStep(from_state=from_state, to_state=current_state, symbol=symbol))
        
        # Verificar si es aceptada
        accepted = current_state in self.finals
        
        return TraceResult(accepted=accepted, final_state=current_state, steps=steps)
