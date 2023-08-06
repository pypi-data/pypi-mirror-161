from functools import cache
from pprint import pformat

import docker
from docker.models.containers import Container as DockerContainer

from .models import Container
from .utils import logger


@cache
def get_docker_client():
    return docker.DockerClient(base_url="unix:///var/run/docker.sock")


def remove_docker_container(task_name: str, warn_on_error: bool = True):
    try:
        get_docker_client().containers.get(task_name).remove()
        logger.info(f"Removed Docker container: {task_name}")
    except docker.errors.NotFound:
        if warn_on_error:
            logger.error(
                f"Could not remove docker container '{task_name}'. Container not found."
            )


def create_docker_container(task_name: str, container: Container) -> DockerContainer:
    """Create a Docker container for running a script.

    Args:
        task_name (str): Name of the task the container is for.
        container (Container): container for the task.

    Returns:
        Container: The created Docker container.
    """
    # remove any existing container with this name.
    remove_docker_container(task_name, warn_on_error=False)
    kwargs = {k: v for k, v in container.dict().items() if v is not None}
    if env := {**kwargs.pop("env_file", {}), **kwargs.pop("env", {})}:
        kwargs["environment"] = env
    kwargs["name"] = task_name
    kwargs["detach"] = True
    if " " in container.command:
        kwargs["command"] = container.command.split()
    if container.ulimits:
        kwargs["ulimits"] = [
            docker.types.Ulimit(name=l.name, soft=l.soft, hard=l.hard)
            for l in container.ulimits
        ]
    if container.volumes:
        kwargs["volumes"] = {
            v.host_path: {
                "bind": v.container_path,
                "mode": "ro" if v.read_only else "rw",
            }
            for v in container.volumes
        }
    logger.info(f"Creating Docker container for {task_name}:\n{pformat(kwargs)}")
    return get_docker_client().containers.create(**kwargs)
