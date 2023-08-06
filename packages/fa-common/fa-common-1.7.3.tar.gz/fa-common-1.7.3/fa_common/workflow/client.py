import json
import time
from collections.abc import Iterable
from typing import Dict, List, Optional, Union

import yaml
from gitlab import Gitlab
from gitlab.exceptions import GitlabCreateError, GitlabDeleteError, GitlabGetError, GitlabJobRetryError
from gitlab.v4.objects import Project, ProjectJob, ProjectPipeline

from fa_common import force_async, get_current_app, get_settings
from fa_common import logger as LOG

from .models import JobAction, JobRun, WorkflowRun
from .utils import GitlabCIYAMLDumper


class GitlabClient:
    """
    Singleton client for interacting with gitlab.
    Is a wrapper over the existing gitlab python client to provide specialist functions for the Job/Module
    workflow.

    Please don't use it directly, use `fa_common.workflow.utils.get_workflow_client`.
    """

    __instance = None
    gitlab: Gitlab

    def __new__(cls) -> "GitlabClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.gitlab = app.gitlab  # type: ignore
        return cls.__instance

    async def project_exists(self, project_id: Union[int, str]) -> bool:
        try:
            self._get_project(project_id)
        except ValueError:
            return False
        return True

    async def _get_project(self, project_id: Union[int, str]) -> Project:
        if isinstance(project_id, int):
            try:
                project = await force_async(self.gitlab.projects.get)(project_id)
            except GitlabGetError:
                raise ValueError(f"No project found with the id {project_id}")
            return project
        else:
            return await self._get_project_by_name(project_id)

    async def _get_project_by_name(self, project_name: str):
        settings = get_settings()
        projects = await force_async(self.gitlab.projects.list)(search=project_name, owned=True)
        for proj in projects:
            group_id = proj.namespace["id"]
            if proj.name == project_name and group_id == settings.GITLAB_GROUP_ID:
                return proj
        raise ValueError(f"No project found with the name {project_name}")

    async def create_project(self, project_name: str) -> int:
        settings = get_settings()
        try:
            project = await force_async(self.gitlab.projects.create)(
                {
                    "name": project_name,
                    "namespace_id": settings.GITLAB_GROUP_ID,
                    "auto_cancel_pending_pipelines": "disabled",
                }
            )
        except GitlabCreateError as err:
            LOG.warning(f"Create Error caught, retrying in 5 secs: {err}")
            time.sleep(5)
            project = await force_async(self.gitlab.projects.create)(
                {"name": project_name, "namespace_id": settings.GITLAB_GROUP_ID}
            )

        LOG.info(f"Created CI Project: {project.id}")
        LOG.debug(f"{project}")

        data = {
            "branch": "master",
            "commit_message": "First Commit",
            "actions": [{"action": "create", "file_path": ".gitlab-ci.yml", "content": ""}],
        }
        commit = await force_async(project.commits.create)(data)
        LOG.info(f"Created CI Commit: {commit.id}")
        LOG.debug(f"{commit}")

        return project

    async def create_branch(self, project_id: int, branch_name: str):
        project = await self._get_project(project_id)
        branch = await force_async(project.branches.create)({"branch": branch_name, "ref": "master"})
        LOG.info(f"Created branch: {branch}")
        return branch

    async def delete_branch(self, project_id: int, branch_name: str):
        project = await self._get_project(project_id)
        try:
            await force_async(project.branches.delete)(branch_name)
            LOG.info(f"Deleted branch: {branch_name}")
        except GitlabDeleteError as err:
            if str(err.response_code) == "404":
                raise ValueError(f"Trying to delete branch {branch_name} that doesn't exist.")
            raise err

    async def get_job(
        self,
        project_id: Union[str, int],
        job_id: int,
        include_log: bool = False,
        include_output=False,
    ) -> JobRun:
        project = await self._get_project(project_id)
        try:
            job = await force_async(project.jobs.get)(job_id)
            log = None
            if include_log:
                log = job.trace()
        except GitlabGetError:
            raise ValueError(f"No job found with the id {job_id} in project {project_id}")

        return self.job_to_job_run(job, log, include_output)

    async def get_job_log(self, project_id: Union[str, int], job_id: int) -> bytes:
        project = await self._get_project(project_id)
        job = await force_async(project.jobs.get)(job_id)
        return job.trace()

    async def update_ci(
        self,
        project_id: Union[str, int],
        branch_name: str,
        ci_file: dict,
        update_message: str = "No message",
    ):
        project = await self._get_project(project_id)
        data = {
            "branch": branch_name,
            "commit_message": update_message,
            "actions": [
                {
                    "action": "update",
                    "file_path": ".gitlab-ci.yml",
                    "content": yaml.dump(ci_file, Dumper=GitlabCIYAMLDumper, default_flow_style=False),
                }
            ],
        }
        commit = await force_async(project.commits.create)(data)
        LOG.info(f"Created CI Commit: {commit.id}")
        LOG.debug(f"{commit}")

        return commit.id

    async def run_pipeline(
        self,
        project_id: Union[str, int],
        branch: str,
        variables: List[dict] = None,
        wait: bool = False,
        include_output: bool = False,
    ) -> WorkflowRun:
        project = await self._get_project(project_id)
        pipeline = project.pipelines.create({"ref": branch, "variables": variables})
        if wait:
            while pipeline.finished_at is None:
                LOG.info(f"Waiting for workflow {pipeline.id} to finish, sleeping for 5 seconds")
                time.sleep(5)
                pipeline.refresh()

        return await self.pipeline_to_workflow_run(pipeline, project, include_output)

    def job_to_job_run(
        self,
        job: ProjectJob,
        job_log: bytes = None,
        include_output: bool = True,
    ) -> JobRun:
        output = None
        if include_output and hasattr(job, "artifacts_file") and job.artifacts_file is not None:
            try:
                output_bytes = None
                output_bytes = job.artifact(f"output/{job.id}/outputs.json")
                if output_bytes is not None:
                    output = json.loads(output_bytes)
                    if isinstance(output, Iterable):
                        output = list(output)
            except Exception as err:
                LOG.error(err)

        job_run = JobRun(
            id=job.id,
            workflow_id=job.pipeline["id"],
            workflow_status=job.pipeline["status"],
            status=job.status,
            started_at=job.started_at,
            finished_at=job.finished_at,
            duration=job.duration,
            name=job.name,
            stage=job.stage,
            output=output,
        )
        if job_log is not None:
            job_run.log = job_log

        return job_run

    async def pipeline_to_workflow_run(
        self,
        pipeline: ProjectPipeline,
        project: Project,
        include_output: bool = False,
    ) -> WorkflowRun:
        hidden_jobs: List[JobRun] = []
        jobs = await force_async(pipeline.jobs.list)()
        job_dict: Dict[str, JobRun] = {}
        for job in jobs:
            project_job = project.jobs.get(job.id)
            job_run = self.job_to_job_run(project_job, include_output=include_output)
            if job_dict.get(job_run.name) is not None:
                if job_dict[job_run.name].get_compare_time() < job_run.get_compare_time():
                    hidden_jobs.append(job_dict[job_run.name])
                    job_dict[job_run.name] = job_run
                else:
                    hidden_jobs.append(job_run)
            else:
                job_dict[job_run.name] = job_run

        return WorkflowRun(
            id=pipeline.id,
            gitlab_project_id=project.id,
            gitlab_project_branch=pipeline.ref,
            commit_id=pipeline.sha,
            status=pipeline.status,
            started_at=pipeline.started_at,
            finished_at=pipeline.finished_at,
            duration=pipeline.duration,
            jobs=list(job_dict.values()),
            hidden_jobs=hidden_jobs,
        )

    async def delete_project(self, project_id: int, wait: bool = True):
        await force_async(self.gitlab.projects.delete)(project_id)
        if wait:
            try:
                proj = await self._get_project(project_id)
                while proj is not None:
                    LOG.info(f"Waiting for project {project_id} to delete")
                    time.sleep(2)
                    proj = await self._get_project(project_id)
            except ValueError:
                LOG.info(f"Project {project_id} successfully deleted")
                return

    async def delete_project_by_name(self, project_name: str, wait: bool = True):
        settings = get_settings()
        projects = await force_async(self.gitlab.projects.list)(search=project_name, owned=True)
        LOG.info(f"Found projects: {projects}")
        for proj in projects:
            group_id = proj.namespace["id"]
            LOG.info(f"Checking project: {proj.id}, {proj.name}, {group_id}")
            if proj.name == project_name and group_id == settings.GITLAB_GROUP_ID:
                LOG.info(f"Deleting project: {proj.id}")
                await self.delete_project(proj.id, wait)
                return
        raise ValueError(f"No project found with the name {project_name}")

    async def job_action(
        self, project_id: Union[str, int], job_id: int, action: JobAction
    ) -> Optional[JobRun]:
        project = await self._get_project(project_id)
        try:
            job = await force_async(project.jobs.get)(job_id)
            if action is JobAction.PLAY:
                await force_async(job.play)()
            elif action is JobAction.CANCEL:
                await force_async(job.cancel)()
            elif action is JobAction.RETRY:
                await force_async(job.retry)()
                pipeline = await force_async(project.pipelines.get)(job.pipeline["id"])
                jobs = await force_async(pipeline.jobs.list)()
                for _job in jobs:
                    if _job.name == job.name and _job.status in ["pending", "running"] and _job.id != job.id:
                        job = _job
                        break

            elif action is JobAction.DELETE:
                await force_async(job.delete)()
                return None
            job = await force_async(project.jobs.get)(job.id)
            return self.job_to_job_run(job, include_output=False)
        except GitlabGetError:
            raise ValueError(f"No job found with the id {job_id} in project {project_id}")
        except GitlabJobRetryError:
            raise ValueError(f"Job {job_id} is not currently retryable.")

    async def get_pipeline(
        self, project_id: Union[str, int], pipeline_id: int, include_output: bool
    ) -> WorkflowRun:
        project = await self._get_project(project_id)
        try:
            pipeline = await force_async(project.pipelines.get)(pipeline_id)
            return await self.pipeline_to_workflow_run(pipeline, project, include_output)
        except GitlabGetError:
            raise ValueError(f"No pipeleine found with the id {pipeline_id} in project {project_id}")

    async def retry_pipeline(self, project_id: Union[str, int], pipeline_id: int) -> WorkflowRun:
        project = await self._get_project(project_id)
        try:
            pipeline = await force_async(project.pipelines.get)(pipeline_id)
            await force_async(pipeline.retry)()
            return await self.pipeline_to_workflow_run(pipeline, project, False)
        except GitlabGetError:
            raise ValueError(f"No pipeleine found with the id {pipeline_id} in project {project_id}")

    async def delete_pipeline(self, project_id: Union[str, int], pipeline_id: int):
        project = await self._get_project(project_id)
        try:
            pipeline = await force_async(project.pipelines.get)(pipeline_id)
            if pipeline.status in ["running", "pending"]:
                await force_async(pipeline.cancel)()
            await force_async(pipeline.delete)()
        except GitlabGetError:
            raise ValueError(f"No pipeline found with the id {pipeline_id} in project {project_id}")
