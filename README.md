# gemini_asistente (Typer)

CLI assistant para interactuar con Gemini (migrado a Typer).

## Quickstart

1. Copia `.env.example` a `.env` y añade `GEMINI_API_KEY`.
2. Instala dependencias:
   - Con Poetry (recomendado): `poetry install`
3. Ejecuta la CLI:
   - Con Poetry: `poetry run gemini --help`
   - Si instalas globalmente con pipx (ver abajo), usa `gemini`.

## Instalación global (opcional)
- Construir paquete: `poetry build`
- Instalar con pipx: `pipx install .`
  (o `pip install dist/*.whl`)

## Comandos principales
- `gemini chat new`
- `gemini chat list`
- `gemini chat load <name>`
- `gemini config role "texto..."`
- `gemini config temp 0.2`
- `gemini ask "pregunta"`

(Ver `gemini --help` para la lista completa.)
