from setuptools import setup, find_packages
setup(
	name='arenasdk',
	version='0.10.0',
	description='Python SDK For Arena',
	author='AlanFok',
	url='https://arena-docs.readthedocs.io/en/latest',
	author_email='huozhixin2868@163.com',
	packages=find_packages(),
	install_requires=["pyyaml", "coloredlogs"]
)
