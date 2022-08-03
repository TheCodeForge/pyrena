import setuptools

setuptools.setup(
	name="pyrena",
	version="1.0.3",
	description="Python wrapper for Arena QMS API.",
	url="https://github.com/thecodeforge/pyrena",
	py_modules=["pyrena"],
	install_requires=[
		"mistletoe",
		"requests"
	],
	packages=setuptools.find_packages()
)