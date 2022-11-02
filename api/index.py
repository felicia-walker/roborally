# This is for Vercel deployment
import os

base_dir: str = os.path.abspath(os.path.dirname(__file__))
db_dir: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src")

from ui.wsgi import app