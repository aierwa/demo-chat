import os
import sys
from pathlib import Path

# 获取项目根目录（api目录的父目录）
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.insert(0, str(BACKEND_DIR))
os.chdir(str(BACKEND_DIR))

os.environ.setdefault("VECTOR_STORE_TYPE", "chroma")

from app.main import app
