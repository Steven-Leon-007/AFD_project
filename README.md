# Simulador de AFD: Autómatas finitos deterministas

Un simulador interactivo de Autómatas Finitos Deterministas (AFD) desarrollado en Python con interfaz gráfica moderna usando Tkinter.

## Características

- **Editor Gráfico Interactivo**: Crea y edita AFDs visualmente con arrastrar y soltar
- **Simulación Paso a Paso**: Visualiza la ejecución de cadenas con animaciones
- **Validación por Lotes**: Valida múltiples cadenas simultáneamente
- **Generación de Cadenas**: Encuentra automáticamente las primeras cadenas aceptadas
- **Persistencia**: Guarda y carga AFDs en formato JSON
- **Interfaz Moderna**: Diseño limpio y moderno con colores consistentes

## Requisitos del Sistema

- Python 3.7 o superior
- Tkinter (generalmente incluido con Python)
- pytest (para ejecutar tests)

## Instalación

1. **Clona o descarga el proyecto**:

   ```bash
   git clone https://github.com/Steven-Leon-007/AFD_project
   cd afd-simulator
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar la aplicación:

```bash
python main.py
```

## Estructura del Proyecto

```
afd-simulator/
├── afd_core/                   # Lógica principal del AFD
│   ├── __init__.py
│   ├── afd.py                  # Clase AFD y simulación
│   ├── generator.py            # Generador de cadenas aceptadas
│   ├── persistence.py          # Guardado/carga de AFDs
│   └── types.py               # Tipos de datos
├── ui/                        # Interfaz de usuario
│   ├── __init__.py
│   ├── app.py                 # Aplicación principal
│   ├── editor.py              # Editor gráfico
│   ├── simulator.py           # Simulador paso a paso
│   └── batch_validator.py     # Validador por lotes
├── tests/                     # Tests unitarios
│   ├── test_afd.py
│   ├── test_generator.py
│   └── test_persistence.py
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
└── README.md                 # Este archivo
```

## Uso de la Aplicación

### Crear un AFD

1. **Agregar Estados**:

   - Haz clic en un espacio vacío del canvas para crear un estado
   - El primer estado se marca automáticamente como inicial

2. **Marcar Estados Especiales**:

   - **Estado inicial**: Click derecho → "Marcar como inicial"
   - **Estados finales**: Click derecho → "Marcar como final"

3. **Crear Transiciones**:
   - Presiona `C` o haz clic en "Modo Conexión"
   - Haz clic en el estado origen, luego en el estado destino
   - Ingresa los símbolos de transición separados por comas

### Modos de Interacción

- **Modo Selección (`S`)**: Seleccionar y mover elementos
- **Modo Conexión (`C`)**: Crear transiciones entre estados

### Atajos de Teclado

- `S`: Cambiar a modo selección
- `C`: Cambiar a modo conexión
- `E`: Editar elemento seleccionado
- `Supr` / `Backspace`: Eliminar elemento seleccionado

### Simulación

1. **Simulación Básica**:

   - Ingresa una cadena en el campo de texto
   - Haz clic en "Simular" o presiona Enter

2. **Simulación Paso a Paso**:

   - Menú → Simulación → "Paso a paso"
   - Usa los controles de navegación para avanzar/retroceder
   - "Auto Play" ejecuta la simulación automáticamente

3. **Validación por Lotes**:
   - Menú → Simulación → "Validar múltiples cadenas"
   - Ingresa una cadena por línea
   - Haz clic en "Validar Todas"

### Persistencia

- **Guardar**: Archivo → "Guardar AFD" (formato JSON)
- **Cargar**: Archivo → "Cargar AFD"
- **Nuevo**: Archivo → "Nuevo" (limpia el canvas)

## Ejecutar Tests

El proyecto incluye tests unitarios completos. pytest está incluido en `requirements.txt`:

```bash
# Ejecutar todos los tests
python -m pytest

# Ejecutar tests con información detallada (recomendado)
python -m pytest -v

# Ejecutar tests de un módulo específico
python -m pytest tests/test_afd.py -v

# Ejecutar tests con cobertura (si tienes pytest-cov instalado)
python -m pytest --cov=afd_core tests/
```

## Ejemplos de AFDs

### AFD que acepta números impares de '1'

**Estados**: {q0, q1}  
**Alfabeto**: {0, 1}  
**Estado inicial**: q0  
**Estados finales**: {q1}  
**Transiciones**:

- q0 + 0 → q0
- q0 + 1 → q1
- q1 + 0 → q1
- q1 + 1 → q0

### AFD que acepta cadenas que terminan en "01"

**Estados**: {q0, q1, q2}  
**Alfabeto**: {0, 1}  
**Estado inicial**: q0  
**Estados finales**: {q2}  
**Transiciones**:

- q0 + 0 → q1
- q0 + 1 → q0
- q1 + 0 → q1
- q1 + 1 → q2
- q2 + 0 → q1
- q2 + 1 → q0

## Formato de Archivo JSON

Los AFDs se guardan en el siguiente formato:

```json
{
  "version": "1.0",
  "states": ["q0", "q1", "q2"],
  "alphabet": ["0", "1"],
  "initial": "q0",
  "finals": ["q2"],
  "transitions": {
    "q0": { "0": "q1", "1": "q0" },
    "q1": { "0": "q1", "1": "q2" },
    "q2": { "0": "q1", "1": "q0" }
  }
}
```

## Solución de Problemas

### Error: "AFD inválido"

- Verifica que todos los estados tengan transiciones definidas para cada símbolo del alfabeto
- Asegúrate de que existe un estado inicial
- Confirma que todos los estados referenciados en las transiciones existen

### Error: "Símbolo no está en el alfabeto"

- El alfabeto se construye automáticamente desde las transiciones
- Asegúrate de que todos los símbolos necesarios estén definidos en alguna transición

### La aplicación no inicia

- Verifica que tienes Python 3.7+ instalado: `python --version`
- Confirma que Tkinter está disponible: `python -c "import tkinter"`
- En algunas distribuciones Linux: `sudo apt-get install python3-tk`

### Tests fallan

- Asegúrate de estar en el directorio raíz del proyecto
- Verifica que pytest esté instalado: `pip install pytest`
- Los tests requieren que los módulos del core estén correctamente importables

## Características Técnicas

- **Arquitectura modular**: Separación clara entre lógica y UI
- **Validación robusta**: Verificación completa de AFDs
- **Algoritmo BFS**: Para generación eficiente de cadenas
- **Interfaz responsiva**: Canvas redimensionable y scroll automático
- **Manejo de errores**: Mensajes informativos para el usuario
- **Persistencia confiable**: Formato JSON estándar con validación

## Autores

Desarrollado por Natalia Bernal, Steven León y Mileth Martinez.
