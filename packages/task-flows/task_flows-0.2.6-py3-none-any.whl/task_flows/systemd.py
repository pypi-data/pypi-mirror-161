from pathlib import Path
from subprocess import run
from textwrap import dedent
from typing import Optional, Sequence

from .models import Timer
from .utils import logger, systemctl, systemd_dir


def enable_task(stem: str):
    systemctl("enable", "--now", f"{stem}.timer")


def create_scheduled_service(
    task_name: str,
    start_timer: Sequence[Timer],
    stop_timer: Optional[Sequence[Timer]] = None,
):
    """Install and enable a systemd service and timer.

    Args:
        task_name (str): Name of task service should be created for.
    """
    systemd_dir.mkdir(parents=True, exist_ok=True)

    def create_systemd_files(timer: Sequence[Timer], stem: str, docker_action: str):
        # create timer file.
        timer = "\n".join(
            [
                "[Unit]",
                f"Description={docker_action} timer for task {task_name}.",
                "[Timer]",
                *[f"{t.option.value}={t.value}" for t in timer],
                "Persistent=true",
                "[Install]",
                "WantedBy=timers.target",
            ]
        )
        systemd_dir.joinpath(f"{stem}.timer").write_text(timer)
        logger.info(f"Installed Systemd timer for {task_name}:\n{timer}")
        service = dedent(
            f"""
            [Unit]
            Description={docker_action} service for task {task_name}.
            After=network.target
            
            [Service]
            Type=simple
            ExecStart=docker {docker_action} {task_name}
            
            [Install]
            WantedBy=multi-user.target
            """
        )
        systemd_dir.joinpath(f"{stem}.service").write_text(service)
        logger.info(f"Installed Systemd service for {task_name}:\n{service}")

    create_systemd_files(start_timer, f"task_flow_{task_name}", "start")
    enable_task(f"task_flow_{task_name}")
    if stop_timer:
        create_systemd_files(stop_timer, f"task_flow_{task_name}_stop", "stop")
        enable_task(f"task_flow_{task_name}_stop")
    # make sure updated service is recognized.
    systemctl("daemon-reload")


def disable_service(task_name: Path, remove_files: bool):
    srv_files = [systemd_dir.joinpath(f"task_flow_{task_name}.service")]
    # check if there is a corresponsing stop service.
    if (
        stop_srv_file := systemd_dir.joinpath(f"task_flow_{task_name}_stop.service")
    ).is_file():
        srv_files.append(stop_srv_file)
    for f in srv_files:
        systemctl("stop", f"{f.stem}.timer")
        systemctl("disable", f"{f.stem}.timer")
        logger.info(f"Disabled service: {f.stem}")
        if remove_files:
            logger.info(f"Removed service: {f.stem}")
            f.unlink()
            # remove the timer that corresponds to this service.
            f.with_suffix(".timer").unlink()
    systemctl("daemon-reload")
    systemctl("reset-failed")
