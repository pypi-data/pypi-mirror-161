import importlib
import site
from importlib import reload

# from johnsnowlabs.abstract_base.software_product import AbstractSoftwareProduct

reload(site)

import sys
import os
from typing import Optional

from johnsnowlabs.utils.enums import LatestCompatibleProductVersion, LibVersionIdentifier, PyInstallTypes
from johnsnowlabs.utils.jsl_secrets import JslSecrets


def ocr_version_is_missmatch(secret_version):
    """Check if installed OCR version is the same as the OCR secret
    :param secret_version: ocr secret version
    :return: True if missmatch, False if versions are fien """
    try:
        import sparkocr
    except ImportError:
        # Import failed, there can be no version missmatch
        return False
    # check versions
    installed_version = sparkocr.version()
    if installed_version == secret_version:
        return False
    return True


def healthcare_version_is_missmatch(secret_version):
    """Check if installed Spark NLP hc version is the same as the Healthcare secret
    :param secret_version: hc secret version
    :return: True if missmatch, False if versions are fine"""
    try:
        import sparknlp_jsl
    except ImportError:
        # Import failed, there can be no version missmatch
        return False
    # check versions
    installed_version = sparknlp_jsl.version()
    if installed_version == secret_version:
        return False
    return True


def check_if_secret_missmatch_and_uninstall_if_bad(secret_version, module_name, package_name):
    """Check if OCR/Healthcare lib installed version match up with the secrets provided.
    If not, this will uninstall the missmaching library
    :param module_name: module import file_name
    :param package_name: pipe package file_name
    :param secret_version: hc/ocr secret version provided
    :return: True if missmatch was uninstalled, False if no missmatch found and nothing was done
    """

    try:
        importlib.import_module(module_name)
    except ImportError:
        # Import failed, there can be no version missmatch
        return False
    if module_name == 'sparknlp_jsl':
        # get versions
        import sparknlp_jsl
        installed_version = sparknlp_jsl.version()
        if installed_version == secret_version:
            return False
    elif module_name == 'sparkocr':
        # get versions
        import sparkocr
        installed_version = sparkocr.version()
        if installed_version == secret_version:
            return False
    else:
        raise ValueError(f'Invalid module_name=={module_name}')

    print(
        f"Installed {module_name}=={installed_version} version not matching provided secret version=={secret_version}. "
        f"Uninstalling it..")
    # version missmatch, uninstall shell
    uninstall_lib(package_name)
    return True


def uninstall_lib(pip_package_name, py_path=sys.executable):
    cmd = f'{py_path} -m pip uninstall {pip_package_name} -y '
    os.system(cmd)
    reload(site)


def install_standard_pypi_lib(pypi_name: str, module_name: Optional[str] = None,
                              python_path: str = sys.executable, upgrade: bool = True):
    """
    Install module via pypi.
    runs the command : 
        `python -m pip install [module_name]`
        `python -m pip install [module_name] --upgrade`
    :param pypi_name: file_name of pypi package
    :param module_name: If defined will import module into globals, making it available to running process
    :param python_path: Which Python to use for installing. Defaults to the Python calling this method.
    :param upgrade: use --upgrade flag or not 
    :return:
    """
    if not pypi_name:
        raise Exception(f'Tried to install software which has no pypi file_name! Aborting.')
    print(f'Installing {pypi_name} to {python_path}')
    c = f'{python_path} -m pip install {pypi_name} '
    if upgrade:
        c = c + '--upgrade '
    os.system(c)

    if module_name:
        try:
            # See if install worked
            # importlib.import_module(module_name)
            reload(site)
            globals()[module_name] = importlib.import_module(module_name)
        except ImportError as err:
            print(err)
            return False
    return True


def install_licensed_pypi_lib(secrets: JslSecrets, pypi_name, module_name, product: 'AbstractSoftwareProduct',
                              spark_version: LibVersionIdentifier = LatestCompatibleProductVersion.pyspark.value):
    """ Install Spark-NLP-Healthcare PyPI Package in current environment if it cannot be imported and license
    provided.
    This just requires the secret of the library.
    """
    get_deps = True
    missmatch = False

    if 'spark-nlp-jsl' in pypi_name:
        module_name = 'sparknlp_jsl'
        secret = secrets.HC_SECRET
        get_deps = False
        # missmatch = check_if_secret_missmatch_and_uninstall_if_bad(lib_version, hc_module_name, hc_pip_package_name)
    elif 'ocr' in pypi_name:
        secret = secrets.OCR_SECRET
        module_name = 'sparkocr'
        get_deps = False

    else:
        raise ValueError(f'Invalid install licensed install target ={pypi_name}')

    try:
        url = product.jsl_url_resolver.get_py_urls(secret=secret, spark_version_to_match=spark_version,
                                                   install_type=PyInstallTypes.wheel).url
        cmd = f'{sys.executable} -m pip install {url}'
        # cmd = f'{sys.executable} -m pip install {pypi_name}=={lib_version} --extra-index-url https://pypi.johnsnowlabs.com/{secret}'
        print(f'Running "{cmd}"')
        if not get_deps:
            cmd = cmd + ' --no-deps'
        os.system(cmd)
        reload(site)
        globals()[module_name] = importlib.import_module(module_name)
    except Exception as err:
        print('failure', err)
        return False

    return True
# python3 -m pip install --upgrade spark-nlp-jsl==3.5.2--user --extra-index-url https://pypi.johnsnowlabs.com/ 3.5.2-8cc37365b969b8e0c26871958f05be9dd800ed6c
