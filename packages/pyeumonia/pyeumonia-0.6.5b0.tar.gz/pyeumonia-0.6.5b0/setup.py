from setuptools import setup, find_packages
setup(
	name="pyeumonia",
	version="0.6.5-beta",
	description="Covid-19 api wrote by python, you can get the covid-19 data from China and the world",
	author="Senge-Studio",
	author_email="a1356872768@gmail.com",
	long_description=open("README.md", encoding="utf-8").read(),
	long_description_content_type="text/markdown",
	install_requires=["requests", "beautifulsoup4", "pypinyin", "iso3166"],
	python_requires=">=3.7.0",
	packages=find_packages(),
	include_package_data=True,
	license="GPL v3",
)