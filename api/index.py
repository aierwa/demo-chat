import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))
os.chdir(str(Path(__file__).parent / "backend"))

os.environ.setdefault("VECTOR_STORE_TYPE", "chroma")

from app.main import app
