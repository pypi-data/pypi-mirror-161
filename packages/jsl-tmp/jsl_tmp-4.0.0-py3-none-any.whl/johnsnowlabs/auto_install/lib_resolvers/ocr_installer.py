from abc import ABCMeta
from johnsnowlabs.abstract_base.lib_resolver import JslLibDependencyResolverABC, PyInstallTypes
from johnsnowlabs.utils.enums import UrlDependency, LatestCompatibleProductVersion, ProductName, SparkVersion, \
    JvmHardwareTarget


class OcrLibResolver(JslLibDependencyResolverABC, metaclass=ABCMeta):
    has_cpu_jars = True
    has_py_install = True
    has_secret = True
    product_name = ProductName.ocr
    compatible_spark_versions = [SparkVersion.spark32x.value, SparkVersion.spark33x.value]
    lib_version = LatestCompatibleProductVersion.ocr.value

    compatible_spark_to_jar_map = {

        SparkVersion.spark32x: {
            JvmHardwareTarget.cpu:
                UrlDependency(
                    url='https://pypi.johnsnowlabs.com/{secret}/jars/spark-ocr-assembly-{lib_version}-spark32.jar',
                    dependency_type=JvmHardwareTarget.cpu,
                    spark_version=SparkVersion.spark32x,
                    product_name=product_name,
                    file_name=product_name.name,
                    dependency_version=lib_version),
        },

        SparkVersion.spark33x: {
            JvmHardwareTarget.cpu:
                UrlDependency(
                    url='https://pypi.johnsnowlabs.com/{secret}/jars/spark-ocr-assembly-{lib_version}-spark32.jar',
                    dependency_type=JvmHardwareTarget.cpu,
                    spark_version=SparkVersion.spark33x,
                    product_name=product_name,
                    file_name=product_name.name,
                    dependency_version=lib_version),

        }

    }

    compatible_spark_to_py_map = {
        SparkVersion.spark32x: {
            PyInstallTypes.wheel: UrlDependency(
                url='https://pypi.johnsnowlabs.com/{secret}/spark-ocr/spark_ocr-{lib_version}%2Bspark32-py3-none-any.whl',
                dependency_type=PyInstallTypes.wheel,
                spark_version=SparkVersion.spark32x,
                product_name=product_name,
                file_name=product_name.name,
                dependency_version=lib_version),

            PyInstallTypes.tar: UrlDependency(
                url='https://pypi.johnsnowlabs.com/{secret}/spark-ocr/spark_ocr-{lib_version}%2Bspark32-py3-none-any.whl',
                dependency_type=PyInstallTypes.tar,
                spark_version=SparkVersion.spark32x,
                product_name=product_name,
                file_name=product_name.name,
                dependency_version=lib_version),

        },
        SparkVersion.spark33x: {
            PyInstallTypes.wheel: UrlDependency(
                url='https://pypi.johnsnowlabs.com/{secret}/spark-ocr/spark_ocr-{lib_version}%2Bspark32-py3-none-any.whl',
                dependency_type=PyInstallTypes.wheel,
                spark_version=SparkVersion.spark33x,
                product_name=product_name,
                file_name=product_name.name,
                dependency_version=lib_version),

            PyInstallTypes.tar: UrlDependency(
                url='https://pypi.johnsnowlabs.com/{secret}/spark-ocr/spark_ocr-{lib_version}%2Bspark32-py3-none-any.whl',
                dependency_type=PyInstallTypes.tar,
                spark_version=SparkVersion.spark33x,
                product_name=product_name,
                file_name=product_name.name,
                dependency_version=lib_version),

        }

    }
