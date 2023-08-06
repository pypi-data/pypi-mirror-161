import logging
from typing import TYPE_CHECKING, Optional, Type

from pgtoolkit.conf import Configuration

from .. import hookimpl
from ..models import interface, system
from ..settings import EXTENSIONS_CONFIG
from . import models
from .impl import POWA_EXTENSIONS
from .impl import available as available

if TYPE_CHECKING:

    from ..ctx import BaseContext
    from ..settings import Settings

logger = logging.getLogger(__name__)


@hookimpl  # type: ignore[misc]
def instance_configuration(
    ctx: "BaseContext", manifest: "interface.Instance"
) -> Configuration:
    settings = available(ctx)
    assert settings is not None
    extensions = [e for e in POWA_EXTENSIONS if EXTENSIONS_CONFIG[e][0]]
    conf = Configuration()
    conf["shared_preload_libraries"] = ", ".join(extensions)
    return conf


@hookimpl  # type: ignore[misc]
def interface_model() -> Type[models.ServiceManifest]:
    return models.ServiceManifest


@hookimpl  # type: ignore[misc]
def get(ctx: "BaseContext", instance: "system.Instance") -> models.ServiceManifest:
    return models.ServiceManifest()


@hookimpl  # type: ignore[misc]
def rolename(settings: "Settings") -> str:
    assert settings.powa
    return settings.powa.role


@hookimpl  # type: ignore[misc]
def role(
    settings: "Settings", manifest: "interface.Instance"
) -> Optional[interface.Role]:
    name = rolename(settings)
    service = manifest.service(models.ServiceManifest)
    if service is None:
        return None
    password = None
    if service.password:
        password = service.password.get_secret_value()
    return interface.Role(
        name=name,
        password=password,
        login=True,
        superuser=True,
    )


@hookimpl  # type: ignore[misc]
def database(
    settings: "Settings", manifest: "interface.Instance"
) -> Optional[interface.Database]:
    service = manifest.service(models.ServiceManifest)
    if service is None:
        return None
    assert settings.powa
    return interface.Database(name=settings.powa.dbname, extensions=POWA_EXTENSIONS)
