import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root so DATABASE_URL can be defined there.
dotenv_path = Path(__file__).resolve().parents[1] / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./phindu.db')
