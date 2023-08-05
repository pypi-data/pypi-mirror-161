from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'pytz==2019.3',
  'flask==2.0.3',
  'flask_restx==0.5.1',
  'python-dateutil==2.8.1',
  'sortedcontainers==2.4.0',
  'bcrypt==3.1.5',
  'pyjwt==1.7.1'
]
sp_tests_require = [
  'pytest==7.1.2'
]

all_require = sp_install_requires + sp_tests_require

setup(name='baseapp_for_restapi_backend_with_swagger',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package which provides a base application class for an app with a restapi backend that provides a swagger',
      url='https://github.com/rmetcalf9/baseapp_for_restapi_backend_with_swagger',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['baseapp_for_restapi_backend_with_swagger'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
