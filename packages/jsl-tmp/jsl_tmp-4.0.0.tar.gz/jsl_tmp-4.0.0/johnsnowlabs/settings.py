from os.path import expanduser

# libs
version = '0.0.1'
nlp = '4.0.0'
medical = '4.0.0'
ocr = '4.0.0'
nlu = '4.0.0'

# Local paths for jsl home
root_dir = jsl_creds_path = f'{expanduser("~")}/.johnsnowlabs'
license_dir = root_dir + '/licenses'
java_dir = root_dir + '/java_installs'
py_dir = root_dir + '/py_installs'
root_info_file = f'{root_dir}/info.json'
java_info_file = f'{java_dir}/info.json'
py_info_file = f'{py_dir}/info.json'
creds_file = f'{license_dir}/jsl_credentials.json'

# databricks
dbfs_home_dir = 'dbfs:/johnsnowlabs'
dbfs_java_dir = f'{dbfs_home_dir}/java_installs'
dbfs_py_dir = f'{dbfs_home_dir}/py_installs'
db_py_jobs_dir = f'{dbfs_home_dir}/py_jobs'
db_py_notebook_dir = f'{dbfs_home_dir}/py_notebook_jobs'
db_jar_jobs_dir = f'{dbfs_home_dir}/jar_jobs'

db_cluster_name = 'John-Snow-Labs-Databricks-Auto-Cluster🚀'
db_job_name = 'John-Snow-Labs-Job {job} 🚀'
db_run_name = 'John-Snow-Labs-Run 🚀'


# Local Spark mode
spark_session_name = 'John-Snow-Labs-Spark-Session 🚀'