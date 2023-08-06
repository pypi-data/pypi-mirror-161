from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='bqpackage',
      version='2.3.26',
      description='Automation infrastructure kit tools for GUI and API tests',
      url='https://upload.pypi.org/legacy/',
      author='Moshe Sar-Idan',
      long_description=long_description,
      long_description_content_type="text/markdown",

      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      use_scm_version=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.7',
      )
