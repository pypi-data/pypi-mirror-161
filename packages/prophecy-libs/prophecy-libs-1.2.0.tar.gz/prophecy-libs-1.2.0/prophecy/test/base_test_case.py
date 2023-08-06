import unittest
from pyspark.sql import SparkSession
import glob


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # jarDependencies = glob.glob("/opt/docker/lib/*.jar")
        cls.spark = SparkSession.builder.master("local").appName("init") \
            .config("spark.sql.legacy.allowUntypedScalaUDF", "true") \
            .getOrCreate()
        cls.maxUnequalRowsToShow = 5

    def setup(self):
        self.spark = BaseTestCase.spark
        self.maxUnequalRowsToShow = BaseTestCase.maxUnequalRowsToShow
