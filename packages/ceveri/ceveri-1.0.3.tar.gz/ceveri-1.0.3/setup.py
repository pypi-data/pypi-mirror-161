from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "Natural Language :: Turkish",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Text Processing"
]

setup(
    name="ceveri",
    version="1.0.3",
    description="Google Cloud API ile veri yerelleştirmesi amacıyla çeviri işlemleri gerçekleştiren bir kütüphane.",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    url="https://ceveri.readthedocs.io",
    author="Arda Uzunoğlu",
    author_email="ardauzunogluarda@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="",
    packages=find_packages(),
    install_requires=["googletrans", "python-docx", "six", "pandas"]
)