'''
@author: Andrew Abi-Mansour (andrew.gaam [at] gmail [dot] com)
@date: March 23, 2019
'''


__version__ = "2018.9.2.7"

import subprocess
import setuptools
import os, sys, shutil
import glob
from distutils.command.build import build
from setuptools.command.build_py import build_py
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
      self.spawn(cmd=['make', '-j2', 'install'])
    else:
      self.spawn(cmd=['cmake', '-GNinja', '..'] +  cm_args)
      self.spawn(cmd=['ninja'])

    os.chdir('../..')
    super().run()

class RDKitBuild_py(build_py):

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

  def delObjFiles(self, fdir):

    dfile_ext = ['tar.gz', '.so.1', '.so', '.log', '.a']

    for path in glob.glob(fdir):
      if os.path.isdir(path):
        self.delObjFiles(path + '/*')
      elif os.path.isfile(path):
        for ext in dfile_ext:
          if path.endswith(ext):
            os.remove(path)
            print('Deleting ' + os.path.abspath(path))

  def delDownloadedFiles(self, fdir):

    dlist = ['build', 'External/rapidjson-1.1.0', 'External/catch/catch/',
            'External/YAeHMOP/tmp/', 'External/YAeHMOP/src/',
            'External/CoordGen/maeparser/', 'External/CoordGen/coordgen/',
            'External/YAeHMOP/yaehmop/', 'lib',
            'rdkit/Chem/inchi.py', 'Code/GraphMol/SLNParse/lex.yysln.cpp',
            'Code/GraphMol/SLNParse/sln.tab.cpp', 'Code/GraphMol/SLNParse/sln.tab.hpp',
            'Code/GraphMol/SmilesParse/lex.yysmarts.cpp', 'Code/GraphMol/SmilesParse/lex.yysmiles.cpp',
            'Code/GraphMol/SmilesParse/smarts.tab.cpp', 'Code/GraphMol/SmilesParse/smarts.tab.hpp',
            'Code/GraphMol/SmilesParse/smiles.tab.cpp', 'Code/GraphMol/SmilesParse/smiles.tab.hpp',
            'Code/RDGeneral/RDConfig.h', 'Code/RDGeneral/export.h', 'Code/RDGeneral/test.h', 
            'Code/RDGeneral/versions.cpp', 'Code/RDGeneral/versions.h', 'rdkit/RDPaths.py',
            'Data/eht_parms.dat', 'Data/templates.mae']

    for dobj in dlist:
      path = os.path.join(fdir, dobj)

      if os.path.isdir(path):
        shutil.rmtree(path)
      elif os.path.isfile(path):
        os.remove(path)
      else:
        continue
      print('Deleting ' + os.path.abspath(path))

  def run(self):
    self.delObjFiles('src/*')
    self.delDownloadedFiles('src')
    super().run()

def pre_build(include_dirs):

  if not os.path.isdir("src/build"):
    os.mkdir('src/build')

  if not os.path.isdir("src/build/lib"):
    os.mkdir('src/build/lib')

  for include_dir in include_dirs:
    open(include_dir + '/__init__.py', 'a').close()

if __name__ == '__main__':

  include_dirs = [] #'src/lib', 'src/Data', 'src/Projects', 'src/Contrib', 'src/Docs']
  pre_build(include_dirs) # must be always called to ensure sdist is built correctly

  setuptools.setup(
      name = "rdkit",
      version = __version__,
      description = ("A collection of cheminformatics and machine-learning software written in C++ and Python"),
      license = "BSD",
      keywords = "cheminformatics",
      url = "https://github.com/rdkit/rdkit",
      packages=setuptools.find_packages('src'),
      package_dir={'rdkit': 'src/rdkit', 'lib': 'src/lib', 'Data': 'src/Data', 'Projects': 'src/Projects', 'Docs': 'src/Docs', 'Contrib': 'src/Contrib'},
      include_package_data=True,
      classifiers=[
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
  	     "Programming Language :: Python :: 3"
      ],
      zip_safe=False,
      cmdclass={'build_py': RDKitBuild_py, 'build': RDKitBuild, 'clean': RDKClean},
      )
