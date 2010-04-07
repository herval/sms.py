from setuptools import setup, find_packages

setup(name = 'sms',
      description = 'SMS sending and receiving with enfora gsm modems',
      long_description = open('README.txt').read(),
      author = ['Amos Latteier', 'Herval Freire'],
      author_email = 'amos@latteier.com',
      url = 'http://pypi.python.org/pypi/sms',
      license = 'MIT',
      version = '0.4',
      packages = find_packages('src'),
      package_dir = {'':'src'},
      package_data = {'sms': ['*.txt']},
      zip_safe = False,
      classifiers = [
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Communications :: Telephony'
        ],
      install_requires = ['pyserial', 'setuptools'],
    )
