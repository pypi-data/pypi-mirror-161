import time
import os

from johnsnowlabs.auto_install.install_info import InstallSuite


def authenticate_enviroment_HC(suite: InstallSuite):
    """Set Secret environ variables for Spark Context"""
    os.environ['SPARK_NLP_LICENSE'] = suite.secrets.HC_LICENSE
    os.environ['AWS_ACCESS_KEY_ID'] = suite.secrets.AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = suite.secrets.AWS_SECRET_ACCESS_KEY


def authenticate_enviroment_OCR(suite: InstallSuite):
    """Set Secret environ variables for Spark Context"""

    os.environ['SPARK_NLP_LICENSE'] = suite.secrets.OCR_LICENSE
    os.environ['AWS_ACCESS_KEY_ID'] = suite.secrets.AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = suite.secrets.AWS_SECRET_ACCESS_KEY


def authenticate_enviroment_HC_and_OCR(suite: InstallSuite):
    """Set Secret environ variables for Spark Context"""
    authenticate_enviroment_HC(suite)
    authenticate_enviroment_OCR(suite)


def retry(fun, max_tries=10):
    for i in range(max_tries):
        try:
            time.sleep(0.3)
            fun()
            break
        except Exception:
            continue
