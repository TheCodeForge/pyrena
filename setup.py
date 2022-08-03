from distutils.core import setup

setup(
	name="pyrena",
	version="1.0",
	description="Python wrapper for Arena QMS API. No license granted.",
	url="https://github.com/thecodeforge/pyrena",
	py_modules="pyrena",
	install_requires=[
		"mistletoe",
		"requests"
	]
)