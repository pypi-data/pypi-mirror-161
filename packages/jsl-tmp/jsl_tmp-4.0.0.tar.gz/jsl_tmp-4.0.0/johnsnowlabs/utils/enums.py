from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
from johnsnowlabs.utils.lib_version import LibVersion
import requests


class Secret(str): pass


class ProductPlatform(Enum):
    # TODO MAYBE DROP
    java = 'java'
    spark = 'spark'
    python = 'python'


class LibVersionIdentifier(str):
    """Representation of a specific library version"""
    pass


class JvmHardwareTarget(Enum):
    gpu = 'gpu'
    cpu = 'cpu'
    m1 = 'm1'


class PyInstallTypes(Enum):
    tar = 'tar.gz'
    wheel = 'whl'


class SparkVersion(Enum):
    # Broad versions
    spark3xx = LibVersion('3.x.x')
    spark31x = LibVersion('3.1.x')
    spark32x = LibVersion('3.2.x')
    spark33x = LibVersion('3.3.x')
    spark330 = LibVersion('3.3.0')
    spark322 = LibVersion('3.2.2')
    spark321 = LibVersion('3.2.1')
    spark320 = LibVersion('3.2.0')
    spark313 = LibVersion('3.1.3')
    spark312 = LibVersion('3.1.2')
    spark311 = LibVersion('3.1.1')
    spark303 = LibVersion('3.0.3')
    spark302 = LibVersion('3.0.2')
    spark301 = LibVersion('3.0.1')
    spark300 = LibVersion('3.0.0')


class LatestCompatibleProductVersion(Enum):
    healthcare = LibVersion('4.0.0')
    spark_nlp = LibVersion('4.0.0')
    ocr = LibVersion('4.0.0')
    nlp_display = LibVersion('4.0.0')
    nlu = LibVersion('4.0.0')
    pyspark = LibVersion('3.2.0')
    finance = LibVersion('finance')
    spark = LibVersion('4.2.0')
    java = LibVersion('java')
    python = LibVersion('python')


class ProductName(Enum):
    hc = 'Spark-Healthcare'
    nlp = 'Spark-NLP'
    ocr = 'Spark-OCR'
    finance = 'Spark-Finance'
    nlp_display = 'NLP-Display'
    nlu = 'nlu'
    jsl_full = 'full'
    pyspark = 'pyspark'
    spark = 'spark'
    java = 'java'
    python = 'python'


class ProductLogo(Enum):
    healthcare = '💊'  # 🏥 🩺 💊 ❤️ ‍🩹 ‍⚕️💉
    spark_nlp = '🚀'
    ocr = '🕶'  # 👁️  🤖 🦾🦿 🥽 👀 🕶 🥽 ⚕
    finance = '🤑'  # 🤑🏦💲💳💰💸💵💴💶💷
    nlp_display = '🎨'
    nlu = '🤖'
    jsl_full = '💯🕴'  # 🕴
    java = '☕'
    python = '🐍'  # 🐉
    pyspark = '🐍+⚡'
    spark = '⚡'


class ProductSlogan(Enum):
    healthcare = 'Heal the planet with NLP!'
    spark_nlp = 'State of the art NLP at scale'
    ocr = 'Empower your NLP with a set of eyes'
    pyspark = 'The big data Engine'
    nlu = '1 line of code to conquer nlp!'
    jsl_full = 'The entire John Snow Labs arsenal!'
    finance = 'NLP for the Finance Industry'
    nlp_display = 'Visualize and Explain NLP!'
    spark = '⚡'
    java = '☕'
    python = '🐍'  # 🐉


@dataclass
class InstalledProductInfo:
    """Representation of a JSL product install. Version is None if not installed  """
    product: ProductName
    version: Optional[LibVersionIdentifier] = None


import urllib.request
import shutil
from urllib.request import urlopen


@dataclass
class UrlDependency:
    """Representation of a URL"""
    url: str
    dependency_type: Union[JvmHardwareTarget, PyInstallTypes]
    spark_version: SparkVersion
    dependency_version: LibVersion
    file_name: str
    product_name: ProductName

    def update_url(self, new_url):
        self.url = new_url

    def validate(self):
        # Try GET on the URL and see if its valid/reachable
        return requests.head(self.url).status_code == 200

    @staticmethod
    def internet_on():
        try:
            return True if urlopen('https://www.google.com/', timeout=10) else False
        except:
            return False

    def download_url(self, save_path):
        if not UrlDependency.internet_on():
            print(f'Warning! It looks like there is no active internet connection on this machine')
            print(f'Trying to continue but might run into problems...')

        if not self.validate():
              raise Exception("Trying to download Invalid URL!")
        save_path = save_path + '/' + self.file_name

        print(f'Downloading {self.file_name}')
        print(self.url)
        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(self.url) as response, open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)


@dataclass
class JslSuiteStatus:
    """Representation and install status of all JSL products and its dependencies.
    Version attribute of InstalledProductInfo is None for uninstalled products
    """
    spark_nlp_info: Optional[InstalledProductInfo] = None
    spark_hc_info: Optional[InstalledProductInfo] = None
    spark_ocr_info: Optional[InstalledProductInfo] = None
    nlu_info: Optional[InstalledProductInfo] = None
    sparknlp_display_info: Optional[InstalledProductInfo] = None
    pyspark_info: Optional[InstalledProductInfo] = None
