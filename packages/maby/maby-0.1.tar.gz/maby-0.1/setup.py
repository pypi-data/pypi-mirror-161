# read the contents of README
from pathlib import Path

from setuptools import setup

directory = Path(__file__).parent
long_description = (directory / "README.md").read_text()

setup(
    name='maby',
    version='0.1',
    packages=['maby'],
    url='',
    license='MIT',
    author='Diane Adjavon',
    author_email='diane.adjavon@ed.ac.uk',
    description='U-Net for sub-cellular segmentation from Bright field',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    package_data={'maby': ['logging.conf', 'downloads.yaml']},
    include_package_data=True,
    install_requires=[
        'numpy',
        'torch',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'scikit-image',
        'pyyaml'
        ],
    entry_points={
        'console_scripts': ['maby-init=maby.__init__:initialize',
                            'maby-train=maby.train:train_main',
                            'maby-evaluate=maby.evaluate:evaluate_main',
                            'maby-visualize=maby.visualize:visualize_main']
    }
)
