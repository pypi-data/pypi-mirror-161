from setuptools import setup

setup(name='rf_otp',
      version='0.1.10',
      description='Get OTP 6 digits from OTP',
      url='https://argon.ceti.etat-ge.ch/gitlab/performancetests/robotframework/rf-otp',
      author='Pedro Lopez Perez',
      author_email='pedro.lopez-perez@etat.ge.ch',
      license='MIT',
      packages=['rf_otp'],
      install_requires=[
          "pyotp=='2.6.0'",
      ],
      package_dir={'': 'src'},
      zip_safe=False)