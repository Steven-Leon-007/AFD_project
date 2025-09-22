"""
Types para representar la simulación de un AFD.

Este módulo define tres tipos de datos:

1. `TransitionFunction`: un diccionario que representa la función de transición
   del AFD. La clave es el estado actual, y el valor es otro diccionario
   que tiene como clave el símbolo y como valor el estado siguiente.

2. `TraceStep`: una clase que representa un paso en la simulación del AFD.
   Tiene los siguientes campos:
   * `from_state`: el estado desde el que se hace la transición
   * `symbol`: el símbolo que se lee en la transición (None para el estado inicial)
   * `to_state`: el estado al que se llega después de la transición

3. `TraceResult`: una clase que representa el resultado de la simulación del AFD.
   Tiene los siguientes campos:
   * `accepted`: indica si la cadena es aceptada por el AFD
   * `final_state`: el estado final en el que se queda después de la simulación
   * `steps`: la traza de pasos que se realizaron durante la simulación
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# Definición del AFD en forma de diccionario
TransitionFunction = Dict[str, Dict[str, str]]

@dataclass
class TraceStep:
    """
    Representa un paso en la simulación del AFD.
    
    Tiene los siguientes campos:
    * `from_state`: el estado desde el que se hace la transición
    * `symbol`: el símbolo que se lee en la transición (None para el estado inicial)
    * `to_state`: el estado al que se llega después de la transición
    """
    from_state: str
    symbol: Optional[str]  # None para el estado inicial
    to_state: str

@dataclass
class TraceResult:
    """
    Representa el resultado de la simulación del AFD.
    
    Tiene los siguientes campos:
    * `accepted`: indica si la cadena es aceptada por el AFD
    * `final_state`: el estado final en el que se queda después de la simulación
    * `steps`: la traza de pasos que se realizaron durante la simulación
    """
    accepted: bool
    final_state: str
    steps: List[TraceStep]
