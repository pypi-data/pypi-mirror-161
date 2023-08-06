# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'readme.md')) as f:
    long_description = f.read()


setup(
    name="UnicodeTokenizer",
    packages=find_packages(),
    version='0.0.7',
    description='UnicodeTokenizer: tokenize all Unicode text',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.0',
    url='https://github.com/laohur/UnicodeTokenizer',
    keywords=['UnicodeTokenizer', 'Tokenizer', 'Unicode','ZiTokenizer', 'ZiCutter','laohur'],
    author='laohur',
    author_email='laohur@gmail.com',
    license='[Anti-996 License](https: // github.com/996icu/996.ICU/blob/master/LICENSE)',
)

"""
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
"""
