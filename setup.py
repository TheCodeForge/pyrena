import setuptools

with open("README.md", "r") as file:
	readme = file.read()

setuptools.setup(
	name="pyrena",
	version="1.4.1",
	description="Python wrapper for Arena QMS API.",
	url="https://github.com/thecodeforge/pyrena",
	py_modules=["pyrena"],
	install_requires=[
		"mistletoe",
		"requests"
	],
	packages=setuptools.find_packages(),
	package_dir={
		"pyrena":"pyrena"
	},
	python_requires= '>=3.7',
	long_description = readme,
	long_description_content_type = "text/markdown"
)