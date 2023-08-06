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

import json
from typing import Dict, List

from pydeequ.analyzers import *
from pydeequ.profiles import *
from pydeequ.checks import *
from pydeequ.verification import *
from pydeequ.analyzers import _AnalyzerObject

import pandas as pd

from vivqu.visualizer import *

class Default(_AnalyzerObject):
    """Default analyzer
    This class is used to add default analyzer to a column.
    """
    def __init__(self, column) -> None:
        super().__init__()
        self.column = column

class AnalyzeBuilder:
    """Analyze runner builder

    The class provides a builder to add various analyzers and settings
    and finally run them. This is actually an encapsulation over 
    pydeequ's AnalysisRunBuilder.

    In most cases, this class will not be accessed by users, as its functions
    are wrapped by QualityChecker.analyze().

    Example:
    >>> analyer = AnalyzeBuilder(spark_session, df)         # initialize the builder
    >>> analyzer.add_default("amount")                      # use default analysis setting
    >>> analyzer.add(Sum("amount")).add(Histogram("cost"))  # add some other metrics
    >>> analyzer.save_to("analysis_result.json")            # save result to json file
    >>> result_df = analyzer.run()                          # run it and get the result

    Args:
    spark: SparkSession
        The spark session used to analyzing data.
    dataframe: DataFrame
        The data frame object that need analysis.
    """
    def __init__(self, spark_session: SparkSession, df: DataFrame):
        self._spark_session = spark_session
        self._df = df
        self._AnaysisRunBuilder = AnalysisRunBuilder(spark_session, df)
        self.visualize = False
        self.save_file_path = None
    
    def add(self, analyzer_obj: _AnalyzerObject):
        """Add new analyzer to the builder

        Args:
        analyzer: _AnalyzerObject
            An analyer object derived from basic class _AnalyzerObject,
            including Default(), Completness(), Mean(), Size(), Sum() and so on.
        
        Returns:
        self: AnalyzeBuilder
            For further chained method calls.
        """
        if type(analyzer_obj) == Default:
            self.add_default(analyzer_obj.column)
        else:
            self._AnaysisRunBuilder.addAnalyzer(analyzer_obj)
        return self

    def add_default(self, column):
        """Add default analyzers to the given column

        Provide Completness, CountDistinct and Histogram metrics for text type,
        provide Completness, ApproxQuantiles, Maximum, Minimum metrics for numeric type,

        Args:
        column: str
            Add default metrics to which column.

        Returns:
        self: AnalyzeBuilder
            For further chained method calls.
        """
        is_found = False
        # get the schema from data frame
        schema = self._df.schema
        for struct_filed in schema:
            field_name: str = struct_filed.name
            if field_name == column:
                field_type = struct_filed.dataType
                type_name = field_type.typeName()
                self._AnaysisRunBuilder.addAnalyzer(Completeness(field_name))
                # if this field is text type
                if type_name in ["string", "integer", "long", "short"]:
                    self._AnaysisRunBuilder.addAnalyzer(CountDistinct([field_name]))
                    self._AnaysisRunBuilder.addAnalyzer(Histogram(field_name))
                # if this field is numeric type
                elif type_name in ["decimal", "double", "float"]:
                    self._AnaysisRunBuilder.addAnalyzer(ApproxQuantiles(field_name, quantiles=[0.25, 0.5, 0.75]))
                    self._AnaysisRunBuilder.addAnalyzer(Maximum(field_name))
                    self._AnaysisRunBuilder.addAnalyzer(Minimum(field_name))
                is_found = True
                break

        if not is_found:
            raise Exception(f"column name {column} not found.")
        return self
    
    def enable_visualize(self):
        # Note that visualization function hasn't been impplemented
        self.visualize = True
        return self
    
    def save_to(self, file_path):
        """Save analysis result as json file

        Note that this method will not imediately save file, it only provides
        file path. File will be saved after run() function.

        Args:
        file_path: str
            Where to save the json file.
        
        Returns:
        self: AnalyzeBuilder
            For further chained method calls.
        """
        self.save_file_path = file_path
        return self
    
    def run(self):
        """Run the analyze builder

        The above methods only add settings to the builder, this method actually
        runs analyzing and saves the result.

        Returns:
        analysis_result_df: DataFrame
            Analysis result as the DataFrame object.
        """
        analysis_result = self._AnaysisRunBuilder.run()
        analysis_result_df = AnalyzerContext.successMetricsAsDataFrame(self._spark_session, analysis_result)
        analysis_result_json = AnalyzerContext.successMetricsAsJson(self._spark_session, analysis_result)

        # save result as json file to the given path 
        if self.save_file_path != None:
            with open(self.save_file_path, 'w') as fp:
                fp.write(json.dumps(analysis_result_json, indent=4))

        # visualize the result
        if self.visualize == True:
            # visualize_analysis_result(analysis_result_df)
            pass

        return analysis_result_df


class QualityChecker:
    """Data quality checker

    This class is designed for data quality checking based on different databases
    like mysql, postgresql and bigQuery. It provides functions, include metrics analyzing,
    profile messages visualizing, constraint suggestion and constraint verification.

    Example:
    >>> checker = QualityChecker(spark_session)
    >>> analysis_result = checker.analyze(df, [DEFAULT, Mean("money")])
    >>> profile_result = checker.profile()

    Args:
    spark_session: SparkSession
        The spark session used to analyzing data.
    """

    def __init__(self, spark_session):
        self._spark_session = spark_session

    def analyze(self, 
                data_frame,
                metric_list: List[_AnalyzerObject],
                file_path=None, 
                visualize=False
            ) -> pd.DataFrame:
        """analyze default metrics on the data frame

        Example:
        >>> result = self.analyze(df)
        You will get analysis result on default metrics.
        Uniqueness metric on each String column, Mean metric on each Numeric column

        >>> result = self.analyze(df, 
                                [Completness("date"), Mean("money")], 
                                "analysis_result.json")
        You will get analysis result on the two metrics, the result will 
        also be saved to the analysis_result.json file

        >>> result = self.analyze(df, 
                                [DEFAULT, StandardDeviation("money")], 
                                visualize=True)
        You will get analysis result on default metrics and StandardDeviation metric,
        the result will be visualized.

        Args:
        data_frame: DataFrame
            The data frame to be analyzing.
        metric_list: List[_AnalyzerObject]
            Analyzers to be added to the dataframe
        file_path: String | None
            If not None, save the analysis result to a file.
        visualize: Boolean
            Enable visualization of analysis result.

        Returns:
        analysis_result: Pandas DataFrame
            The analysis result of default metric.
        """

        analyzer = AnalyzeBuilder(self._spark_session, data_frame)
        # add all analyzer object, including DEFAULT
        for analyzer_obj in metric_list:
            analyzer.add(analyzer_obj)
        # save to json file
        if file_path != None:
            analyzer.save_to(file_path)
        # visualize result
        if visualize != False:
            analyzer.enable_visualize()

        analysis_result = analyzer.run().toPandas()
        return analysis_result