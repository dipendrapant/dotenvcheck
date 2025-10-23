`dotenvcheck` cross-checks the environment variables used in your Python code against those declared in your `.env` and `docker-compose.yml` files.
It reports **unused**, **missing**, and **mismatched** variables — helping you keep your environment configuration clean and consistent.

For example, if you’ve ever had a project with 20 variables in `.env` but only 10 actually used, `dotenvcheck` instantly shows you which ones can be safely removed or fixed.

---

## Installation

```bash
pip install dotenvcheck
# or
pipx install dotenvcheck

# with docker-compose support
pip install "dotenvcheck[compose]"
```

---

## Usage

From your project root (where `.env` lives):

```bash
dotenvcheck .
```

You’ll get a report listing missing, unused, or suspicious environment variables.

Example output:

```
== dotenvcheck report ==
unused (2): DATABASE_URL, NOTUSEDAPI_KEY

sources:
  API_KEY: .env
  DATABASE_URL: .env
  DEBUG: .env
  NOTUSEDAPI_KEY: .env
```

---

## Configuration (optional)

You can configure defaults globally for your project via a `[tool.dotenvcheck]` section in your `pyproject.toml`.

```toml
[tool.dotenvcheck]
exclude = [".venv", "venv", "env", ".git", "__pycache__", "dist", "build", "node_modules"]
fail_on = ["missing"]
dotenv = ".env"
include = "*.py"
```

### Options

| Key       | Type                      | Default                                                                            | Description                                                                                                          |
| --------- | ------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `exclude` | list of strings           | `[".venv", "venv", "env", ".git", "__pycache__", "dist", "build", "node_modules"]` | Directories or file patterns to ignore while scanning your code.                                                     |
| `include` | string or list of strings | `"*.py"`                                                                           | Glob pattern(s) of files to include when scanning for environment variable usage.                                    |
| `dotenv`  | string                    | `".env"`                                                                           | Path to your `.env` file used for validation.                                                                        |
| `fail_on` | list of strings           | `["missing"]`                                                                      | Determines which findings trigger a non-zero exit code. Options: `"missing"`, `"typos"`, `"bad_values"`, `"unused"`. |

---

## Behavior

- Ignores common directories like `.venv`, `dist/`, `build/`, and `.git/` by default.
- Command-line arguments always override `pyproject.toml`.
- Works seamlessly across macOS, Linux, and Windows.
- Fully supports Python 3.8 → 3.12+.

---

## Project structure

```
dotenvcheck/
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
└─ .github/
   └─ workflows/
      ├─ test.yml
      └─ workflow.yml
```

---

## License

**MIT License** – feel free to use, modify, and contribute.
