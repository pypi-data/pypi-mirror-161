#TODO: Implement src-structure from https://www.freecodecamp.org/news/how-to-create-and-upload-your-first-python-package-to-pypi/
#from distutils.core import setup
import setuptools

version = '1.0.3'

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
  name              = 'pythonskole',     # How you named your package folder (MyLib)
  packages          = ['pythonskole'],   # Chose the same as "name"
  author            = 'Vegard Lundby Rekaa',        # Type in your name
  author_email      = 'vegard@pythonskole.no',      # Type in your E-Mail
  description       = 'Koder til bruk i undervisning i Python',   # Give a short description about your library
  long_description  = long_description,
  long_description_content_type = 'text/markdown',
  url               = 'https://github.com/vegardlr/pythonskole',   # Provide either the link to your github or to your website
  version           = version,      # Start with a small number and increase it with every change you make
  license           ='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  download_url      = 'https://github.com/vegardlr/pythonskole/archive/refs/tags/v'+version+'.tar.gz',    # I explain this later on
  keywords          = ['Pythonskole', 'Undervisning', 'Koding','Python','Programmering','Læring'],   # Keywords that define your package best
  install_requires  = ['numpy', 'matplotlib'],
  # Development Status: "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
  classifiers=[
    'Development Status :: 4 - Beta',  
    'Intended Audience :: Education',    
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',     
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10'
  ],
)
