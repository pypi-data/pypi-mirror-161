"""Default models and images for the maby package."""
import logging.config
import urllib.request
from importlib.resources import path
from pathlib import Path

import yaml

with path("maby", "logging.conf") as f:
    logging.config.fileConfig(f)


def initialize():
    """Initialize tha package, downloading data and models."""
    directory = Path(__file__).parent.absolute()
    # Get the location of the files to download
    with open(directory / 'downloads.yaml') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    # Make an examples folder
    examples_dir = directory / 'examples'
    if not examples_dir.exists():
        examples_dir.mkdir()
        # Download example files
        for filename, url in config['examples'].items():
            urllib.request.urlretrieve(url,
                                       filename=str(examples_dir / filename))
    # Make a models folder
    models_dir = directory / 'models'
    if not models_dir.exists():
        models_dir.mkdir()
        # Download models
        for filename, url in config['models'].items():
            urllib.request.urlretrieve(url,
                                       filename=str(models_dir / filename))


if __name__ == "__main__":
    initialize()
