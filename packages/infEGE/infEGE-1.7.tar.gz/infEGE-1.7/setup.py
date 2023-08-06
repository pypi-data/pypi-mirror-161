import setuptools

with open("infEGE/Documentation.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="infEGE",
    version="1.7",
    author="Ilya484",
    author_email="ucdo854@kemcdo.ru",
    description="Библиотека для ЕГЭ по информатике",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ilya484/infEGE",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)