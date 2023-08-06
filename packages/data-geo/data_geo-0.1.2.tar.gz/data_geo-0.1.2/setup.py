from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent

with open(this_directory/'README.md', encoding='utf-8') as f:
    long_description = f.read()

with open(this_directory/'VERSION') as version_file:
    version = version_file.read().strip()

setup(name='data_geo',
      version=version,
      description='DataDBS for geojson',
      url='https://gitlab.com/pineiden/datadbs-geojson',
      author='David Pineda Osorio',
      author_email='dpineda@csn.uchile.cl',
      license='GPLv3',
      packages=['data_geo'],
      install_requires=["networktools", "datadbs", "numpy"],
      package_dir={'data_geo': 'data_geo'},
      package_data={
          'data_geo': ['../doc', '../docs', '../requeriments.txt']},
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False)
