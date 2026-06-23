# Developer Guide & Guidelines (v7.0)

## Environment Setup
1. Clone the repository.
2. Install Python 3.11+.
3. Install package dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Code
- **PySide6 Desktop Application**: `python main.py`
- **FastAPI Endpoint Service**: `python src/api/app.py`

## Linter & Formatting Standards
The codebase adheres to `ruff` and `black` rules:
- **Run Black Formatter Check**:
  ```bash
  black --check src/ tests/
  ```
- **Run Ruff Linter**:
  ```bash
  ruff check src/ tests/
  ```

## Running Automated Tests
We use `pytest` for validation and `pytest-cov` to measure code coverage:
```bash
pytest --cov=src --cov-report=term-missing tests/
```

## Compilation & Executables
To generate a standalone Windows executable:
```bash
pyinstaller --onefile --windowed --name="WarframeTacticalAdvisor" src/gui/main_window.py
```
This outputs `WarframeTacticalAdvisor.exe` inside the `dist/` folder.
To generate a Windows setup installer package, install Inno Setup and run the compiler script:
```bash
iscc installer/setup.iss
```
This produces `Warframe Tactical Advisor Setup.exe` inside the `dist/` directory.
