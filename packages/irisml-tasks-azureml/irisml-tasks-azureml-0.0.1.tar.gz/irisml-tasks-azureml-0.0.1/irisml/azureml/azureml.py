import contextlib
import json
import pathlib
import shutil
import tempfile
import typing
import azureml.core
import pkg_resources
from irisml.core import JobDescription


class AMLJobManager:
    def __init__(self, subscription_id, workspace_name, experiment_name, compute_target_name):
        self._workspace = self._get_workspace(subscription_id, workspace_name)
        self._experiment = azureml.core.Experiment(workspace=self._workspace, name=experiment_name)
        self._compute_target_name = compute_target_name

    def _get_workspace(self, subscription_id, workspace_name):
        ws_dict = azureml.core.Workspace.list(subscription_id=subscription_id)
        workspaces = ws_dict.get(workspace_name)
        if not workspaces:
            raise RuntimeError(f"Workspace {workspace_name} is not found.")
        if len(workspaces) >= 2:
            raise RuntimeError("Multiple workspaces are found.")

        return workspaces[0]

    def _get_environment(self, job_env):
        env = azureml.core.environment.Environment(name='irisml')
        conda_dep = azureml.core.conda_dependencies.CondaDependencies()
        conda_dep.set_python_version('3.8')
        for package in job_env.pip_packages:
            conda_dep.add_pip_package(package)
        if job_env.extra_index_url:
            conda_dep.set_pip_option(f'--extra-index-url "{job_env.extra_index_url}"')
        env.python.conda_dependencies = conda_dep
        return env

    def _get_compute_target(self):
        if self._compute_target_name == 'local':
            return 'local'
        return azureml.core.compute.ComputeTarget(workspace=self._workspace, name=self._compute_target_name)

    def get_script_run_config(self, project_dir, job, job_env):
        return azureml.core.ScriptRunConfig(source_directory=project_dir, compute_target=self._get_compute_target(), environment=self._get_environment(job_env), command=job.command)

    def submit(self, job, job_env):
        with job.create_project_directory() as project_dir:
            script_run_config = self.get_script_run_config(project_dir, job, job_env)
            run = self._experiment.submit(config=script_run_config)
            return AzureMLRun(run)


class Job:
    def __init__(self, job_description_filepath: pathlib.Path, environment_variables: typing.Dict):
        # Check if the given file is a valid JobDescription
        job_description_dict = json.loads(job_description_filepath.read_text())
        job_description = JobDescription.from_dict(job_description_dict)
        if job_description is None:
            raise RuntimeError(f"The given file is not a valid job description: {job_description_filepath}")

        self._job_description_filepath = job_description_filepath
        self._environment_variables = environment_variables
        self._custom_task_relative_paths = []

    @property
    def name(self):
        return self._job_description_filepath.name

    @property
    def command(self):
        # AZURE_CLIENT_ID is for ManagedIdentity authentication.
        c = f'AZURE_CLIENT_ID=$DEFAULT_IDENTITY_CLIENT_ID irisml_run {self.name} -v'
        for key, value in self._environment_variables.items():
            c += f' -e {key}="{value}"'
        if self._custom_task_relative_paths:  # Add the current directory to PYTHONPATH so that the custom tasks can be loaded.
            c = 'PYTHONPATH=.:$PYTHONPATH ' + c
        return c

    def add_custom_tasks(self, tasks_dir: pathlib.Path):
        self._custom_task_relative_paths = [str(p.relative_to(tasks_dir)) for p in tasks_dir.rglob('*.py')]
        self._custom_task_dir = tasks_dir

    @contextlib.contextmanager
    def create_project_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            shutil.copy(self._job_description_filepath, temp_dir)
            for p in self._custom_task_relative_paths:
                if p.startswith('irisml/tasks'):
                    dest = temp_dir / p
                else:
                    dest = temp_dir / 'irisml' / 'tasks' / p

                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self._custom_task_dir / p, dest)
            yield temp_dir


class JobEnvironment:
    STANDARD_PACKAGES = ['irisml', 'irisml-tasks', 'irisml-tasks-training']

    def __init__(self, base_docker_image, base_docker_image_registry, custom_packages, extra_index_url=None):
        self._base_docker_image = base_docker_image
        self._base_docker_image_registry = base_docker_image_registry
        self._custom_packages = custom_packages
        self._extra_index_url = extra_index_url
        self._standard_packages = self._find_standard_packages()

    @property
    def base_docker_image(self):
        return self._base_docker_image and (self._base_docker_image, self._base_docker_image_registry)

    @property
    def pip_packages(self):
        return self._standard_packages + self._custom_packages

    @property
    def extra_index_url(self):
        return self._extra_index_url

    def _find_standard_packages(self) -> typing.Tuple[str, str]:
        # TODO: Get latest versions
        return sorted([w.project_name + '==' + w.version for w in pkg_resources.working_set if w.project_name in self.STANDARD_PACKAGES])

    def __str__(self):
        s = ''
        if self._base_docker_image:
            s += f'Base Docker: {self._base_docker_image}'
            if self._base_docker_image_registry:
                s += f' ({self._base_docker_image_registry})'
            s += '\n'
        s += f'Packages: {",".join(self.pip_packages)}'
        if self.extra_index_url:
            s += f'\nExtra index url: {self.extra_index_url}'
        return s


class AzureMLRun:
    def __init__(self, run):
        self._run = run

    def wait_for_completion(self):
        return self._run.wait_for_completion(show_output=True)

    def get_portal_url(self):
        return self._run.get_portal_url()

    def __str__(self):
        return f'AzureML Run(id={self._run.id}, url={self._run.get_portal_url()}'
