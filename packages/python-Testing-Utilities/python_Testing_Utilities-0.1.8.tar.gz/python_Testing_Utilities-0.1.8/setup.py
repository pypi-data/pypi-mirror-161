from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'requests==2.28.1'
]
sp_tests_require = [
  'pytest==7.1.2'
]

all_require = sp_install_requires + sp_tests_require

setup(name='python_Testing_Utilities',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Testing utilities for python apps',
      url='https://github.com/rmetcalf9/python_Testing_Utilities',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['python_Testing_Utilities'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
