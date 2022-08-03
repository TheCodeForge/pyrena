from setuptools import setup

setup(
	name="pyrena",
	version="1.0.0",
	description="Python wrapper for Arena QMS API.",
	url="https://github.com/thecodeforge/pyrena",
	py_modules=["pyrena"],
	install_requires=[
		"mistletoe",
		"requests"
	]
)