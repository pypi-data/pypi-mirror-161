# Vivqu: Data Quality Check For Post Monitoring

## 1. Environment Requirement
Use `pip install pydeequ` or `conda install pydeequ` to install pydeequ.

Latest pydeequ (version = 1.0.1) only support pyspark version = 3.0, 2.6, 2.4. Make sure that your pyspark version meet the requirement.

## 2. Project Background:
Feature quality is of great important to machine learing model performance, in order to insure the intactness of data that come from multiple upstream data sources, I deviced a data quality checking library for post monitoring, which is named **vivqu**. 

Based on PyDeequ, it gives data scientists deep insight into the data quality, and enable them to check whichever metrics they are insterested in. It also simplifies the intricate process when using PyDeequ directly and make users able to do the checking job within a few lines of code.

Vivqu consists of several parts:
1. QualityChecker: provides several interfaces to measure the quality of current dataframe.
2. DataLoader: provides different ways to load data from multiple sources.
3. Visualizer: provides visualization for analysis or profile results.

## 3. Example with Jupyter Notebook

Import all needed modules.
```python
import pyspark
from pyspark.sql import SparkSession
import pydeequ
from pydeequ.analyzers import *
from vivqu import *
```

Create a spark session locally, note that this may take a long time on the first run.
You can also use a remote spark session.

```python
spark_session = (
    SparkSession.builder
    .config("spark.jars.packages", pydeequ.deequ_maven_coord)
    .config("spark.jars.excludes", pydeequ.f2j_maven_coord)
    .getOrCreate()
    )
```

Create quality checker by providing it with a spark session.

```python
checker = QualityChecker(spark_session)
```

Load data frame from a sample csv file.

```python
loader = DataLoader(spark_session)
df = loader.load_csv("sample.csv")
df.printSchema()
```

Use default setting to analyze.

```python
result = checker.analyze(df)
result.show()
```

Customize analyzer by adding some self-defined metrics and run.

```python
result = checker.analyze(df,
            [Size(), Completeness("date"), Mean("money")]
        )
result.show()
```

use default setting and one customized metric to analyze and save the result to json file
```python
result = checker.analyze(df, 
            [DEFAULT, StandardDeviation("money")], 
            "analysis_result.json"
        )
result.show()
```

Print profile message and save it to a json file
```python
profile = checker.profile(df, "profile_result.json")
print(json.dumps(profile, indent=4))
```


## 4. Metrics Explanation:

### (1) analyzer metrics

Here are the detailed explanation and example of all provided metrics. You can add them by using checker.analyze([Metric1(Column1), Metric2[Column2], ...])

Reference: https://aws.amazon.com/cn/blogs/big-data/test-data-quality-at-scale-with-deequ/

| Metric | Description | Example |
| ----   | -----       | ----    |
|ApproxCountDistinct | Approximate number of distinct value, computed with HyperLogLogPlusPlus sketches. | `ApproxCountDistinct("review_id")` |
| ApproxQuantile | Approximate quantile of a distribution. | `ApproxQuantile("star_rating", quantile = 0.5)`
| ApproxQuantiles | Approximate quantiles of a distribution. | `ApproxQuantiles("star_rating", quantiles = Seq(0.1, 0.5, 0.9))`
| Completeness | Fraction of non-null values in a column. | `Completeness("review_id")`
| Compliance | Compliance | `Compliance("top star_rating", "star_rating >= 4.0")`
| Correlation | Pearson correlation coefficient, measures the linear correlation between two columns. The result is in the range [-1, 1], where 1 means positive linear correlation, -1 means negative linear correlation, and 0 means no correlation.| `Correlation("total_votes", "star_rating")`
| CountDistinct| Number of distinct values.| `CountDistinct("review_id")`
| DataType | Distribution of data types such as Boolean, Fractional, Integral, and String. The resulting histogram allows filtering by relative or absolute fractions. | `DataType("year")`
| Distinctness | Fraction of distinct values of a column over the number of all values of a column. Distinct values occur at least once. Example: [a, a, b] contains two distinct values a and b, so distinctness is 2/3. | `Distinctness("review_id")`
| Entropy | Entropy is a measure of the level of information contained in an event (value in a column) when considering all possible events (values in a column). It is measured in nats (natural units of information). Entropy is estimated using observed value counts as the negative sum of (value_count/total_count) * log(value_count/total_count). Example: [a, b, b, c, c] has three distinct values with counts [1, 2, 2]. Entropy is then (-1/5\*log(1/5)-2/5\*log(2/5)-2/5\*log(2/5)) = 1.055. | `Entropy("star_rating")`
| Maximum | Maximum value. | `Maximum("star_rating")`
| Mean | Mean value; null values are excluded. | `Mean("star_rating")`
| Minimum | Minimum value. | `Minimum("star_rating")`
| MutualInformation | Mutual information describes how much information about one column (one random variable) can be inferred from another column (another random variable). If the two columns are independent, mutual information is zero. If one column is a function of the other column, mutual information is the entropy of the column. Mutual information is symmetric and nonnegative. | `MutualInformation(Seq("total_votes", "star_rating"))`
| PatternMatch | Fraction of rows that comply with a given regular experssion. | `PatternMatch("marketplace", pattern = raw"\w{2}".r)`
| Size | Number of rows in a DataFrame. | `Size()`
| Sum | Sum of all values of a column.| `Sum("total_votes")`
| UniqueValueRatio | Fraction of unique values over the number of all distinct values of a column. Unique values occur exactly once; distinct values occur at least once. Example: [a, a, b] contains one unique value b, and two distinct values a and b, so the unique value ratio is 1/2. | `UniqueValueRatio("star_rating")`
| Uniqueness | Fraction of unique values over the number of all values of a column. Unique values occur exactly once. Example: [a, a, b] contains one unique value b, so uniqueness is 1/3. | `Uniqueness("star_rating")`

### (2) profile metrics

Include `Completness`, `approximateNumDistincValues`, `dataType`, `isDataTypeInferred`, `typeCounts`, `histgram` metrics for values of all types.

Include extra `kll`, `mean`, `maximum`, `minimum`, `sum`, `stdDev`, `approxPercentiles` metrics for 
Numeric values.