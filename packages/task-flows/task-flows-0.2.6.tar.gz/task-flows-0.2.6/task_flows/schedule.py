from .containers import create_docker_container, remove_docker_container
from .models import ScheduledTask
from .systemd import create_scheduled_service, disable_service, enable_task


def create_scheduled_task(config: ScheduledTask):
    create_docker_container(config.task_name, config.container)
    create_scheduled_service(config.task_name, config.start_timer, config.stop_timer)


def remove_scheduled_task(task_name: str):
    remove_docker_container(task_name)
    disable_service(task_name=task_name, remove_files=True)


def enable_scheduled_task(task_name: str):
    enable_task(task_name)


def disable_scheduled_task(task_name: str):
    disable_service(task_name=task_name, remove_files=False)
