# Copyright 2022 Airwallex.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydeequ import SparkSession

class DataLoader:
    """Data Loader
    Load data from different data sources

    Args:
    spark: SparkSession
        Run the data loader on which spark session .

    Returns:
    df: DataFrame
        Data frame of loaded data.
    """
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def load_list(self, data, schema):
        self.df = self.spark.createDataFrame(data, schema)
        return self.df

    def load_csv(self, data_path):
        self.df = self.spark.read.options(header=True, inferSchema=True).csv(data_path)
        return self.df

    def load_bigquery(self, data_path):
        raise NotImplementedError("load bigquery need implementation")