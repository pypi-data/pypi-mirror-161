from distutils.core import setup
setup(
  name = 'speedboat',
  packages = ['speedboat'],
  version = '0.2',
  license='Apache License',
  description = 'Faster boto3 with multithreading',
  url = 'https://github.com/andyil/speedboat',
  download_url = 'https://github.com/andyil/speedboat/archive/0.1.tar.gz',
  keywords = ['aws', 's3', 'cloud', 'storage', 'shutil', 'network'],
  install_requires=['boto3'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'Topic :: Internet',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)