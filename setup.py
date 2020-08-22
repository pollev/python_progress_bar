from distutils.core import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'python_progress_bar',
  packages = ['python_progress_bar'],
  version = '1.01',
  license='MIT',
  description = 'A progress bar for python shell scripts (Linux)',
  author = 'Polle Vanhoof',
  author_email = 'vanhoofpolle@gmail.com',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url = 'https://github.com/pollev/python_progress_bar',
  download_url = 'https://github.com/pollev/python_progress_bar/archive/v1.01.tar.gz',
  keywords = ['progress', 'bar', 'indicator'],
  install_requires=[
      ],
  classifiers=[
    'Development Status :: 4 - Beta', # "3 - Alpha" / "4 - Beta" / "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
