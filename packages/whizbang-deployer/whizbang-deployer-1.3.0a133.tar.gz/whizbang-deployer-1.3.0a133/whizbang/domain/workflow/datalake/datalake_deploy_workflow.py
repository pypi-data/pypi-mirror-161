from whizbang.core.workflow import Workflow, IWorkflow
from whizbang.core.workflow_task import IWorkflowTask
from whizbang.domain.workflow.datalake.datalake_task import ApplyDatalakeAclTask, CreateDatalakeFoldersTask, \
    RemoveDatalakeAclTask, CreateDatalakeFileSystemTask


class IDatalakeDeployWorkflow(IWorkflow):
    """"""


class DatalakeDeployWorkflow(Workflow, IDatalakeDeployWorkflow):
    def __init__(self, create_datalake_file_system_task: CreateDatalakeFileSystemTask,
                 apply_datalake_acl_task: ApplyDatalakeAclTask,
                 create_datalake_folders_task: CreateDatalakeFoldersTask,
                 remove_datalake_acl_task: RemoveDatalakeAclTask):
        self.create_datalake_file_system_task = create_datalake_file_system_task
        self.apply_datalake_acl_task = apply_datalake_acl_task
        self.create_datalake_folders_task = create_datalake_folders_task
        self.remove_datalake_acl_task = remove_datalake_acl_task

    def _get_workflow_tasks(self) -> 'list[IWorkflowTask]':
        workflow: list[IWorkflowTask] = [self.create_datalake_file_system_task,
                                         self.apply_datalake_acl_task,
                                         self.create_datalake_folders_task,
                                         self.remove_datalake_acl_task]
        return workflow
