# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spark_utils',
 'spark_utils.common',
 'spark_utils.dataframes',
 'spark_utils.dataframes.sets',
 'spark_utils.delta_lake',
 'spark_utils.models']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=36.0,<36.1',
 'delta-spark>=1.1,<1.2',
 'hadoop-fs-wrapper>=0.4.5,<0.5.0',
 'pandas>=1.4,<1.5']

setup_kwargs = {
    'name': 'spark-utils',
    'version': '0.6.0',
    'description': 'Utility classes for comfy Spark job authoriing.',
    'long_description': '# Introduction \nUtility functions and classes for working with Dataframes, provisioning SparkSession and much more.\n\nCore features:\n- Provisioning Spark session with some routine settings set in advance, including Delta Lake configuration. You must have delta-core jars in class path for this to work.\n- Spark job argument wrappers, allowing to specify job inputs for `spark.read.format(...).options(...).load(...)` and outputs for `spark.write.format(...).save(...)` in a generic way. Those are exposed as `source` and `target` built-in arguments (see example below).\n\nConsider a simple Spark Job that reads `json` data from `source` and stores it as `parquet` in `target`. This job can be defined using `spark-utils` as below:\n\n```python\nfrom spark_utils.common.spark_job_args import SparkJobArgs\nfrom spark_utils.common.spark_session_provider import SparkSessionProvider\n\n\ndef main(args=None):\n    """\n     Job entrypoint\n    :param args:\n    :return:\n    """\n    spark_args = SparkJobArgs()\n        .parse(args)\n\n    source_table = spark_args.source(\'json_source\')\n    target_table = spark_args.output(\'parquet_target\')\n\n    # Spark session and hadoop FS\n    spark_session = SparkSessionProvider().get_session()\n    df = spark_session.read.format(source_table.data_format).load(source_table.data_path)\n    df.write.format(target_table.data_format).save(target_table.data_path)\n```\n\nNow we can call this job directly or with `spark-submit`. Note that you must have `spark-utils` in PYTHONPATH before running the script:\n```commandline\nspark-submit --master local[*] --deploy-mode client --name simpleJob ~/path/to/main.py --source \'json_source|file://tmp/test_json/*|json\' --output \'parquet_target|file://tmp/test_parquet/*|parquet\'\n```\n\n  - Job argument encryption is supported. This functionality requires an encryption key to be present in a cluster environment variable `RUNTIME_ENCRYPTION_KEY`. The only supported algorithm now is `fernet`. You can declare an argument as encrypted using `new_encrypted_arg` function. You then must pass an encrypted value to the declared argument, which will be decrypted by `spark-utils` when a job is executed and passed to the consumer.\n\nFor example, you can pass sensitive spark configuration (storage access keys, hive database passwords etc.) encrypted:\n\n```python\nimport json\n\nfrom spark_utils.common.spark_job_args import SparkJobArgs\nfrom spark_utils.common.spark_session_provider import SparkSessionProvider\n\n\ndef main(args=None):\n    spark_args = SparkJobArgs()\n        .new_encrypted_arg("--custom-config", type=str, default=None,\n                           help="Optional spark configuration flags to pass. Will be treated as an encrypted value.")\n        .parse(args)\n\n    spark_session = SparkSessionProvider(\n        additional_configs=json.loads(\n            spark_args.parsed_args.custom_config) if spark_args.parsed_args.custom_config else None).get_session()\n\n    ...\n```\n\n- Delta Lake utilities\n  - Table publishing to Hive Metastore.\n  - Delta OSS compaction with row count / file optimization target.\n- Models for common data operations like data copying etc. Note that actual code for those operations will be migrated to this repo a bit later.\n- Utility functions for common data operations, for example, flattening parent-child hierarchy, view concatenation, column name clear etc.\n\nThere are so many possibilities with this project - please feel free to open an issue / PR adding new capabilities or fixing those nasty bugs!\n\n# Getting Started\nSpark Utils must be installed on your cluster or virtual env that Spark is using Python interpreter from:\n```commandline\npip install spark-utils\n```\n\n# Build and Test\nTest pipeline runs Spark in local mode, so everything can be tested against our current runtime. Update the image used in `build.yaml` if you require a test against a different runtime version.\n',
    'author': 'ECCO Sneaks & Data',
    'author_email': 'esdsupport@ecco.com',
    'maintainer': 'GZU',
    'maintainer_email': 'gzu@ecco.com',
    'url': 'https://github.com/SneaksAndData/spark-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
