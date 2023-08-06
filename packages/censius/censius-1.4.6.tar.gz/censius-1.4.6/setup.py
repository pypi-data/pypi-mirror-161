from setuptools import setup

with open('README.md', 'r') as fh:
  long_description = fh.read()

setup(
  name='censius',
  version='1.4.6',
  description='API for Censius',
  long_description=long_description,
  long_description_content_type='text/markdown',
  py_modules=["censius/client"],
  package_dir={'':'src'},
  packages=['censius'],
  install_requires=['requests','jsonschema','pandas'],
  extras_require={
    "dev": [
      "pytest>=3.7",
      "pdoc3==0.9.2"
    ]
  },
  url="https://github.com/Censius/censius-logs-python-sdk",
  author="Censius",
  author_email="dev@censius.ai",
  keywords=[]
)