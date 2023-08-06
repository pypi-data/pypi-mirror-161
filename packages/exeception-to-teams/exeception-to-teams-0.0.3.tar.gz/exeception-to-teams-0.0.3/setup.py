from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.3"
DESCRIPTION = "Notification/Alert for django users"
LONG_DESCRIPTION = (
    "A package that allows to send notification to microsoft teams channel."
)

# Setting up
setup(
    name="exeception-to-teams",
    version=VERSION,
    author="Ideabreed Technology (Milann Malla)",
    author_email="<hello@itsmilann.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["requests", "django"],
    keywords=["python", "django", "middleware", "exception", "ideabreed", "teams", "microsoft"],
    project_urls={
        "exception to teams": "https://github.com/ItsMilann/exeception-to-teams/tree/release",
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
