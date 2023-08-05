from enum import Enum

API_TOKEN_HEADER = "Dagster-Cloud-Api-Token"

DEPLOYMENT_NAME_HEADER = "Dagster-Cloud-Deployment"

DAGSTER_CLOUD_SCOPE_HEADER = "Dagster-Cloud-Scope"


class DagsterCloudInstanceScope(Enum):
    ORGANIZATION = "organization"
    DEPLOYMENT = "deployment"
    UNSCOPED = "unscoped"
