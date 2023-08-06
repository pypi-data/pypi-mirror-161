import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="weepy",
	version="1.0.8",
	scripts=["tools/dev_server.py"],
	entry_points={
		'console_scripts': ['weepy=dev_server:server'],
	},
	author="Patrik Katrenak",
	author_email="patrik@katryapps.com",
	description="Tiny Python ASGI framework",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://gitlab.com/katry/weepy",
	packages=["weepy"],
	install_requires=[],
	extras_require={
		"orjson": ["orjson"],
		"ujson": ["ujson"],
		"dev": ["daemon", "uvicorn[standard]", "orjson", "python-dotenv", "requests", "pytest"]
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
		"Operating System :: OS Independent",
	],
	platforms=["any"],
	python_requires=">=3.9",
)
