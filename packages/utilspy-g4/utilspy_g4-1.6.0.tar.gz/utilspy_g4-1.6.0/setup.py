from setuptools import setup
from os import path


top_level_directory = path.abspath(path.dirname(__file__))
with open(path.join(top_level_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

setup(
   name='utilspy_g4',
   version='1.6.0',
   description='Small utils for Python',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Genzo',
   author_email='genzo@bk.ru',
   url='https://github.com/Genzo4/utilspy',
   project_urls={
           'Bug Tracker': 'https://github.com/Genzo4/utilspy/issues',
       },
   classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
      'Programming Language :: Python :: 3.10',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'Natural Language :: Russian',
      'Topic :: Software Development',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Utilities'
   ],
   keywords=['utils', 'utilspy', 'g4',
             'add ext', 'addExt', 'addext',
             'compareframes', 'compare frames', 'compareFrames',
             'delExt', 'del ext', 'delext',
             'templatedRemoveFiles', 'templated remove files', 'remove files',
             'getExt', 'get ext', 'getext',
             'concatVideo', 'concat video', 'concatvideo',
             'intTo2str', 'inttostr', 'int2str',
             'getFilesCount', 'files count',
             ],
   license='MIT',
   packages=['utilspy_g4'],
   install_requires=['opencv-contrib-python'],
   python_requires='>=3.6'
)