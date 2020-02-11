# Application entry point

from pantry_raid.config import Config
from pantry_raid import create_app


app = create_app(Config)
