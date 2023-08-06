import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'lazyearth',                # Name project the same with folder
  packages = ['lazyearth'],          # Name project the same with folder
  version = '0.0.30',                 # 
  license='MIT', 
  description = 'Library OOP for workwith odc by Tun Kedsaro',    #Show on PyPi
  long_description=DESCRIPTION,
  author = 'Tun Kedsaro',            #          
  author_email = 'Tun.k@ku.th',      #
  url = 'https://github.com/Tun555/lazyearth',  #
  download_url = 'https://github.com/Tun555/lazyearth/archive/refs/tags/v0.0.15.zip',                                      #  
  keywords = ['OOP','ODC'],      # When someone search
  install_requires=[                 # Package that use
        'numpy',
        'matplotlib',
    ],  
  classifiers=[    
    'Development Status :: 1 - Planning',  
    'Intended Audience :: Education', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Version pathon that we test    
    'Programming Language :: Python :: 3.8',
  ],
)