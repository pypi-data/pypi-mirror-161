from setuptools import find_packages, setup
setup(
	name='epigenetics_utilities',
	packages=find_packages(include=['epigenetics_utilities']),
	version='0.1.0',
	description='Epigenetics Utilities from the Downing Lab',
	author='Me',
	license='MIT',
	install_requires=[],
	setup_requires=['pytest-runner'],
	tests_require=['pytest'],
	test_suite='tests',
)