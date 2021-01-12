import os

from dotenv import load_dotenv

load_dotenv()

SKLIK_TEST_TOKEN = os.environ.get("SKLIK_TEST_TOKEN", None)
