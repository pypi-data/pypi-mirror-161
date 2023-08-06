from setuptools import setup, find_packages

install_requires = [
    "opencv-python",
    "Pillow",
    "tensorflow",
    "tensorflow_hub",
    "numpy"
]

setup(
    name='elekiban',
    version='0.0.0',
    url="https://github.com/DameNianch/elekiban",
    author="DameNianch",
    license="Check https://github.com/DameNianch/elekiban",
    packages=find_packages(),
    install_requires=install_requires
)
