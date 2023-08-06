from enum import Enum
from typing import Dict, Optional, Sequence, Union

from dotenv import dotenv_values
from pydantic import BaseModel, FilePath, validator


class TimerOption(Enum):
    # Defines realtime (i.e. wallclock) timers with calendar event expressions.
    OnCalendar = "OnCalendar"
    # Defines a timer relative to the moment the timer unit itself is activated.
    OnActiveSec = "OnActiveSec"
    # Defines a timer relative to when the machine was booted up.
    # In containers, for the system manager instance, this is mapped to OnStartupSec=, making both equivalent.
    OnBootSec = "OnBootSec"
    # Defines a timer relative to when the service manager was first started.
    # For system timer units this is very similar to OnBootSec= as the system service manager is generally started very early at boot.
    # It's primarily useful when configured in units running in the per-user service manager,
    # as the user service manager is generally started on first login only, not already during boot.
    OnStartupSec = "OnStartupSec"
    # Defines a timer relative to when the unit the timer unit is activating was last activated.
    OnUnitActiveSec = "OnUnitActiveSec"
    # Defines a timer relative to when the unit the timer unit is activating was last deactivated.
    OnUnitInactiveSec = "OnUnitInactiveSec"


class Timer(BaseModel):
    option: TimerOption
    value: str


class Volume(BaseModel):
    """Docker volume."""

    host_path: str
    container_path: str
    read_only: bool = True


class Ulimit(BaseModel):
    name: str
    soft: Optional[int] = None
    hard: Optional[int] = None

    @validator("soft", always=True)
    def check_has_limit(cls, soft, values):
        if soft is None and values.get("hard") is None:
            raise ValueError("Either `soft` limit or `hard` limit must be set.")


class Container(BaseModel):
    image: str
    command: str
    network_mode: str = "host"
    init: bool = True
    user: Optional[str] = None
    mem_limit: Optional[str] = None
    shm_size: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    env_file: Optional[FilePath] = None
    volumes: Optional[Union[Volume, Sequence[Volume]]] = None
    ulimits: Optional[Union[Ulimit, Sequence[Ulimit]]] = None

    @validator("env_file")
    def load_env_file(cls, f):
        if f is not None:
            return dotenv_values(f)

    @validator("volumes", "ulimits")
    def check_iterable(cls, v):
        if not isinstance(v, (list, tuple, set)):
            return [v]
        return v


class ScheduledTask(BaseModel):
    task_name: str
    container: Container
    start_timer: Union[Timer, Sequence[Timer]]
    stop_timer: Optional[Union[Timer, Sequence[Timer]]] = None

    @validator("start_timer", "stop_timer")
    def check_iterable(cls, v):
        if v is not None and not isinstance(v, (list, tuple, set)):
            return [v]
        return v
