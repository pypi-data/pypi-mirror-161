import sys
from typing import Dict, Optional, Union, List
from johnsnowlabs import med, nlp, ocr, settings, viz
# het helpers into global space
from johnsnowlabs.nlp import *

import johnsnowlabs as jsl

# TODO all these imports below should be INSIDE of methods!
from johnsnowlabs.abstract_base.lib_resolver import try_import_lib, is_spark_version_env
from johnsnowlabs.abstract_base.software_product import AbstractSoftwareProduct
from johnsnowlabs.auto_install.jsl_home import setup_jsl_home, get_install_suite_from_jsl_home
from johnsnowlabs.auto_install.offline_install import get_printable_dependency_urls
from johnsnowlabs.auto_install.softwares import SparkNlpSoftware, Software
from johnsnowlabs.utils.enums import ProductName, PyInstallTypes, JvmHardwareTarget
from johnsnowlabs.utils.env_utils import is_running_in_databricks
from johnsnowlabs.utils.jsl_secrets import JslSecrets
from johnsnowlabs.utils.sparksession_utils import authenticate_enviroment_HC, authenticate_enviroment_OCR, retry
from johnsnowlabs.auto_install.install_software import check_and_install_dependencies


def login():
    pass


def install(
        browser_login: bool = True,
        access_token: Optional[str] = None,
        license_number: int = 0,
        secrets_file: Optional[str] = None,
        product: Optional[ProductName] = None,
        python_exec_path: str = sys.executable,
        hc_license: Optional[str] = None,
        hc_secret: Optional[str] = None,
        ocr_secret: Optional[str] = None,
        ocr_license: Optional[str] = None,
        aws_access_key: Optional[str] = None,
        aws_key_id: Optional[str] = None,
        install_optional: bool = True,
        install_licensed: bool = True,
        sparknlp_to_latest: bool = True,

        install_to_current_env: bool = True,

        databricks_host: Optional[str] = None,
        databricks_password: Optional[str] = None,
        databricks_email: Optional[str] = None,
        databricks_token: Optional[str] = None,

        store_in_jsl_home: bool = True,

        offline: bool = False,
        gpu: bool = False,
        m1: bool = False,
        py_install_type=PyInstallTypes.wheel):
    secrets: JslSecrets = JslSecrets.build_or_try_find_secrets(browser_login=browser_login,
                                                               access_token=access_token,
                                                               license_number=license_number,
                                                               secrets_file=secrets_file,
                                                               hc_license=hc_license,
                                                               hc_secret=hc_secret,
                                                               ocr_secret=ocr_secret,
                                                               ocr_license=ocr_license,
                                                               aws_access_key=aws_access_key,
                                                               aws_key_id=aws_key_id,
                                                               return_empty_secrets_if_none_found=True)

    if not product:
        product = Software.jsl_full
    elif product == ProductName.nlp.value:
        product = Software.spark_nlp
    elif product == ProductName.nlu.value:
        product = Software.nlu
    elif product == ProductName.jsl_full.value:
        product = Software.jsl_full
    elif product == ProductName.hc.value:
        product = Software.spark_hc
    elif product == ProductName.ocr.value:
        product = Software.spark_ocr
    elif product == ProductName.nlp_display.value:
        product = Software.sparknlp_display
    elif product == ProductName.pyspark.value:
        product = Software.pyspark

    elif not offline:
        bck = "\n"
        raise Exception(f'Invalid install target: {product}'
                        f' please specify on of:\n{bck.join([n.value for n in ProductName])}')

    if gpu:
        jvm_install_type = JvmHardwareTarget.gpu
    elif m1:
        jvm_install_type = JvmHardwareTarget.m1
    else:
        jvm_install_type = JvmHardwareTarget.cpu

    if store_in_jsl_home and not offline:
        setup_jsl_home(
            secrets=secrets,
            jvm_install_type=jvm_install_type,
            py_install_type=py_install_type,
        )

    if offline:
        get_printable_dependency_urls(secrets=secrets,
                                      jvm_install_type=jvm_install_type,
                                      py_install_type=py_install_type)
    elif databricks_host:
        # TODO test if Stuff downloaded or not.
        pass


    elif install_to_current_env:
        check_and_install_dependencies(product=product, secrets=secrets, install_optional=install_optional,
                                       install_licensed=install_licensed, sparknlp_to_latest=sparknlp_to_latest,
                                       python_exec_path=python_exec_path)

    # TODO if databricks, check configs are correctly set!


def start(
        browser_login: bool = False,
        access_token: Optional[str] = None,
        license_number: int = 0,
        secrets_file: Optional[str] = None,
        hc_license: Optional[str] = None,
        hc_secret: Optional[str] = None,
        ocr_secret: Optional[str] = None,
        ocr_license: Optional[str] = None,
        aws_access_key: Optional[str] = None,
        aws_key_id: Optional[str] = None,
        spark_conf: Dict[str, str] = None,
        master_url: str = 'local[*]',
        jar_paths: List[str] = None,
        exclude_nlp: bool = False,
        exclude_healthcare: bool = False,
        exclude_ocr: bool = False,
        gpu=False,
        m1=False,

) -> 'pyspark.sql.SparkSession':
    """
    Start a SparkSession with JSL-Products of your choice and authenticates the environment to use licensed software
    based on supplied secrets and licenses.
    By default all libraries for which valid credentials are supplied will be loaded into the Spark Sessions JVM.
    You exclude any of them from being loaded by using the exclude parameters.

    If secrets_file and all license and secret parameters are None,
    the following strategy is applied to find secret and license information on this machine:

    1. The pattern os.getcwd()/*.json will be globed for valid JSL-Secret json files
     and substituted for the secrets_file parameter

    2. The pattern /content/*.json will be globed by default and searched for valid JSL-Secret json files
     and substituted for the secrets_file parameter

    3. Environment is checked for variable names match up with a secret file_name

    4. /~/.johnsnowlabs will be searched for default credentials file generated from CLI-login (TODO implement)

    5. Supply Email+password or Token to start a session?



    :param secrets_file: A file
    :param hc_license:
    :param hc_secret:
    :param ocr_secret:
    :param ocr_license:
    :param aws_access_key:
    :param aws_key_id:
    :param spark_conf:
    :param master_url:
    :param exclude_nlp:
    :param exclude_healthcare:
    :param exclude_ocr:
    :param gpu:
    :return:
    """
    from pyspark.sql import SparkSession

    if '_instantiatedSession' in dir(SparkSession) and SparkSession._instantiatedSession is not None:
        print('Warning::Spark Session already created, some configs may not take.')
    from johnsnowlabs.auto_install.lib_resolvers import OcrLibResolver, HcLibResolver, NlpLibResolver
    jars = []

    if gpu:
        suite = get_install_suite_from_jsl_home(only_jars=True,jvm_hardware_target=JvmHardwareTarget.gpu)
    elif m1:
        suite = get_install_suite_from_jsl_home(only_jars=True,jvm_hardware_target=JvmHardwareTarget.m1)
    else:
        suite = get_install_suite_from_jsl_home(only_jars=True,jvm_hardware_target=JvmHardwareTarget.cpu)

    # Collect all Jar URLs for the SparkSession
    jars = []

    if not exclude_nlp:
         jars.append(suite.nlp.get_java_path())

    if suite.secrets:
        if suite.secrets.HC_LICENSE and not exclude_healthcare:
            jars.append(suite.hc.get_java_path())
            authenticate_enviroment_HC(suite)

        if suite.secrets.OCR_LICENSE and not exclude_ocr:
            jars.append(suite.ocr.get_java_path())
            authenticate_enviroment_OCR(suite)

    builder = SparkSession.builder.appName(settings.spark_session_name).master(master_url)

    default_conf = {"spark.driver.memory": "32G",
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.kryoserializer.buffer.max": "2000M",
                    'spark.driver.maxResultSize': '2000M',
                    'spark.jars': ','.join(jars), }

    if suite.secrets and suite.secrets.OCR_LICENSE:
        # is_spark_version_env('32')
        default_conf["spark.sql.optimizer.expression.nestedPruning.enabled"] = "false"
        default_conf["spark.sql.optimizer.nestedSchemaPruning.enabled"] = "false"
        default_conf["spark.sql.legacy.allowUntypedScalaUDF"] = "true"
        default_conf["spark.sql.repl.eagerEval.enabled"] = "true"

    for k, v in default_conf.items():
        builder.config(str(k), str(v))
    if spark_conf:
        for k, v in spark_conf.items():
            builder.config(str(k), str(v))

    spark = builder.getOrCreate()

    # TODO what is this for?? We need bo th??
    if suite.secrets and suite.secrets.HC_LICENSE:
        spark._jvm.com.johnsnowlabs.util.start.registerListenerAndStartRefresh()
    if suite.secrets and suite.secrets.OCR_SECRET:
        retry(spark._jvm.com.johnsnowlabs.util.OcrStart.registerListenerAndStartRefresh)
    return spark
