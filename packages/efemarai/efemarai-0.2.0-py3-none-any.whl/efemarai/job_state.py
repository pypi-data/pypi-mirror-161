from enum import Enum


class JobState(Enum):
    """
    Possible Test Run, Baseline and Dataset States.
    """

    NotStarted = "NotStarted"
    Starting = "Starting"
    Evaluating = "Evaluating"
    Testing = "Testing"
    Loading = "Loading"
    DataLoaded = "Data Loaded"
    CalculatingMetadata = "Calculating Metadata"
    GeneratingReport = "Generating Report"
    Finished = "Finished"
    Failed = "Failed"
    Stopped = "Stopped"
