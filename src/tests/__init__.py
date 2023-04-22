import os
import sys
from pathlib import Path

# env vars needed to run tests
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['DB_URL'] = 'sqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret'

# src dir must be on sys.path to run tests from cli
src_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(src_dir))
