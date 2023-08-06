from abc import ABC
from abc import abstractmethod

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession


class SparkExecNode(ABC):
    @abstractmethod
    def to_dataframe(self, spark: SparkSession) -> DataFrame:
        raise NotImplementedError
