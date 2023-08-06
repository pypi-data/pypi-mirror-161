from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
  name = 'randprox', 
  version = '1.4',      
  license='MIT',        
  description = 'Get Random Proxy',   
  author = 'KattStof',                   
  author_email = 'Kattstof@autistici.org',      
  url = 'https://github.com/kattstof',
  requires=['random', 'requests'],
  download_url = 'https://github.com/kattstof/RandProx', 
  keywords = ['proxy'],  
  classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3',
  ],
)
