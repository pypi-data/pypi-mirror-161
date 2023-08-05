from setuptools import setup, find_packages
from os.path import abspath, dirname, join

README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

setup(
    name="word_image",
    version="0.1.1",
    license="MIT",
    packages=find_packages(),
    description="Generate images of words with configurable augmentation options",
    long_description=README_MD,
    long_description_content_type="text/markdown",
    url="https://github.com/econser/word_image",
    download_url="https://github.com/econser/word_image/archive/refs/tags/v_01_1.tar.gz",
    install_requires=['numpy', 'imgaug', 'Pillow', 'matplotlib'],
    author="econser",
    author_email="econser@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3 :: Only"
    ],
    keywords="contrastive learning, computer vision, image augmentation"
)
