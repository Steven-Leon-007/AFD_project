# afd_core/generator.py
from collections import deque
from typing import List
from .afd import AFD


def generate_strings(afd: AFD, limit: int = 10, max_length: int = 20) -> List[str]:
    """
    Genera las primeras 'limit' cadenas aceptadas por el AFD,
    ordenadas por longitud (usando BFS).
    
    :param afd: instancia de AFD ya validada
    :param limit: número máximo de cadenas a devolver
    :param max_length: límite de longitud para evitar loops infinitos
    :return: lista de cadenas aceptadas
    """
    afd.validate()

    results: List[str] = []
    queue = deque()
    visited = set()

    # Nodo inicial: (estado_actual, cadena_construida)
    queue.append((afd.initial, ""))

    while queue and len(results) < limit:
        state, string = queue.popleft()

        # Si es estado final (y no es cadena vacía) → aceptar
        if state in afd.finals and string not in results:
            results.append(string)
            if len(results) >= limit:
                break

        # Expandir solo hasta max_length
        if len(string) < max_length:
            for symbol in afd.alphabet:
                next_state = afd.transitions[state][symbol]
                new_string = string + symbol
                # Usamos visited para no explotar en autómatas con ciclos
                if (next_state, new_string) not in visited:
                    visited.add((next_state, new_string))
                    queue.append((next_state, new_string))

    return results
