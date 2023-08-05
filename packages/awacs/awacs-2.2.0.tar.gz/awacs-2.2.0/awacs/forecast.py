# Copyright (c) 2012-2021, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from .aws import Action as BaseAction
from .aws import BaseARN

service_name = "Amazon Forecast"
prefix = "forecast"


class Action(BaseAction):
    def __init__(self, action: str = None) -> None:
        super().__init__(prefix, action)


class ARN(BaseARN):
    def __init__(self, resource: str = "", region: str = "", account: str = "") -> None:
        super().__init__(
            service=prefix, resource=resource, region=region, account=account
        )


CreateAutoPredictor = Action("CreateAutoPredictor")
CreateDataset = Action("CreateDataset")
CreateDatasetGroup = Action("CreateDatasetGroup")
CreateDatasetImportJob = Action("CreateDatasetImportJob")
CreateExplainability = Action("CreateExplainability")
CreateExplainabilityExport = Action("CreateExplainabilityExport")
CreateForecast = Action("CreateForecast")
CreateForecastExportJob = Action("CreateForecastExportJob")
CreateMonitor = Action("CreateMonitor")
CreatePredictor = Action("CreatePredictor")
CreatePredictorBacktestExportJob = Action("CreatePredictorBacktestExportJob")
DeleteDataset = Action("DeleteDataset")
DeleteDatasetGroup = Action("DeleteDatasetGroup")
DeleteDatasetImportJob = Action("DeleteDatasetImportJob")
DeleteExplainability = Action("DeleteExplainability")
DeleteExplainabilityExport = Action("DeleteExplainabilityExport")
DeleteForecast = Action("DeleteForecast")
DeleteForecastExportJob = Action("DeleteForecastExportJob")
DeleteMonitor = Action("DeleteMonitor")
DeletePredictor = Action("DeletePredictor")
DeletePredictorBacktestExportJob = Action("DeletePredictorBacktestExportJob")
DeleteResourceTree = Action("DeleteResourceTree")
DescribeAutoPredictor = Action("DescribeAutoPredictor")
DescribeDataset = Action("DescribeDataset")
DescribeDatasetGroup = Action("DescribeDatasetGroup")
DescribeDatasetImportJob = Action("DescribeDatasetImportJob")
DescribeExplainability = Action("DescribeExplainability")
DescribeExplainabilityExport = Action("DescribeExplainabilityExport")
DescribeExplainablity = Action("DescribeExplainablity")
DescribeForecast = Action("DescribeForecast")
DescribeForecastExportJob = Action("DescribeForecastExportJob")
DescribeMonitor = Action("DescribeMonitor")
DescribePredictor = Action("DescribePredictor")
DescribePredictorBacktestExportJob = Action("DescribePredictorBacktestExportJob")
GetAccuracyMetrics = Action("GetAccuracyMetrics")
ListDatasetGroups = Action("ListDatasetGroups")
ListDatasetImportJobs = Action("ListDatasetImportJobs")
ListDatasets = Action("ListDatasets")
ListExplainabilities = Action("ListExplainabilities")
ListExplainabilityExports = Action("ListExplainabilityExports")
ListForecastExportJobs = Action("ListForecastExportJobs")
ListForecasts = Action("ListForecasts")
ListMonitorEvaluations = Action("ListMonitorEvaluations")
ListMonitors = Action("ListMonitors")
ListPredictorBacktestExportJobs = Action("ListPredictorBacktestExportJobs")
ListPredictors = Action("ListPredictors")
ListTagsForResource = Action("ListTagsForResource")
QueryForecast = Action("QueryForecast")
ResumeResource = Action("ResumeResource")
StopResource = Action("StopResource")
TagResource = Action("TagResource")
UntagResource = Action("UntagResource")
UpdateDatasetGroup = Action("UpdateDatasetGroup")
