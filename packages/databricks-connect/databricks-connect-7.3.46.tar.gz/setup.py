#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import pkgutil
import glob
import os
import sys
from setuptools import setup
from shutil import copyfile, copytree, rmtree

EULA = """LICENSE
---------------------------------
Copyright (2018) Databricks, Inc.

This library (the "Software") may not be used except in connection with the
Licensee's use of the Databricks Platform Services pursuant to an Agreement
(defined below) between Licensee (defined below) and Databricks, Inc.
("Databricks"). This Software shall be deemed part of the "Subscription
Services" under the Agreement, or if the Agreement does not define
Subscription Services, then the term in such Agreement that refers to the
applicable Databricks Platform Services (as defined below) shall be
substituted herein for "Subscription Services."  Licensee's use of the
Software must comply at all times with any restrictions applicable to the
Subscription Services, generally, and must be used in accordance with any
applicable documentation. If you have not agreed to an Agreement or otherwise
do not agree to these terms, you may not use the Software.  This license
terminates automatically upon the termination of the Agreement or Licensee's
breach of these terms.

Agreement: the agreement between Databricks and Licensee governing the use of
the Databricks Platform Services, which shall be, with respect to Databricks,
the Databricks Terms of Service located at www.databricks.com/termsofservice,
and with respect to Databricks Community Edition, the Community Edition Terms
of Service located at www.databricks.com/ce-termsofuse, in each case unless
Licensee has entered into a separate written agreement with Databricks
governing the use of the applicable Databricks Platform Services.

Databricks Platform Services: the Databricks services or the Databricks
Community Edition services, according to where the Software is used.

Licensee: the user of the Software, or, if the Software is being used on
behalf of a company, the company."""

for importer in pkgutil.iter_importers():
    if not hasattr(importer, "path") or not importer.path:
        continue  # skip over non-file or relative importers
    has_pyspark = os.path.exists(os.path.join(importer.path, "pyspark"))
    is_dbr = os.path.exists(os.path.join(importer.path, "pyspark/wrapped_python.py"))
    if has_pyspark and not is_dbr:
        print(
            "Found conflicting `pyspark` installation at {}. ".format(
                os.path.join(importer.path, "pyspark")) +
            "Please uninstall this with `pip uninstall pyspark` before installing "
            "databricks-connect.")
        sys.exit(-1)

if sys.version_info < (2, 7):
    print("Python versions prior to 2.7 are not supported for pip installed PySpark.",
          file=sys.stderr)
    sys.exit(-1)

try:
    exec(open('pyspark/version.py').read())
except IOError:
    print("Failed to load PySpark version file for packaging. You must be in Spark's python dir.",
          file=sys.stderr)
    sys.exit(-1)
VERSION = __version__  # noqa
# A temporary path so we can access above the Python project root and fetch scripts and jars we need
TEMP_PATH = "deps"
SPARK_HOME = os.path.abspath("../")

# Provide guidance about how to use setup.py
incorrect_invocation_message = """
If you are installing pyspark from spark source, you must first build Spark and
run sdist.

    To build Spark with maven you can run:
      ./build/mvn -DskipTests clean package
    Building the source dist is done in the Python directory:
      cd python
      python setup.py sdist
      pip install dist/*.tar.gz"""

# Figure out where the jars are we need to package with PySpark.
JARS_PATH = glob.glob(os.path.join(SPARK_HOME, "assembly/target/scala-*/jars/"))

if len(JARS_PATH) == 1:
    JARS_PATH = JARS_PATH[0]
elif (os.path.isfile("../RELEASE") and len(glob.glob("../jars/spark*core*.jar")) == 1):
    # Release mode puts the jars in a jars directory
    JARS_PATH = os.path.join(SPARK_HOME, "jars")
elif len(JARS_PATH) > 1:
    print("Assembly jars exist for multiple scalas ({0}), please cleanup assembly/target".format(
        JARS_PATH), file=sys.stderr)
    sys.exit(-1)
elif len(JARS_PATH) == 0 and not os.path.exists(TEMP_PATH):
    print(incorrect_invocation_message, file=sys.stderr)
    sys.exit(-1)

EXAMPLES_PATH = os.path.join(SPARK_HOME, "examples/src/main/python")
SCRIPTS_PATH = os.path.join(SPARK_HOME, "bin")
USER_SCRIPTS_PATH = os.path.join(SPARK_HOME, "sbin")
DATA_PATH = os.path.join(SPARK_HOME, "data")
LICENSES_PATH = os.path.join(SPARK_HOME, "licenses")
DBCONNECT_CONF_PATH = os.path.join(SPARK_HOME, "dbconnect/conf")

SCRIPTS_TARGET = os.path.join(TEMP_PATH, "bin")
USER_SCRIPTS_TARGET = os.path.join(TEMP_PATH, "sbin")
JARS_TARGET = os.path.join(TEMP_PATH, "jars")
EXAMPLES_TARGET = os.path.join(TEMP_PATH, "examples")
DATA_TARGET = os.path.join(TEMP_PATH, "data")
LICENSES_TARGET = os.path.join(TEMP_PATH, "licenses")

# Check and see if we are under the spark path in which case we need to build the symlink farm.
# This is important because we only want to build the symlink farm while under Spark otherwise we
# want to use the symlink farm. And if the symlink farm exists under while under Spark (e.g. a
# partially built sdist) we should error and have the user sort it out.
in_spark = (os.path.isfile("../core/src/main/scala/org/apache/spark/SparkContext.scala") or
            (os.path.isfile("../RELEASE") and len(glob.glob("../jars/spark*core*.jar")) == 1))


def _supports_symlinks():
    """Check if the system supports symlinks (e.g. *nix) or not."""
    return getattr(os, "symlink", None) is not None


if (in_spark):
    # Construct links for setup
    try:
        os.mkdir(TEMP_PATH)
    except:
        print("Temp path for symlink to parent already exists {0}".format(TEMP_PATH),
              file=sys.stderr)
        sys.exit(-1)

# If you are changing the versions here, please also change ./python/pyspark/sql/utils.py
# For Arrow, you should also check ./pom.xml and ensure there are no breaking changes in the
# binary format protocol with the Java version, see ARROW_HOME/format/* for specifications.
_minimum_pandas_version = "0.23.2"
_minimum_pyarrow_version = "0.15.1"

try:
    # We copy the shell script to be under pyspark/python/pyspark so that the launcher scripts
    # find it where expected. The rest of the files aren't copied because they are accessed
    # using Python imports instead which will be resolved correctly.
    try:
        os.makedirs("pyspark/python/pyspark")
    except OSError:
        # Don't worry if the directory already exists.
        pass
    copyfile("pyspark/shell.py", "pyspark/python/pyspark/shell.py")

    if (in_spark):
        # Construct the symlink farm - this is necessary since we can't refer to the path above the
        # package root and we need to copy the jars and scripts which are up above the python root.
        if _supports_symlinks():
            os.symlink(JARS_PATH, JARS_TARGET)
            os.symlink(SCRIPTS_PATH, SCRIPTS_TARGET)
            os.symlink(USER_SCRIPTS_PATH, USER_SCRIPTS_TARGET)
            os.symlink(EXAMPLES_PATH, EXAMPLES_TARGET)
            os.symlink(DATA_PATH, DATA_TARGET)
            os.symlink(LICENSES_PATH, LICENSES_TARGET)
        else:
            # For windows fall back to the slower copytree
            copytree(JARS_PATH, JARS_TARGET)
            copytree(SCRIPTS_PATH, SCRIPTS_TARGET)
            copytree(USER_SCRIPTS_PATH, USER_SCRIPTS_TARGET)
            copytree(EXAMPLES_PATH, EXAMPLES_TARGET)
            copytree(DATA_PATH, DATA_TARGET)
            copytree(LICENSES_PATH, LICENSES_TARGET)
    else:
        # If we are not inside of SPARK_HOME verify we have the required symlink farm
        if not os.path.exists(JARS_TARGET):
            print("To build packaging must be in the python directory under the SPARK_HOME.",
                  file=sys.stderr)

    if not os.path.isdir(SCRIPTS_TARGET):
        print(incorrect_invocation_message, file=sys.stderr)
        sys.exit(-1)

    # Scripts directive requires a list of each script path and does not take wild cards.
    script_names = os.listdir(SCRIPTS_TARGET)
    scripts = list(map(lambda script: os.path.join(SCRIPTS_TARGET, script), script_names))
    # We add find_spark_home.py to the bin directory we install so that pip installed PySpark
    # will search for SPARK_HOME with Python.
    scripts.append("pyspark/find_spark_home.py")

    with open('README.md') as f:
        long_description = f.read()

    setup(
        name='databricks-connect',
        version=VERSION,
        description='Databricks Connect Client',
        long_description=(
            'Databricks Connect is a Spark client library that lets you connect your '
            'favorite IDE (IntelliJ, Eclipse, PyCharm, and so on), notebook server '
            '(Zeppelin, Jupyter, RStudio), and other custom applications to Databricks '
            'clusters and run Spark code.\n\n'
            'To get started, run ``databricks-connect configure`` after installation.\n\n'
            'AWS docs: https://docs.databricks.com/user-guide/dev-tools/databricks-connect.html\n\n'
            'Azure docs: https://docs.microsoft.com/en-us/azure/databricks/'
            'user-guide/dev-tools/databricks-connect.html\n\n'
            'GCP docs: https://docs.gcp.databricks.com/dev-tools/databricks-connect.html\n\n'
            'Overview\n'
            '---------\n'
            'Databricks Connect allows you to write '
            'jobs using Spark native APIs and have them execute remotely on a Databricks '
            'cluster instead of in the local Spark session.\n\n'
            'For example, when you run the DataFrame command ``spark.read.parquet(...).'
            'groupBy(...).agg(...).show()`` using Databricks Connect, the parsing and '
            'planning of the job runs on your local machine. Then, the logical '
            'representation of the job is sent to the Spark server running in Databricks '
            'for execution in the cluster.\n\n'
            'With Databricks Connect, you can:\n\n'
            '- Run large-scale Spark jobs from any Python, Java, Scala, or R application. '
            'Anywhere you can ``import pyspark``, ``import org.apache.spark``, or '
            '``require(SparkR)``, you can now run Spark jobs directly from your '
            'application, without needing to install any IDE plugins or use Spark '
            'submission scripts.\n'
            '- Step through and debug code in your IDE even when working with a remote '
            'cluster.\n'
            '- Iterate quickly when developing libraries. You do not need to restart the '
            'cluster after changing Python or Java library dependencies in Databricks '
            'Connect, because each client session is isolated from each other in the '
            'cluster.\n'
            '- Shut down idle clusters without losing work. Because the client session is '
            'decoupled from the cluster, it is unaffected by cluster restarts or upgrades, '
            'which would normally cause you to lose all the variables, RDDs, and DataFrame '
            'objects defined in a notebook.\n\n' + EULA),
        long_description_content_type="text/markdown",
        author='Databricks',
        author_email='feedback@databricks.com',
        packages=['pyspark',
                  'pyspark.databricks',
                  'pyspark.databricks.koalas',
                  'pyspark.databricks.utils',
                  'pyspark.mllib',
                  'pyspark.mllib.linalg',
                  'pyspark.mllib.stat',
                  'pyspark.ml',
                  'pyspark.ml.linalg',
                  'pyspark.ml.param',
                  'pyspark.sql',
                  'pyspark.sql.avro',
                  'pyspark.sql.pandas',
                  'pyspark.streaming',
                  'pyspark.bin',
                  'pyspark.sbin',
                  'pyspark.jars',
                  'pyspark.python.pyspark',
                  'pyspark.python.lib',
                  'pyspark.data',
                  'pyspark.licenses',
                  'pyspark.examples.src.main.python'],
        include_package_data=True,
        package_dir={
            'pyspark.jars': 'deps/jars',
            'pyspark.bin': 'deps/bin',
            'pyspark.sbin': 'deps/sbin',
            'pyspark.python.lib': 'lib',
            'pyspark.data': 'deps/data',
            'pyspark.licenses': 'deps/licenses',
            'pyspark.examples.src.main.python': 'deps/examples',
        },
        package_data={
            'pyspark.jars': ['*.jar'],
            'pyspark.bin': ['*'],
            'pyspark.sbin': ['spark-config.sh', 'spark-daemon.sh',
                             'start-history-server.sh',
                             'stop-history-server.sh', ],
            'pyspark.python.lib': ['*.zip'],
            'pyspark.data': ['*.txt', '*.data'],
            'pyspark.licenses': ['*.txt'],
            'pyspark.examples.src.main.python': ['*.py', '*/*.py']},
        scripts=scripts,
        entry_points={
            'console_scripts': [
                'databricks-connect = pyspark.databricks_connect:main',
            ],
        },
        license='Databricks Proprietary License',
        install_requires=['py4j==0.10.9', 'six'],
        provides=['pyspark'],
        obsoletes=['pyspark'],
        extras_require={
            'ml': ['numpy>=1.7'],
            'mllib': ['numpy>=1.7'],
            'sql': [
                'pandas>=%s' % _minimum_pandas_version,
                'pyarrow>=%s' % _minimum_pyarrow_version,
            ]
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: Other/Proprietary License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy']
    )
finally:
    # We only cleanup the symlink farm if we were in Spark, otherwise we are installing rather than
    # packaging.
    if (in_spark):
        # Depending on cleaning up the symlink farm or copied version
        if _supports_symlinks():
            os.remove(os.path.join(TEMP_PATH, "jars"))
            os.remove(os.path.join(TEMP_PATH, "bin"))
            os.remove(os.path.join(TEMP_PATH, "sbin"))
            os.remove(os.path.join(TEMP_PATH, "examples"))
            os.remove(os.path.join(TEMP_PATH, "data"))
            os.remove(os.path.join(TEMP_PATH, "licenses"))
        else:
            rmtree(os.path.join(TEMP_PATH, "jars"))
            rmtree(os.path.join(TEMP_PATH, "bin"))
            rmtree(os.path.join(TEMP_PATH, "sbin"))
            rmtree(os.path.join(TEMP_PATH, "examples"))
            rmtree(os.path.join(TEMP_PATH, "data"))
            rmtree(os.path.join(TEMP_PATH, "licenses"))
        os.rmdir(TEMP_PATH)
