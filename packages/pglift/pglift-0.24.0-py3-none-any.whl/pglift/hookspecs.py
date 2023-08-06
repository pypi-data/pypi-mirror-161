from typing import TYPE_CHECKING, Any, Dict, Optional, Type

import pluggy
from pgtoolkit.conf import Configuration

from . import __name__ as pkgname
from ._compat import Literal, TypeAlias

if TYPE_CHECKING:
    import click

    from .ctx import BaseContext
    from .models import interface
    from .models.system import BaseInstance, Instance, PostgreSQLInstance
    from .settings import Settings
    from .types import ConfigChanges, ServiceManifest

hookspec = pluggy.HookspecMarker(pkgname)

FirstResult: TypeAlias = Optional[Literal[True]]


@hookspec  # type: ignore[misc]
def install_systemd_unit_template(ctx: "BaseContext", header: str = "") -> None:
    """Install systemd unit templates."""


@hookspec  # type: ignore[misc]
def uninstall_systemd_unit_template(ctx: "BaseContext") -> None:
    """Uninstall systemd unit templates."""


@hookspec  # type: ignore[misc]
def cli() -> "click.Command":
    """Return command-line entry point as click Command (or Group) for the plugin."""


@hookspec  # type: ignore[misc]
def instance_cli(group: "click.Group") -> None:
    """Extend 'group' with extra commands from the plugin."""


@hookspec  # type: ignore[misc]
def system_lookup(ctx: "BaseContext", instance: "PostgreSQLInstance") -> Optional[Any]:
    """Look up for the satellite service object on system that matches specified instance."""


@hookspec  # type: ignore[misc]
def get(ctx: "BaseContext", instance: "Instance") -> Optional["ServiceManifest"]:
    """Return the description the satellite service bound to specified instance."""


@hookspec  # type: ignore[misc]
def interface_model() -> Type["ServiceManifest"]:
    """The interface model for satellite component provided plugin."""


@hookspec  # type: ignore[misc]
def instance_configuration(
    ctx: "BaseContext", manifest: "interface.Instance"
) -> Configuration:
    """Called before the PostgreSQL instance configuration is written."""


@hookspec(firstresult=True)  # type: ignore[misc]
def instance_init_replication(
    ctx: "BaseContext",
    instance: "Instance",
    standby: "interface.Instance.Standby",
) -> Optional[bool]:
    """Called before PostgreSQL datadir is created for a standby."""


@hookspec  # type: ignore[misc]
def instance_configure(
    ctx: "BaseContext",
    manifest: "interface.Instance",
    config: Configuration,
    changes: "ConfigChanges",
    creating: bool,
) -> None:
    """Called when the PostgreSQL instance got (re-)configured."""


@hookspec  # type: ignore[misc]
def instance_drop(ctx: "BaseContext", instance: "Instance") -> None:
    """Called when the PostgreSQL instance got dropped."""


@hookspec  # type: ignore[misc]
def instance_start(ctx: "BaseContext", instance: "Instance") -> None:
    """Called when the PostgreSQL instance got started."""


@hookspec  # type: ignore[misc]
def instance_stop(ctx: "BaseContext", instance: "Instance") -> None:
    """Called when the PostgreSQL instance got stopped."""


@hookspec  # type: ignore[misc]
def instance_env(ctx: "BaseContext", instance: "Instance") -> Dict[str, str]:
    """Return environment variables for instance defined by the plugin."""


@hookspec  # type: ignore[misc]
def rolename(settings: "Settings") -> str:
    """Return the name of role used by a plugin."""


@hookspec  # type: ignore[misc]
def role(settings: "Settings", manifest: "interface.Instance") -> "interface.Role":
    """Return the role used by a plugin, to be created at instance creation."""


@hookspec  # type: ignore[misc]
def database(
    settings: "Settings", manifest: "interface.Instance"
) -> "interface.Database":
    """Return the database used by a plugin, to be created at instance creation."""


@hookspec(firstresult=True)  # type: ignore[misc]
def initdb(
    ctx: "BaseContext", manifest: "interface.Instance", instance: "BaseInstance"
) -> FirstResult:
    """Initialize a PostgreSQL database cluster.

    Only one implementation should be invoked so call order and returned value
    matter.
    """


@hookspec(firstresult=True)  # type: ignore[misc]
def configure_postgresql(
    ctx: "BaseContext",
    manifest: "interface.Instance",
    configuration: Configuration,
    instance: "BaseInstance",
) -> Optional["ConfigChanges"]:
    """Configure PostgreSQL and return 'changes' to postgresql.conf.

    Only one implementation should be invoked so call order and returned value
    matter.
    """


@hookspec(firstresult=True)  # type: ignore[misc]
def start_postgresql(
    ctx: "BaseContext", instance: "PostgreSQLInstance", foreground: bool, wait: bool
) -> FirstResult:
    """Start PostgreSQL for specified 'instance'.

    Only one implementation should be invoked so call order and returned value
    matter.
    """


@hookspec(firstresult=True)  # type: ignore[misc]
def stop_postgresql(
    ctx: "BaseContext", instance: "PostgreSQLInstance", mode: str, wait: bool
) -> FirstResult:
    """Stop PostgreSQL for specified 'instance'.

    Only one implementation should be invoked so call order and returned value
    matter.
    """


@hookspec(firstresult=True)  # type: ignore[misc]
def restart_postgresql(
    ctx: "BaseContext", instance: "Instance", mode: str, wait: bool
) -> FirstResult:
    """Restart PostgreSQL for specified 'instance'.

    Only one implementation should be invoked so call order and returned value
    matter.
    """


@hookspec(firstresult=True)  # type: ignore[misc]
def systemd_postgresql_unit(instance: "BaseInstance") -> str:
    """Return the system unit name for a PostgreSQL instance (e.g.
    postgresql@14-main.service).

    Only one implementation should be invoked so call order and returned value
    matter.
    """
