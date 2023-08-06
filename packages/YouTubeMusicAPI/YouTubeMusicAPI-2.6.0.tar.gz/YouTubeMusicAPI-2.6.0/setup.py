import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="YouTubeMusicAPI",
    version="2.6.0",
    author="Sijey Praveen",
    author_email="cjpraveen@hotmail.com",
    description="The unofficial search API for YouTube Music.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sijey-Praveen/YouTube-Music-API",
    keywords = "youtube music api, YouTubeMusicAPI, python youtube music api, youtube music api python, youtube api pypi, sijey-praveen pypi, youtube api, sijey, sijey-praveen, sijey praveen projects, sijey praveen",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
