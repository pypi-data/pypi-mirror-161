"""Setup script for object_detection with TF2.0."""
import os
from setuptools import find_packages
from setuptools import setup

# Note: adding apache-beam to required packages causes conflict with
# tf-models-offical requirements. These packages request for incompatible
# oauth2client package.
REQUIRED_PACKAGES = [
    # Required for apache-beam with PY3
    # 'avro-python3',
    # 'apache-beam',
    'pillow',
    'lxml',
    'matplotlib',
    'Cython',
    'contextlib2',
    'tf-slim',
    'six',
    'pycocotools',
    'lvis',
    'scipy',
    'pandas',
    'tf-models-official'
]

setup(
    name='tf_models_research_object_detection',
    version='2.5.0.post2',
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    author='Google Inc.',
    author_email='packages@tensorflow.org',
    url='https://github.com/tensorflow/models',
    license='Apache 2.0',
    packages=(
            [p for p in find_packages() if p.startswith('object_detection')] +
            ['tf_models_research_object_detection.' + p for p in find_packages(where=os.path.join('.', 'slim'))]),
    package_dir={
        'tf_models_research_object_detection.datasets': os.path.join('slim', 'datasets'),
        'tf_models_research_object_detection.nets': os.path.join('slim', 'nets'),
        'tf_models_research_object_detection.preprocessing': os.path.join('slim', 'preprocessing'),
        'tf_models_research_object_detection.deployment': os.path.join('slim', 'deployment'),
        'tf_models_research_object_detection.scripts': os.path.join('slim', 'scripts'),
    },
    description='Ready to use tensorflow research object_detection distribution for windows and linux.',
    long_description='This is not an official package from the creators of tensorflow/models/research. '
                     'The creator of these wheels does not hold any rights to tensorflow models as well as tensorflow. '
                     'We do not give any support and are not liable for any damage caused by the use of this software. '
                     '\n'
                     'For more information about the copyright holders please visit '
                     'https://github.com/tensorflow/models/tree/master/research/object_detection',
    python_requires='>3.6',
)
