from setuptools import setup
import pathwin

classifiers = [
	"Development Status :: 5 - Production/Stable",
	"Programming Language :: Python :: 2",
	"Programming Language :: Python :: 3",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: MIT License",
	"Topic :: Software Development :: Libraries",
	"Topic :: Utilities",
]

with open("README.md", "r") as f:
	long_description = f.read()

setup(
	name="pathwin",
	version=pathwin.__version__,
	author="kurages",
	author_email="git.kurages@outlook.jp",
	url="https://github.com/kurages/pathwin",
	py_modules=["pathwin"],
	description="setPath is a library for easy manipulation of the Windows environment variable Path.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	license="MIT License",
	classifiers=classifiers,
	python_requires=">=3.6"
)
