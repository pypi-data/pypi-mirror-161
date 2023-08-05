# -*- coding: utf-8 -*-
import pdb
from setuptools import setup
from setuptools import find_packages
from distutils.cmd import Command
from distutils.extension import Extension
import os
import sys
import io
import subprocess
import platform
import numpy as np
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import Cython.Compiler.Options

Cython.Compiler.Options.annotate = True

if "--line_trace" in sys.argv:
    line_trace = True
    print("Build with line trace enabled ...")
    sys.argv.remove("--line_trace")
else:
    line_trace = False

PACKAGE = "ultron"
NAME = "Finance-Ultron"
VERSION = "0.7.6"
DESCRIPTION = "FinUltron " + VERSION
AUTHOR = "flaght"
AUTHOR_EMAIL = "flaght@gmail.com"
URL = 'https://github.com/flaght'


def git_version():
    from subprocess import Popen, PIPE
    gitproc = Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE)
    (stdout, _) = gitproc.communicate()
    return stdout.strip()


if platform.system() != "Windows":
    import multiprocessing
    n_cpu = multiprocessing.cpu_count()
else:
    n_cpu = 0


class version_build(Command):

    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None, "directory that contains the test definitions"),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        git_ver = git_version()[:10]
        configFile = 'ultron/__init__.py'

        file_handle = open(configFile, 'r')
        lines = file_handle.readlines()
        newFiles = []
        for line in lines:
            if line.startswith('__version__'):
                line = line.split('+')[0].rstrip()
                line = line + " + \"-" + git_ver + "\"\n"
            newFiles.append(line)
        file_handle.close()
        os.remove(configFile)
        file_handle = open(configFile, 'w')
        file_handle.writelines(newFiles)
        file_handle.close()


if sys.version_info > (3, 0, 0):
    requirements = "requirements/py3.txt"
else:
    requirements = "requirements/py2.txt"

ext_modules = [
    "ultron/sentry/Analysis/TechnicalAnalysis/StatefulTechnicalAnalysers.pyx",
    "ultron/sentry/Analysis/TechnicalAnalysis/StatelessTechnicalAnalysers.pyx",
    "ultron/sentry/Analysis/CrossSectionValueHolders.pyx",
    "ultron/sentry/Analysis/SecurityValueHolders.pyx",
    "ultron/sentry/Analysis/SeriesValues.pyx",
    "ultron/sentry/Analysis/transformer.pyx",
    "ultron/sentry/Math/Accumulators/IAccumulators.pyx",
    "ultron/sentry/Math/Accumulators/impl.pyx",
    "ultron/sentry/Math/Accumulators/StatefulAccumulators.pyx",
    "ultron/sentry/Math/Accumulators/StatelessAccumulators.pyx",
    "ultron/sentry/Math/Distributions/norm.pyx",
    "ultron/sentry/Math/Distributions/NormalDistribution.pyx",
    "ultron/sentry/Math/ErrorFunction.pyx",
    "ultron/sentry/Math/MathConstants.pyx", "ultron/sentry/Math/udfs.pyx",
    "ultron/sentry/Utilities/Asserts.pyx", "ultron/sentry/Utilities/Tools.pyx",
    "ultron/tradingday/Calendar.pyx", "ultron/tradingday/Date.pyx",
    "ultron/tradingday/Period.pyx", "ultron/tradingday/Schedule.pyx",
    "ultron/tradingday/Enums/TimeUnits.pyx",
    "ultron/tradingday/Enums/BizDayConventions.pyx",
    "ultron/tradingday/Enums/DateGeneration.pyx",
    "ultron/tradingday/Enums/Months.pyx",
    "ultron/tradingday/Enums/NormalizingType.pyx",
    "ultron/tradingday/Enums/OptionType.pyx",
    "ultron/tradingday/Enums/Weekdays.pyx"
]


def generate_extensions(ext_modules, line_trace=True):

    extensions = []

    if line_trace:
        print("define cython trace to True ...")
        define_macros = [('CYTHON_TRACE', 1), ('CYTHON_TRACE_NOGIL', 1)]
    else:
        define_macros = []

    for pyxfile in ext_modules:
        ext = Extension(name='.'.join(pyxfile.split('/'))[:-4],
                        sources=[pyxfile],
                        define_macros=define_macros)
        extensions.append(ext)
    return extensions


import multiprocessing

n_cpu = multiprocessing.cpu_count()

ext_modules_settings = cythonize(generate_extensions(ext_modules, line_trace),
                                 compiler_directives={
                                     'embedsignature': True,
                                     'linetrace': line_trace
                                 },
                                 nthreads=n_cpu)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    include_package_data=False,
    install_requires=io.open(requirements, encoding='utf8').read(),
    classifiers=[],
    cmdclass={"version_build": version_build},
    ext_modules=ext_modules_settings,
    include_dirs=[np.get_include()],
)
