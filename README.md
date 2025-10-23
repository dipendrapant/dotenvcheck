This project cross-check environment variables used in your Python code against declarations in `.env` and `docker-compose.yml`. And gives the report showing the list of unused environment variable. It is a great package at least i was waiting for a long time.

## Install

````bash
pipx install envguard
# or
pip install envguard
# docker-compose extras:
pip install "envguard[compose]"

## Project
```
envguard/
├─ src/
│  └─ envguard/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ scanner.py
│     ├─ dotenv.py
│     ├─ compose.py
│     └─ report.py
├─ tests/
├─ pyproject.toml
├─ LICENSE
├─ README.md
├─ .gitignore
└─ .github/
   └─ workflows/
      └─ test.yml
```

## Configuration

`envguard` can be configured globally for your project using a `[tool.envguard]` section in your `pyproject.toml`.

### Example, Optional project-wide configuration
```toml
[tool.envguard]
exclude = [".venv", "venv", "env", ".git", "__pycache__", "dist", "build", "node_modules"]
fail_on = ["missing"]
dotenv = ".env"
include = "*.py"
````

### Options

| Key       | Type                      | Default                                                                            | Description                                                                                                                                                                                       |
| --------- | ------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exclude` | list of strings           | `[".venv", "venv", "env", ".git", "__pycache__", "dist", "build", "node_modules"]` | Directories or file patterns to ignore while scanning your code.                                                                                                                                  |
| `include` | string or list of strings | `"*.py"`                                                                           | Glob pattern(s) of files to include when scanning for environment variable usage.                                                                                                                 |
| `dotenv`  | string                    | `".env"`                                                                           | Path to your `.env` file used for validation.                                                                                                                                                     |
| `fail_on` | list of strings           | `["missing"]`                                                                      | Defines which issues should cause a non-zero exit code. Possible values: `"missing"` (variable used in code but not declared), `typos`,`bad_values`, `"unused"` (variable declared but not used). |

### Behavior

- By default, `envguard` ignores common virtual environments, build directories, and version control folders.
- You can override any of these defaults in your `pyproject.toml` to fit your project structure.
- Command-line arguments override `pyproject.toml` only when explicitly provided.
