from setuptools import setup
 
setup(name='pyAudioKits',
      version="1.0",
      description='Powerful Python audio workflow support based on librosa and other libraries',
      author='HarmoniaLeo',
      author_email='harmonialeo@gmail.com',
      maintainer='HarmoniaLeo',
      maintainer_email='harmonialeo@gmail.com',
      packages=['pyAudioKits','pyAudioKits.audio','pyAudioKits.algorithm','pyAudioKits.filters','pyAudioKits.datastructures','pyAudioKits.analyse'],
      license="Public domain",
      platforms=["any"],
      url="https://github.com/HarmoniaLeo/pyAudioKits",
     )