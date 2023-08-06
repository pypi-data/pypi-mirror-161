# -*- coding: utf-8 -*-
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
#

import functools
import re
import sys
import threading
import traceback
import os
import inspect
import platform
from py4j.protocol import Py4JJavaError

__all__ = []


def _exception_message(excp):
    """Return the message from an exception as either a str or unicode object.  Supports both
    Python 2 and Python 3.

    >>> msg = "Exception message"
    >>> excp = Exception(msg)
    >>> msg == _exception_message(excp)
    True

    >>> msg = u"unicöde"
    >>> excp = Exception(msg)
    >>> msg == _exception_message(excp)
    True
    """
    if isinstance(excp, Py4JJavaError):
        # 'Py4JJavaError' doesn't contain the stack trace available on the Java side in 'message'
        # attribute in Python 2. We should call 'str' function on this exception in general but
        # 'Py4JJavaError' has an issue about addressing non-ascii strings. So, here we work
        # around by the direct call, '__str__()'. Please see SPARK-23517.
        return excp.__str__()
    if hasattr(excp, "message"):
        return excp.message
    return str(excp)


def _get_argspec(f):
    """
    Get argspec of a function. Supports both Python 2 and Python 3.
    """
    if sys.version_info[0] < 3:
        argspec = inspect.getargspec(f)
    else:
        # `getargspec` is deprecated since python3.0 (incompatible with function annotations).
        # See SPARK-23569.
        argspec = inspect.getfullargspec(f)
    return argspec


def print_exec(stream):
    ei = sys.exc_info()
    traceback.print_exception(ei[0], ei[1], ei[2], None, stream)


class VersionUtils(object):
    """
    Provides utility method to determine Spark versions with given input string.
    """
    @staticmethod
    def majorMinorVersion(sparkVersion):
        """
        Given a Spark version string, return the (major version number, minor version number).
        E.g., for 2.0.1-SNAPSHOT, return (2, 0).

        >>> sparkVersion = "2.4.0"
        >>> VersionUtils.majorMinorVersion(sparkVersion)
        (2, 4)
        >>> sparkVersion = "2.3.0-SNAPSHOT"
        >>> VersionUtils.majorMinorVersion(sparkVersion)
        (2, 3)

        """
        m = re.search(r'^(\d+)\.(\d+)(\..*)?$', sparkVersion)
        if m is not None:
            return (int(m.group(1)), int(m.group(2)))
        else:
            raise ValueError("Spark tried to parse '%s' as a Spark" % sparkVersion +
                             " version string, but it could not find the major and minor" +
                             " version numbers.")


def fail_on_stopiteration(f):
    """
    Wraps the input function to fail on 'StopIteration' by raising a 'RuntimeError'
    prevents silent loss of data when 'f' is used in a for loop in Spark code
    """
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except StopIteration as exc:
            raise RuntimeError(
                "Caught StopIteration thrown from user's code; failing the task",
                exc
            )

    return wrapper


def _print_missing_jar(lib_name, pkg_name, jar_name, spark_version):
    print("""
________________________________________________________________________________________________

  Spark %(lib_name)s libraries not found in class path. Try one of the following.

  1. Include the %(lib_name)s library and its dependencies with in the
     spark-submit command as

     $ bin/spark-submit --packages org.apache.spark:spark-%(pkg_name)s:%(spark_version)s ...

  2. Download the JAR of the artifact from Maven Central http://search.maven.org/,
     Group Id = org.apache.spark, Artifact Id = spark-%(jar_name)s, Version = %(spark_version)s.
     Then, include the jar in the spark-submit command as

     $ bin/spark-submit --jars <spark-%(jar_name)s.jar> ...

________________________________________________________________________________________________

""" % {
        "lib_name": lib_name,
        "pkg_name": pkg_name,
        "jar_name": jar_name,
        "spark_version": spark_version
    })


def _normalize_path_for_spark_client_on_windows(sc, path):
    from pyspark.sql import SparkSession
    session = SparkSession._instantiatedSession
    if session is not None and \
            session.conf.get("spark.databricks.service.client.enabled") == "true" and \
            platform.system() == "Windows" and \
            session.conf.get(
                "spark.databricks.service.client.windows.path.normalizationEnabled") == "true":
        return path.replace(os.path.sep, "/")
    else:
        return path


def _parse_memory(s):
    """
    Parse a memory string in the format supported by Java (e.g. 1g, 200m) and
    return the value in MiB

    Examples
    --------
    >>> _parse_memory("256m")
    256
    >>> _parse_memory("2g")
    2048
    """
    units = {'g': 1024, 'm': 1, 't': 1 << 20, 'k': 1.0 / 1024}
    if s[-1].lower() not in units:
        raise ValueError("invalid format: " + s)
    return int(float(s[:-1]) * units[s[-1].lower()])


def inheritable_thread_target(f):
    """
    Return thread target wrapper which is recommended to be used in PySpark when the
    pinned thread mode is enabled. The wrapper function, before calling original
    thread target, it inherits the inheritable properties specific
    to JVM thread such as ``InheritableThreadLocal``.

    Also, note that pinned thread mode does not close the connection from Python
    to JVM when the thread is finished in the Python side. With this wrapper, Python
    garbage-collects the Python thread instance and also closes the connection
    which finishes JVM thread correctly.

    When the pinned thread mode is off, it return the original ``f``.

    Parameters
    ----------
    f : function
        the original thread target.

    .. versionadded:: 3.2.0

    Notes
    -----
    This API is experimental.

    It captures the local properties when you decorate it. Therefore, it is encouraged
    to decorate it when you want to capture the local properties.

    For example, the local properties from the current Spark context is captured
    when you define a function here:

    >>> @inheritable_thread_target
    ... def target_func():
    ...     pass  # your codes.

    If you have any updates on local properties afterwards, it would not be reflected to
    the Spark context in ``target_func()``.

    The example below mimics the behavior of JVM threads as close as possible:

    >>> Thread(target=inheritable_thread_target(target_func)).start()  # doctest: +SKIP
    """
    from pyspark import SparkContext
    if os.environ.get("PYSPARK_PIN_THREAD", "false").lower() == "true":
        # Here's when the pinned-thread mode (PYSPARK_PIN_THREAD) is on.
        sc = SparkContext._active_spark_context

        # Get local properties from main thread
        properties = sc._jsc.sc().getLocalProperties().clone()

        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                # Set local properties in child thread.
                sc._jsc.sc().setLocalProperties(properties)
                return f(*args, **kwargs)
            finally:
                thread_connection = sc._jvm._gateway_client.thread_connection.connection()
                if thread_connection is not None:
                    connections = sc._jvm._gateway_client.deque
                    # Reuse the lock for Py4J in PySpark
                    with SparkContext._lock:
                        for i in range(len(connections)):
                            if connections[i] is thread_connection:
                                connections[i].close()
                                del connections[i]
                                break
                        else:
                            # Just in case the connection was not closed but removed from the
                            # queue.
                            thread_connection.close()
        return wrapped_f
    else:
        return f


class InheritableThread(threading.Thread):
    """
    Thread that is recommended to be used in PySpark instead of :class:`threading.Thread`
    when the pinned thread mode is enabled. The usage of this class is exactly same as
    :class:`threading.Thread` but correctly inherits the inheritable properties specific
    to JVM thread such as ``InheritableThreadLocal``.

    Also, note that pinned thread mode does not close the connection from Python
    to JVM when the thread is finished in the Python side. With this class, Python
    garbage-collects the Python thread instance and also closes the connection
    which finishes JVM thread correctly.

    When the pinned thread mode is off, this works as :class:`threading.Thread`.

    .. versionadded:: 3.1.0


    Notes
    -----
    This API is experimental.
    """
    def __init__(self, target, *args, **kwargs):
        super(InheritableThread, self).__init__(
            target=inheritable_thread_target(target), *args, **kwargs
        )


if __name__ == "__main__":
    import doctest
    (failure_count, test_count) = doctest.testmod()
    if failure_count:
        sys.exit(-1)
