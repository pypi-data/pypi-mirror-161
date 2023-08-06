from setuptools import setup

setup(
	name="pyrena",
	version="1.0.1",
	description="Python wrapper for Arena QMS API.",
	url="https://github.com/thecodeforge/pyrena",
	py_modules=["pyrena"],
	install_requires=[
		"mistletoe",
		"requests"
	],
	package_dir={
		"pyrena":"pyrena"
	}
)