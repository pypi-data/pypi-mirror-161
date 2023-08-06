from dataclasses import dataclass
from typing import Union, Optional, Tuple

from johnsnowlabs import settings
from johnsnowlabs.utils.jsl_secrets import JslSecrets
from johnsnowlabs.utils.enums import ProductName, JvmHardwareTarget, PyInstallTypes
from johnsnowlabs.utils.lib_version import LibVersion


@dataclass
class InstallFileInfo:
    file_name: str
    product: ProductName
    compatible_spark_version: LibVersion
    product_version: LibVersion
    # install_type: Optional[JvmHardwareTarget]


@dataclass
class PyInstallInfo(InstallFileInfo):
    install_type: PyInstallTypes


@dataclass
class JvmInstallInfo(InstallFileInfo):
    install_type: JvmHardwareTarget


@dataclass
class InstallSuite:
    ocr: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    nlp: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    hc: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    secrets: Optional[JslSecrets] = None


from collections import namedtuple
import typing

Point = typing.NamedTuple("Point", [('x', int), ('y', int)])
Py4JInstall = typing.NamedTuple("Py4JInstall", [('java_dep', JvmInstallInfo),
                                                ('py_dep', PyInstallInfo)])
Py4JInstallMultiHardware = typing.NamedTuple("Py4JInstallMultiHardware",
                                             [('java_dep', JvmInstallInfo),
                                              ('py_dep', PyInstallInfo)])


@dataclass
class LocalPy4JLib:
    java_lib: JvmInstallInfo
    py_lib: Optional[PyInstallInfo] = None

    def get_java_path(self):
        return f'{settings.java_dir}/{self.java_lib.file_name}'

    def get_py_path(self):
        return f'{settings.py_dir}/{self.py_lib.file_name}'


@dataclass
class RootInfo:
    version: LibVersion
    run_from: str


@dataclass
class  InstallSuite:
    info: RootInfo
    nlp: LocalPy4JLib
    ocr: Optional[LocalPy4JLib] = None
    hc: Optional[LocalPy4JLib] = None
    secrets: Optional[JslSecrets] = None
    optional_pure_py_jsl: Optional[LocalPy4JLib] = None
    optional_pure_py_jsl_dependencies: Optional[LocalPy4JLib] = None
