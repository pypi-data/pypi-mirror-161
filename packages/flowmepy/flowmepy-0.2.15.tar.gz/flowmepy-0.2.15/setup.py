import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

def copytree(src: str, dst: str, ext:str = "", symlinks: bool=False, ignore: bool=None):
    import shutil
    import os

    if not os.path.exists(dst):
        os.mkdir(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        if os.path.isdir(s):
            copytree(s, d, ext, symlinks, ignore)
        elif ext:
            if s.endswith(ext):
                shutil.copyfile(s, d)
        else:
            shutil.copyfile(s, d)

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):

    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        import shutil

        extdir = os.path.abspath(os.path.dirname(
            self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        # make headless
        cmake_args += ['-Dfm_headless=ON']

        if platform.system() == "Windows":
            cmake_args += [
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            # the next line is needed to get it running on martin@cvl - comment if it causes troubles on your system
            cmake_args += ['-DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda-8.0/']

            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        # disable qDebug() output
        cmake_args += ['-Ddisable_qt_debug=ON']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] +
                              cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] +
                              build_args, cwd=self.build_temp)

        # copy dll's & data
        # this is quick & dirty -> sorry if it ever breaks here...
        fm_build_dir = os.getcwd() + os.path.sep + self.build_temp + os.path.sep + "flowme"

        if platform.system() == "Windows":
            fm_build_dir += os.path.sep + "Release"
    
        dst = os.getcwd() + os.path.sep + self.build_lib
        
        # remove next line - it just speeds-up installs by excluding training data
        # copytree(fm_build_dir + os.path.sep + "cloud", 
        #         dst + os.path.sep + "cloud")
        # copytree(fm_build_dir + os.path.sep + "samples",
        #          dst + os.path.sep + "samples")
        copytree(fm_build_dir + os.path.sep + "profiles",
                 dst + os.path.sep + "profiles")
        # copy config  markerdict - incluce_package_data + package_data.. did not work
        # not sure why so I did it like markus qick and dirty 
        # (see https://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distutils)
        # print(str(os.getcwd()))
        copytree(os.getcwd() + os.path.sep + "src" + os.path.sep + "configs", dst + os.path.sep + "configs")

        if platform.system() == "Windows":
            copytree(fm_build_dir + os.path.sep,
                     dst + os.path.sep, "dll")


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'flowmepy',
    version = '0.2.15',
    author = 'Markus Diem, Lisa Weijler, Matthias Woedlinger, Florian Kowarsch',
    author_email = 'lweijler@cvl.tuwien.ac.at',
    description = 'a C++ FCS Loader',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    ext_modules = [CMakeExtension('FlowMePy')],
    cmdclass = dict(build_ext=CMakeBuild),
    packages = find_packages('src', exclude=["test"]),
    package_dir = {'': 'src'},
    install_requires = [
        'numpy>=1.17.4',
        'pandas>=0.24.2',
        'cmake!=3.16.3',    # we ad a issue with the docker here (no module named 'skbuild')
    ],
    zip_safe=False,
    #package_data={'src':['flowme/configs/markerdict.json']},
)
