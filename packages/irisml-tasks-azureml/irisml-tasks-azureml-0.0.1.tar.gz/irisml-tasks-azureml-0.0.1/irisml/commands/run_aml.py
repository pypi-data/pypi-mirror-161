import argparse
import logging
import os
import pathlib
from irisml.azureml import AMLJobManager, Job, JobEnvironment

logger = logging.getLogger(__name__)


def main():
    class KeyValuePairAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            assert len(values) == 1
            k, v = values[0].split('=', 1)
            d = getattr(namespace, self.dest)
            d[k] = v

    parser = argparse.ArgumentParser()
    parser.add_argument('job_filepath', type=pathlib.Path)
    parser.add_argument('--env', '-e', nargs=1, default={}, action=KeyValuePairAction)
    parser.add_argument('--cache_url', default=os.getenv('IRISML_CACHE_URL'))
    parser.add_argument('--no_cache', action='store_true')
    parser.add_argument('--include_local_tasks', '-l', nargs='?', const=pathlib.Path(), default=None, type=pathlib.Path)
    parser.add_argument('--custom_packages', '-p', nargs='+', default=[])
    parser.add_argument('--requirement', '-r', type=pathlib.Path)
    parser.add_argument('--extra_index_url')
    parser.add_argument('--no_wait', action='store_true')
    parser.add_argument('--compute_target', default=os.getenv('IRISML_AML_COMPUTE_TARGET'))
    parser.add_argument('--subscription_id', default=os.getenv('IRISML_AML_SUBSCRIPTION_ID'))
    parser.add_argument('--workspace', default=os.getenv('IRISML_AML_WORKSPACE_NAME'))
    parser.add_argument('--experiment', default=os.getenv('IRISML_AML_EXPERIMENT_NAME', 'irisml'))
    parser.add_argument('--base_docker_image')
    parser.add_argument('--base_docker_image_registry')

    args = parser.parse_args()

    envs = args.env
    if args.cache_url and not args.no_cache:
        if args.include_local_tasks:
            logger.warning("Cache is disabled since local tasks implementations are used.")
        else:
            envs['IRISML_CACHE_URL'] = args.cache_url

    job = Job(args.job_filepath, envs)
    if args.include_local_tasks:
        job.add_custom_tasks(args.include_local_tasks)

    custom_packages = args.custom_packages
    if args.requirement:
        custom_packages = custom_packages + args.requirement.read_text().splitlines()
    env = JobEnvironment(args.base_docker_image, args.base_docker_image_registry, custom_packages, args.extra_index_url)
    print(env)

    job_manager = AMLJobManager(args.subscription_id, args.workspace, args.experiment, args.compute_target)
    run = job_manager.submit(job, env)
    print(run)

    if not args.no_wait:
        run.wait_for_completion()
