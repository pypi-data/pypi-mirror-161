import copy
import json
import os
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Union

import oyaml as yaml

from fa_common import get_settings
from fa_common import logger as LOG
from fa_common.storage import File, get_storage_client

from .models import JobAction, JobRun, ScidraModule, WorkflowProject, WorkflowRun
from .utils import get_workflow_client

dirname = os.path.dirname(__file__)


async def create_workflow_project(user_id: str, project_name: str, bucket_id: str = None) -> WorkflowProject:
    client = get_workflow_client()
    try:
        project = await client._get_project_by_name(user_id)
    except ValueError:
        LOG.info(f"Workflow User {user_id} does not exist, creating.")
        project = await client.create_project(user_id)

    branch = await client.create_branch(project.id, project_name)

    return WorkflowProject(
        name=branch.name,
        user_id=user_id,
        bucket_id=bucket_id,
        gitlab_project_id=project.id,
        created=str(datetime.now()),
    )


async def delete_workflow_project(user_id: str, project_name: str):
    client = get_workflow_client()

    try:
        await client.delete_branch(user_id, project_name)
    except ValueError:
        LOG.error(f"Trying to delete workflow project {project_name} does not exist for user {user_id}.")
        raise ValueError(f"Workflow Project {project_name} does not exist.")


async def delete_workflow_user(user_id: str, wait: bool = False):
    client = get_workflow_client()
    try:
        await client.delete_project_by_name(user_id, wait)
    except ValueError:
        LOG.error(f"Workflow User {user_id} does not exist.")
        raise ValueError(f"Workflow User {user_id} does not exist.")


async def get_job_log(user_id: str, job_id: int) -> bytes:
    client = get_workflow_client()
    logs = await client.get_job_log(user_id, job_id)
    return logs


async def job_action(user_id: str, job_id: int, action: JobAction) -> Optional[JobRun]:
    client = get_workflow_client()
    return await client.job_action(user_id, job_id, action)


async def retry_workflow(user_id: str, workflow_id: int) -> WorkflowRun:
    client = get_workflow_client()
    return await client.retry_pipeline(user_id, workflow_id)


async def get_job_output(bucket_id: str, workflow_id: int, job_id: int) -> Union[dict, List, None]:
    # client = get_workflow_client()
    storage = get_storage_client()
    file = await storage.get_file(
        bucket_id,
        f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/outputs.json",
    )
    if file is None:
        return None
    return json.load(file)


async def get_job_file(
    bucket_id: str, workflow_id: int, job_id: int, filename: str, ref_only: bool = False
) -> Union[Optional[BytesIO], File]:
    storage = get_storage_client()
    if ref_only:
        return await storage.get_file_ref(
            bucket_id,
            f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/{filename}",
        )
    return await storage.get_file(
        bucket_id,
        f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/{filename}",
    )


async def get_job_file_refs(bucket_id: str, workflow_id: int, job_id: int) -> List[File]:
    storage = get_storage_client()
    return await storage.list_files(
        bucket_id,
        f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/",
    )


async def add_data_to_job(job: JobRun, bucket_id: str, output: bool = True, file_refs: bool = True) -> JobRun:
    if job.status == "success":
        if file_refs:
            job.files = await get_job_file_refs(bucket_id, job.workflow_id, job.id)
        if output and job.output is None:
            job.output = await get_job_output(bucket_id, job.workflow_id, job.id)
    return job


async def delete_workflow(user_id: str, bucket_id: str, workflow_id: int):
    client = get_workflow_client()
    await client.delete_pipeline(user_id, workflow_id)
    storage = get_storage_client()
    await storage.delete_file(bucket_id, f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id}", True)


async def run_job(
    project: WorkflowProject,
    description: str,
    module: ScidraModule,
    job_data: Union[dict, List[dict]],
    runner: str = "csiro-swarm",
    files: List[File] = [],
    sync: bool = False,
    upload: bool = True,
    upload_runner: str = None,
) -> WorkflowRun:

    settings = get_settings()
    file_refs = [_file.dict() for _file in files]
    with open(os.path.join(dirname, "job.yml")) as yaml_file:
        job_yaml = yaml.safe_load(yaml_file)

    if not isinstance(job_data, List):
        job_data = [job_data]

    job_yaml["run-job"]["tags"] = [runner]
    job_yaml["run-job"]["image"] = module.docker_image
    job_yaml["run-job"]["variables"]["TZ"] = project.timezone
    job_yaml["run-job"]["variables"]["FILE_REFS"] = json.dumps(file_refs)
    job_yaml["run-job"]["variables"]["MODULE_NAME"] = module.name
    job_yaml["run-job"]["variables"]["KUBERNETES_CPU_REQUEST"] = module.cpu_request
    job_yaml["run-job"]["variables"]["KUBERNETES_CPU_LIMIT"] = module.cpu_limit
    job_yaml["run-job"]["variables"]["KUBERNETES_MEMORY_REQUEST"] = f"{module.memory_request_gb}Gi"
    job_yaml["run-job"]["variables"]["KUBERNETES_MEMORY_LIMIT"] = f"{module.memory_limit_gb}Gi"

    if len(job_data) > 1:
        for i, params in enumerate(job_data):
            run_job_i = copy.deepcopy(job_yaml["run-job"])
            job_yaml[f"run-job{i}"] = run_job_i
            job_yaml[f"run-job{i}"]["variables"]["JOB_PARAMETERS"] = json.dumps(params)
        del job_yaml["run-job"]
    else:
        job_yaml["run-job"]["variables"]["JOB_PARAMETERS"] = json.dumps(job_data[0])

    if not upload:
        del job_yaml["upload-data"]
    else:
        upload_uri = get_storage_client().get_uri(project.bucket_id, settings.WORKFLOW_UPLOAD_PATH)
        job_yaml["upload-data"]["variables"]["UPLOAD_PATH"] = upload_uri
        if upload_runner is None:
            upload_runner = runner
        job_yaml["upload-data"]["tags"] = [runner]

    client = get_workflow_client()

    await client.update_ci(project.gitlab_project_id, project.name, job_yaml, description)
    workflow_run = await client.run_pipeline(
        project.gitlab_project_id, project.name, wait=sync, include_output=sync
    )
    if sync and upload:
        for job in workflow_run.jobs:
            await add_data_to_job(job, project.bucket_id, output=True, file_refs=True)
    return workflow_run


async def get_job_run(
    user_id: str,
    bucket_id: str,
    job_id: int,
    include_log: bool = False,
    output: bool = True,
    file_refs: bool = True,
) -> JobRun:
    client = get_workflow_client()
    job = await client.get_job(user_id, job_id, include_log, output)
    job = await add_data_to_job(job, bucket_id, output, file_refs)
    return job


async def get_workflow(
    user_id: str,
    bucket_id: str,
    workflow_id: int,
    output: bool = False,
    file_refs: bool = True,
) -> WorkflowRun:
    client = get_workflow_client()
    workflow = await client.get_pipeline(user_id, workflow_id, output)
    for job in workflow.jobs:
        job = await add_data_to_job(job, bucket_id, output, file_refs)
    return workflow
