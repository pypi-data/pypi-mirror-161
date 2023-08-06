"""GraphQL Data models for the metadata store api."""
from dataclasses import dataclass
from os import environ

AUTH_TOKEN = environ.get("GQL_AUTH_TOKEN")


@dataclass
class RecipeRunMutation:
    """Dataclass used to hold a recipe run mutation record."""

    recipeRunId: int
    recipeRunStatusId: int
    authToken: str = AUTH_TOKEN


@dataclass
class RecipeRunStatusResponse:
    """Dataclass used to hold the response to a recipe run status query."""

    recipeRunStatusId: int


@dataclass
class RecipeRunStatusQuery:
    """Dataclass used to execute a recipe run status query."""

    recipeRunStatusName: str


@dataclass
class CreateRecipeRunStatusResponse:
    """Dataclass used to hold a recipe run status query response."""

    recipeRunStatus: RecipeRunStatusResponse


@dataclass
class RecipeRunStatusMutation:
    """Dataclass to hold a recipe run status mutation table."""

    recipeRunStatusName: str
    isComplete: bool
    recipeRunStatusDescription: str
    authToken: str = AUTH_TOKEN


@dataclass
class InputDatasetResponse:
    """Dataclass used to hold an input dataset query response."""

    inputDatasetId: int
    isActive: bool
    inputDatasetDocument: str


@dataclass
class RecipeInstanceResponse:
    """Dataclass used to hold a recipe instance query response."""

    inputDataset: InputDatasetResponse
    recipeId: int


@dataclass
class RecipeRunResponse:
    """Dataclass used to hold a recipe instance query response."""

    recipeInstance: RecipeInstanceResponse
    recipeInstanceId: int
    configuration: str = None


@dataclass
class RecipeRunQuery:
    """Dataclass used to execute a recipe run query."""

    recipeRunId: int


@dataclass
class DatasetCatalogReceiptAccountMutation:
    """
    Dataclass used to write the dataset_catalog_receipt_account record for the run.

    It sets an expected object count for a dataset so that dataset inventory creation
    doesn't happen until all objects are transferred and inventoried.
    """

    datasetId: str
    expectedObjectCount: int
    authToken: str = AUTH_TOKEN


@dataclass
class RecipeRunProvenanceMutation:
    """Dataclass used to hold a recipe run provenance mutation record."""

    inputDatasetId: int
    isTaskManual: bool
    recipeRunId: int
    taskName: str
    libraryVersions: str
    workflowVersion: str
    codeVersion: str = None
    authToken: str = AUTH_TOKEN


@dataclass
class QualityReportMutation:
    """Dataclass used to hold a quality report mutation record."""

    datasetId: str
    qualityReport: str  # JSON
    authToken: str = AUTH_TOKEN


@dataclass
class QualityReportQuery:
    """Query parameters for the metadata store endpoint qualityReports."""

    datasetId: str


@dataclass
class QualityReportResponse:
    """Query Response for the metadata store endpoint qualityReports."""

    qualityReportId: int
