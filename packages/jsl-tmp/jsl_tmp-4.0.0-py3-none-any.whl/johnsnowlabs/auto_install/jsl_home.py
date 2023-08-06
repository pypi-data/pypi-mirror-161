import shutil
import sys
from typing import Optional, List
import json
from johnsnowlabs import settings

from johnsnowlabs.auto_install.install_info import InstallFileInfo, JvmInstallInfo, PyInstallInfo, \
    RootInfo, InstallSuite, LocalPy4JLib
from johnsnowlabs.utils.jsl_secrets import JslSecrets
from johnsnowlabs.utils.enums import JvmHardwareTarget, PyInstallTypes, ProductName, UrlDependency
import os
from pathlib import Path
from johnsnowlabs.auto_install.offline_install import get_dependency_urls
from johnsnowlabs.utils.json_utils import dump_dataclass_to_json, json_path_as_dict
from johnsnowlabs.utils.lib_version import LibVersion

"""Folder structure :
~.johnsnowlabs/
   ├─ licenses/
   │  ├─ license1.json
   │  ├─ license2.json
   ├─ java_installs/
   │  ├─ app1.jar
   │  ├─ app2.jar
   ├─ py_installs/
   │  ├─ app1.tar.gz
   │  ├─ app2.tar.gz
   ├─ info.txt
"""



def jsl_home_exist():
    return os.path.exists(settings.root_info_file)


def is_jsl_home_outdated():
    if os.path.exists(settings.root_info_file):
        old_infos = RootInfo(**json_path_as_dict(settings.root_info_file))
        if old_infos.version == settings.version:
            return False
        else:
            return True

    else:
        raise Exception(f'JSL-Home does not exist! Cannot check if outdated')


def download_deps_and_create_info(deps: List[UrlDependency],
                                  lib_dir, info_file_path,
                                  overwrite=False, ):
    """Download a list of deps to given lib_dir folder and creates info_file at info_file_path.
    TODO check if Java Dep for new hardware release but same version
    """
    info = {}
    if os.path.exists(info_file_path):
        #  keep old infos, we assume they are up-to-date and compatible
        old_infos = json_path_as_dict(info_file_path)
        info.update(old_infos)

    for p in deps:
        if os.path.exists(f'{lib_dir}/{p.file_name}') and not overwrite:
            continue
        p.download_url(lib_dir)
        info[p.file_name] = dict(
            file_name=p.file_name,
            product=p.product_name,
            compatible_spark_version=p.spark_version.value.as_str(),
            install_type=p.dependency_type.value,
            product_version=p.dependency_version.as_str())
    with open(info_file_path, 'w') as json_file:
        json.dump(info, json_file, indent=4)



def setup_jsl_home(
        secrets: Optional[JslSecrets] = None,
        jvm_install_type: JvmHardwareTarget = JvmHardwareTarget.cpu,
        py_install_type: PyInstallTypes = PyInstallTypes.wheel,
        only_jars: bool = False,
        spark_version=None,
        overwrite=False,
) -> None:
    Path(settings.license_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.java_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.py_dir).mkdir(parents=True, exist_ok=True)

    if jsl_home_exist() and is_jsl_home_outdated():
        # TODO download non-JVM deps i.e wheels/tars x p with  pipdownload
        # TODO uuse install_software to setup pip sub_dep folder!
        # Delete everything except license data and re-create folder
        shutil.rmtree(settings.java_dir)
        shutil.rmtree(settings.py_dir)
        Path(settings.java_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.py_dir).mkdir(parents=True, exist_ok=True)

    java_deps, py_deps = get_dependency_urls(
        secrets=secrets,
        spark_version=spark_version,
        jvm_install_type=jvm_install_type,
        py_install_type=py_install_type)

    # store deps to jsl home with info.json files
    if not only_jars:
        download_deps_and_create_info(py_deps, settings.py_dir, settings.py_info_file, overwrite)
    download_deps_and_create_info(java_deps, settings.java_dir, settings.java_info_file, overwrite)

    root_info = RootInfo(version=settings.version, run_from=sys.executable, )
    dump_dataclass_to_json(root_info, settings.root_info_file, )
    if secrets:
        #     # TODO overwrite old creds or not?   Or Store Multipel!!!!
        dump_dataclass_to_json(secrets, settings.creds_file, )
        print(f'📋 Stored John Snow Labs Credentials in {settings.license_dir}')
    print(f'🙆 JSL Home setup in {settings.root_dir}')


def get_install_suite_from_jsl_home(create_jsl_home_if_missing: bool = True,
                                    jvm_hardware_target: JvmHardwareTarget = JvmHardwareTarget.cpu,
                                    hc: bool = True,
                                    ocr: bool = True,
                                    nlp: bool = True,
                                    only_jars: bool = False,
                                    recurisve_call=False,
                                    ) -> InstallSuite:
    """Read all info files from JSL home if exists.
    If not exists, sets up JSL home"""
    json_paths = [settings.java_info_file, settings.py_info_file]
    data = ()

    # TODO this needs to call JSlSecrets to start interactive Secret fetch flow
    # TODO CHECK IF MISSING
    if not jsl_home_exist() or is_jsl_home_outdated():
        # Nothing setup yet, download atlast spark nlp jars
        setup_jsl_home(only_jars=only_jars)

    # TODOD check if found but hardware target not match! -> Download

    for p in json_paths:
        if not os.path.exists(p):
            # TODOD FINE?
            print(f'Missing Info-file in {p}')
            continue
        with open(p) as f:
            data = (*data, json.load(f))

    data_classes = ()
    for file_info in data:
        for v in file_info.values():
            print(v['file_name'])
            file_info = InstallFileInfo(
                file_name=v['file_name'],
                product=ProductName(v['product']),
                compatible_spark_version=LibVersion(v['compatible_spark_version']),
                # install_type=JvmHardwareTarget(v['install_type']) if 'jar' in v['file_name'] else \
                #     PyInstallTypes(v['install_type']),
                product_version=LibVersion(v['product_version']), )
            install_type = v['install_type']
            if install_type in JvmHardwareTarget._value2member_map_:
                file_info = JvmInstallInfo(*file_info.__dict__.values(), install_type=JvmHardwareTarget(install_type))
            elif install_type in PyInstallTypes._value2member_map_:
                file_info = PyInstallInfo(*file_info.__dict__.values(), install_type=PyInstallTypes(install_type))
            else:
                raise Exception(f'Invalid Install Type = {install_type}')
            data_classes = (*data_classes, file_info)

    info = RootInfo(**json_path_as_dict(settings.root_info_file))
    license_data = JslSecrets.from_jsl_home()
    # TODO we could check  for len right away aand download if missing
    # Only for nLP lib, since other libs should be provided via .install()!
    java_ocr = [file for file in data_classes if
                file.install_type in JvmHardwareTarget and file.product == ProductName.ocr]
    py_ocr = [file for file in data_classes if file.install_type in PyInstallTypes and file.product == ProductName.ocr]
    ocr = java_ocr + py_ocr

    java_hc = [file for file in data_classes if
               file.install_type in JvmHardwareTarget and file.product == ProductName.hc]
    py_hc = [file for file in data_classes if file.install_type in PyInstallTypes and file.product == ProductName.hc]
    hc = java_hc + py_hc
    # Only Spark NLP has hardware specific releases
    java_nlp = [file for file in data_classes if
                file.install_type == jvm_hardware_target and file.product == ProductName.nlp]
    py_nlp = [file for file in data_classes if file.install_type in PyInstallTypes and file.product == ProductName.nlp]
    nlp = java_nlp + py_nlp

    if only_jars:
        suite = InstallSuite(
            ocr=LocalPy4JLib(java_ocr[0]) if len(java_ocr) == 1 else None,
            hc=LocalPy4JLib(java_hc[0]) if len(java_hc) == 1 else None,
            nlp=LocalPy4JLib(java_nlp[0]) if len(java_nlp) == 1 else None,
            secrets=license_data if license_data else None,
            info=info,
        )
        # Try downloading missing things and re-run
        if not suite.nlp:
            setup_jsl_home(only_jars=only_jars, jvm_install_type=jvm_hardware_target, )
            return get_install_suite_from_jsl_home(
                create_jsl_home_if_missing=create_jsl_home_if_missing,
                jvm_hardware_target=jvm_hardware_target,
                hc=hc,
                ocr=ocr,
                nlp=nlp,
                only_jars=only_jars, recurisve_call=True )

            pass

        if suite.secrets and suite.secrets.OCR_LICENSE and not suite.ocr:
            pass

        if suite.secrets and suite.secrets.HC_LICENSE and not suite.hc:
            pass

    return InstallSuite(
        ocr=LocalPy4JLib(*ocr) if len(ocr) == 2 or len(ocr) == 1 else None,
        hc=LocalPy4JLib(*hc) if len(hc) == 2 or len(hc) == 1 else None,
        nlp=LocalPy4JLib(*nlp) if len(nlp) == 2 or len(nlp) == 1 else None,
        secrets=license_data if license_data else None,
        info=info,
    )

# TODO ZIP!

# TODO validate info.json file with contents ? -> Super edy case
