'''
@author: Andrew Abi-Mansour (andrew.gaam [at] gmail [dot] com)
@date: March 23, 2019
'''


__version__ = "2018.9.2.7"

import subprocess
import setuptools
import os, sys
import glob
from distutils.command.build import build
from distutils.command.clean import clean

class RDKitBuild(build):

  def find(self, fname, path):

    for root, dirs, files in os.walk(path):
      if fname in files:
        return os.path.join(root, fname)

    return None

  def run(self):

    python_version = str(sys.version_info[0]) + str(sys.version_info[1])

    python_lib = self.find('libpython{}.so'.format(python_version).format(python_version), '/') 
    python_exec = sys.executable

    if not python_lib:
      print('Could not find any installed python-dev (libpython.so) library.')
      print('Proceeding ...')
      cm_args = ['-DPYTHON_EXECUTABLE=' + python_exec]
    else:
      cm_args = ['-DPYTHON_LIBRARY=' + python_lib, '-DPYTHON_EXECUTABLE=' + python_exec]

    os.chdir('src/build')
    try:
      import ninja
    except:
      self.spawn(cmd=['cmake', '..'] +  cm_args)
      self.spawn(cmd=['make', 'install'])
    else:
      self.spawn(cmd=['cmake', '-GNinja', '..'] +  cm_args)
      self.spawn(cmd=['ninja'])

    os.chdir('../..')
    super().run()

class RDKClean(clean):

  def findObjFiles(self, fdir):

    for path in glob.glob(fdir):
      if os.path.isdir(path):
        self.findObjFiles(path + '/*')
      elif os.path.isfile(path):
        if path.endswith('.so') or path.endswith('.so.1'):
          os.remove(path)
          print('Deleting ' + os.path.abspath(path))

  def run(self):
    self.findObjFiles('src/*')
    super().run()

def pre_build():

  if not os.path.isdir("src/build"):
    os.mkdir('src/build')

  if not os.path.isdir("src/build/lib"):
    os.mkdir('src/build/lib')

if __name__ == '__main__':

  pre_build()

  setuptools.setup(
      name = "rdkit",
      version = __version__,
      description = ("A collection of cheminformatics and machine-learning software written in C++ and Python"),
      license = "BSD",
      keywords = "cheminformatics",
      url = "https://github.com/rdkit/rdkit",
      packages=setuptools.find_packages('src') + ['rdkit.lib', 'rdkit.Data', 'rdkit.Projects', 'rdkit.Contrib', 'rdkit.Docs'] ,
      package_dir={'rdkit':'src/rdkit', 'rdkit.lib':'src/build/lib', 'rdkit.Data': 'src/Data', 'rdkit.Docs': 'src/Docs', \
                  'rdkit.Projects': 'src/Projects', 'rdkit.Contrib': 'src/Contrib'},
      include_package_data=True,
      classifiers=[
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
  	     "Programming Language :: Python :: 3"
      ],
      zip_safe=False,
      cmdclass={'build': RDKitBuild, 'clean': RDKClean},
      )
