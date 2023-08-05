from setuptools import setup
import pypandoc

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='letters',
    version='2.0.1',
    license='GPLv3+',
    authors=['zelow'],
    url='https://github.com/zeloww/letters',
    install_requires=['numpy', 'pillow'],
    description='A simple method to customize your programs to infinity!',
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords=['python', 'py', 'letter', 'letters', 'font', 'ascii', 'color', 'colors', 'gradient', 'gradients', 'fade' 'text'],
    packages=['letters'],
)
