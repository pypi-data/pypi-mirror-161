from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

REQUIRED_PKGS = [
    # TODO read from config file!?
    'spark-nlp==4.0.0',
    'nlu',
    'spark-nlp-display',
    'numpy',
    'pyarrow>=0.16.0',
    'pandas>=1.3.5',
    'dataclasses',
    'requests'
]


setup(

    name='jsl_tmp',
    version='4.0.0',
    description='John Snow Labs NLU provides state of the art algorithms for NLP&NLU with 5000+ of pretrained models in 200+ languages. It enables swift and simple development and research with its powerful Pythonic and Keras inspired API. It is powerd by John Snow Labs powerful Spark NLP library.',

    long_description=long_description,
    install_requires=REQUIRED_PKGS,

    long_description_content_type='text/markdown',
    url='https://nlu.johnsnowlabs.com',
    author='John Snow Labs',
    author_email='christian@johnsnowlabs.com',

    classifiers=[  # Optional
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='NLP spark development NLU ',

    packages=find_packages(exclude=['test*', 'tmp*']),  # exclude=['test']

    include_package_data=True  # Needed to install jar file

)