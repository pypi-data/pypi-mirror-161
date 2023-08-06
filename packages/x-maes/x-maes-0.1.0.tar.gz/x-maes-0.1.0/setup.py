from setuptools import setup, find_packages

setup(
  name = 'x-maes',
  packages = find_packages(exclude=['examples']),
  version = '0.1.0',
  license='MIT',
  description = 'X-MAEs - Pytorch',
  author = 'Jiangwei Zhao',
  author_email = '2574298210@qq.com',
  url = 'https://github.com/Mmhmmmmm/x-maes',
  long_description_content_type = 'text/markdown',
  keywords = [
    'artificial intelligence',
    'attention mechanism',
    'transformers',
    'mae'
  ],
  install_requires=[
    'torch>=1.6',
    'einops>=0.3',
    'entmax'
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)