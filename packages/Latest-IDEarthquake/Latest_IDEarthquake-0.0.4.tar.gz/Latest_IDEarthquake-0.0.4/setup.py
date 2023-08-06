from setuptools import setup

with open("README.md", "r", encoding ="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Latest_IDEarthquake',
    version='0.0.4',
    packages=['gempaterkirni'],
    url='https://github.com/RemoteWorkerIDN/Latest_IDEarthquake',
    license='Development Status :: 4 - Beta',
    author='danahiswara',
    author_email='danahiswara.danas@gmail.com',
    description='This package will scrape Indonesia\'s latest earthquake data from bmkg.go.id'
)
