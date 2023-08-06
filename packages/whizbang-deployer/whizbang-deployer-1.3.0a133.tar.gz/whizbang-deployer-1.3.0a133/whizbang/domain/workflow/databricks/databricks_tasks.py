import abc
import tempfile

import requests

from whizbang.core.workflow_task import WorkflowTask, IWorkflowTask
from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.manager.databricks.databricks_cluster_manager import IDatabricksClusterManager
from whizbang.domain.manager.databricks.databricks_job_manager import IDatabricksJobManager
from whizbang.domain.manager.databricks.databricks_library_manager import IDatabricksLibraryManager
from whizbang.domain.manager.databricks.databricks_secret_scope_manager import IDatabricksSecretScopeManager
from whizbang.domain.manager.databricks.databricks_sql_endpoint_manager import DatabricksSqlEndpointManager
from whizbang.domain.manager.databricks.databricks_workspace_manager import IDatabricksWorkspaceManager
from whizbang.domain.manager.databricks.databricks_pool_manager import IDatabricksPoolManager
from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.models.databricks.databricks_job import DatabricksJob
from whizbang.domain.models.databricks.databricks_library import DatabricksLibrary
from whizbang.domain.models.databricks.databricks_notebook import DatabricksNotebook
from whizbang.domain.models.databricks.databricks_pool import DatabricksPool
from whizbang.domain.models.databricks.databricks_sql_endpoint import DatabricksSqlEndpoint
from whizbang.domain.models.databricks.databricks_state import DatabricksState
from whizbang.domain.workflow.verify_deployed_workflow_task import VerifyDeployedWorkflowTask
from whizbang.util.logger import logger


class IDatabricksTask(IWorkflowTask):

    @abc.abstractmethod
    def run(self, request: DatabricksState):
        """"""


class CreatePoolsTask(VerifyDeployedWorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksPoolManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_pools"

    def run(self, request: DatabricksState):
        logger.info("Deploying Databricks Pools")

        def __run(request: DatabricksState):
            for pool_json in request.pool_state:
                try:
                    self.manager.save(request.client, DatabricksPool(pool_json))
                except KeyError as e:
                    logger.exception(f'pool json not properly formatted: {e}')
                    raise e

        self.verify_deployed(callback=__run, resource_name="Databricks Workspace", timeout_seconds=300, request=request)


class UpdateClusterSecretScopeTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksSecretScopeManager, account_manager: AzAccountManager):
        WorkflowTask.__init__(self)
        self.manager = manager
        self.account_manager = account_manager

    @property
    def task_name(self) -> str:
        return "set cluster secret scope"

    def run(self, request: DatabricksState):
        logger.info("Updating Cluster Secret Scope")
        if self.account_manager.get_account().account_type.lower() == 'serviceprincipal':
            logger.warning(
                'A service principal cannot create a databricks secret scope, skipping secret scope creation...')
            return
        self.manager.save(client_args=request.client, t_object=request.secret_scope)


class UpdateUniversalClusterFieldsTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksClusterManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    """At the moment we only need universal env variables. Variables specific to a named cluster will need a new 
    task. """

    @property
    def task_name(self) -> str:
        return "update_universal_cluster_env_variables"

    def run(self, request: DatabricksState):
        logger.info("Updating Databricks Cluster Environment Variables")
        for cluster_json in request.cluster_state:
            self.manager.update_cluster_env_variables(cluster_fields=request.new_cluster_fields,
                                                      cluster=DatabricksCluster(cluster_json))


class CreateClustersTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksClusterManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_clusters"

    def run(self, request: DatabricksState):
        logger.info("Deploying Databricks Clusters")
        for cluster_json in request.cluster_state:
            try:
                self.manager.save(request.client, DatabricksCluster(cluster_json))
            except KeyError as e:
                logger.exception(f'cluster json not properly formatted: {e}')
                raise e
            except requests.HTTPError as e:
                logger.exception(f'cluster {cluster_json.get("cluster_name")} could not be started: {e}')
                raise e


class PinClustersTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksClusterManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "pin_clusters"

    def run(self, request: DatabricksState):
        logger.info("Pinning Databricks Clusters")
        for cluster_json in request.cluster_state:
            try:
                self.manager.pin_cluster(client_args=request.client, cluster=DatabricksCluster(cluster_json))
            except KeyError as e:
                logger.exception(f'cluster json not properly formatted: {e}')
                raise e


class CreateNotebooksTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksWorkspaceManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_notebooks"

    def run(self, request: DatabricksState) -> any:
        logger.info("Deploying Databricks Notebooks")
        self.manager.save(request.client, DatabricksNotebook(source_path=request.notebook_state, target_path=request.notebook_target_path))


class CreateLibrariesTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksLibraryManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_libraries"

    def run(self, request: DatabricksState) -> any:
        logger.info("Deploying Databricks Libraries")
        for library in request.universal_library_state:
            try:
                self.manager.save(request.client, DatabricksLibrary(library_dict=library, install_all=True))
            except KeyError as e:
                logger.exception(f'all cluster library json not properly formatted: {e}')
                raise e
            except requests.HTTPError as e:
                logger.exception(f'{library} could not be installed on all clusters: {e}')
                raise e
        for target_cluster_libraries in request.library_state:
            try:
                self.manager.save(request.client, DatabricksLibrary(library_dict=target_cluster_libraries))
            except KeyError as e:
                logger.exception(f'library json not properly formatted: {e}')
                raise e
            except requests.HTTPError as e:
                logger.exception(f'libraries could not be installed on'
                                 f' {target_cluster_libraries["cluster_name"]}: {e}')
                raise e


class CreateJobsTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: IDatabricksJobManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_jobs"

    def run(self, request: DatabricksState):
        logger.info("Deploying Databricks Jobs")
        for job_json in request.job_state:
            try:
                self.manager.save(request.client, DatabricksJob(job_json['settings']))
            except KeyError as e:
                logger.exception(f'job json not properly formatted: {e}')
                raise e
            except requests.HTTPError as e:
                logger.exception(f'{job_json["settings"]["name"]} could not be installed on the cluster'
                                 f' {job_json["settings"]["existing_cluster_name"]}: {e}')
                raise e


class CreateSqlEndpointsTask(WorkflowTask, IDatabricksTask):
    def __init__(self, manager: DatabricksSqlEndpointManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_sql_endpoints"

    def run(self, request: DatabricksState):
        logger.info("Deploying Databricks Sql Endpoints")
        for sql_endpoint in request.sql_endpoint_state:
            try:
                return self.manager.save(client_args=request.client, t_object=DatabricksSqlEndpoint(sql_endpoint))
            except requests.HTTPError as e:
                logger.warning(f'Create sql endpoint failed with error {e}')
