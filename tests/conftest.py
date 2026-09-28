import sys
from pathlib import Path

# Allow `pytest` to run even before `pip install -e .`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
