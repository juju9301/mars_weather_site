# Mars Weather Site

This is a Django-based web app I built to explore Playwright automation while incorporating some fun Mars-related data. 🚀

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Managing dependencies](#managing-dependencies)
- [Usage](#usage)
- [Running tests](#running-tests)
- [License](#license)

## Features
- 🌌 **Mars Weather Dashboard** – Displays the latest imported REMS weather, using calibrated products from the NASA Planetary Data System.
- 📈 **Temperature Graphs** – Uses matplotlib to visualize min, max, and avg temperatures.
- 📝 **Basic Blog System** – Users can authenticate, compose posts, and attach a random Mars rover image to their entries.
- 🧪 **Automated Testing** – Pytest + Playwright tests, with reports generated via pytest-cov and pytest-html. Include basic tests, tests using overwritten request query parameters, overwritten response body, image text recognition
- 🔄 **CI/CD Integration** – Configured with CircleCI for automated testing.
- 🚀 **Live Deployment** – Hosted on PythonAnywhere (currently inactive due to becoming too large for free tier).

## Installation

**Requirements:** Python 3.13–3.14 with Django 5.2 LTS. CI targets Python 3.13, which is available on PythonAnywhere's newer `innit` system image. Select manual configuration and install this project's dependencies in a virtualenv rather than relying on PythonAnywhere's bundled Django version.

1. Clone the repository:
    ```bash
    git clone https://github.com/juju9301/mars_weather_site.git
    cd mars_weather_site
    ```
2. Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
    On Windows, `py -3.13 -m venv .venv` creates the deployment-compatible environment.
3. Install the dependencies:
    ```bash
    # Running the app only (what production uses)
    pip install -r requirements.txt

    # Development: app + test tooling
    pip install -r requirements.txt -r requirements-dev.txt
    playwright install chromium
    ```
4. Run the migrations:
    ```bash
    cd src
    python manage.py migrate
    ```
5. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Managing dependencies

Dependencies are managed with [pip-tools](https://github.com/jazzband/pip-tools). Each `.in` file lists only the packages we use directly, and the compiled `.txt` file pins every package (including transitive ones) to an exact version. **Edit the `.in` files, never the `.txt` files by hand.**

| File | Purpose | Installed in |
|------|---------|--------------|
| `requirements.in` / `requirements.txt` | Runtime dependencies of the app | Production, CI, development |
| `requirements-dev.in` / `requirements-dev.txt` | Testing and tooling (pytest, pytest-django, Playwright, Faker, pip-tools, pip-audit) | CI, development |
| `requirements-experiments.in` / `requirements-experiments.txt` | Heavy, optional packages for experiments (easyocr, torch) | Only when running the experimental tests |

The dev and experiments files start with `-c requirements.txt` (and the experiments file also with `-c requirements-dev.txt`). These are *constraint* lines: they make sure a package shared between files resolves to the same version everywhere, without installing the other file's packages.

### Adding or removing a package
1. Add or remove it in the right `.in` file.
2. Recompile that file and every file that depends on it (runtime → dev → experiments):
    ```bash
    python -m piptools compile requirements.in -o requirements.txt --pip-args "--only-binary=:all:"
    python -m piptools compile requirements-dev.in -o requirements-dev.txt --pip-args "--only-binary=:all:"
    ```
3. Sync your environment and run the tests:
    ```bash
    pip-sync requirements.txt requirements-dev.txt
    pytest
    ```
4. Commit both the `.in` and the compiled `.txt` files.

### Upgrading all dependencies
Compile in the same order, adding `--upgrade`:
```bash
python -m piptools compile --upgrade requirements.in -o requirements.txt --pip-args "--only-binary=:all:"
python -m piptools compile --upgrade requirements-dev.in -o requirements-dev.txt --pip-args "--only-binary=:all:"
pip-sync requirements.txt requirements-dev.txt
pytest
```
Then check for known vulnerabilities in what ships:
```bash
pip-audit -r requirements.txt
```
Review `git diff` of the `.txt` files and skim the release notes for major version bumps (especially Django).

### Experimental dependencies
The commented-out tests that use `easyocr` / `torch` need the experiments file:
```bash
python -m piptools compile requirements-experiments.in -o requirements-experiments.txt --pip-args "--only-binary=:all:"
pip install -r requirements-experiments.txt
```
`torch` is large and sometimes lags behind the newest Python release. Note that `pip-sync requirements.txt requirements-dev.txt` **uninstalls** these packages; to keep them, list all three files:
```bash
pip-sync requirements.txt requirements-dev.txt requirements-experiments.txt
```

### Troubleshooting
- **pip tries to compile a package from source** (Meson / "Unknown compiler" errors): the pinned version has no prebuilt wheel for your Python. Recompile with `--upgrade` and `--only-binary=:all:`, or use a Python version the package supports.
- **`No matching distribution found` for a pinned version**: you are probably using a different Python than the one the lockfile was compiled with. Check `python --version` against the header of `requirements.txt`.
- **`-c requirements.txt` is not recognized as a command**: that line belongs inside a `.in` file, not in the terminal.

## Usage
- **Mars Weather Dashboard**: Navigate to `/` to see the weather data for the latest sol available, as well as NASA's picture of the day and the posts submitted so far
- **Mars Weather Data**: Navigate to `/list` to see all the weather data available. New sols are imported from downloaded REMS products with the management command described below.
- **Temperature Graphs**: Access the temperature graphs at `/plot`. You can plot data for max, min and avg temperature. 
- **Blog System**: Authenticate and start creating blog posts at `/add_post`. You can fetch a random Mars picture taken by one of the three Mars rovers and attach it to the post. You can also leave comments for each post.

### Importing REMS data

Place each sol's calibrated RMD and ADR products (the `.TAB`, `.xml`, and `.LBL` files) under `data/sols/<sol>/`. The local `data/` directory is ignored by Git. From `src`, generate a one-record Django fixture and load it:

```bash
python manage.py migrate
python manage.py export_rems_fixture --sol 4843
python manage.py loaddata weather_sol_4843
```

The parser checks its column definitions and record counts against the PDS XML labels. It derives sunrise and sunset from the ADR solar-zenith crossings. Values that aren't directly available are left unset rather than guessed: in particular, the ADR field named `SOLAR_LONGITUDE_ANGLE` is rover-relative solar azimuth, not Mars solar longitude (`ls`). The generated fixture is written to `weather/fixtures/weather_sol_<sol>.json`.

## Running tests
Install the dev dependencies (see [Installation](#installation)), start the dev server, and run pytest from `src`:
```bash
cd src
python manage.py runserver        # in a separate terminal
pytest
```
CircleCI runs the same steps on every push: it installs `requirements.txt` and `requirements-dev.txt`, audits the runtime dependencies with `pip-audit`, runs the migrations, loads the fixtures, and executes the Playwright tests. The experiments file is not installed in CI.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
