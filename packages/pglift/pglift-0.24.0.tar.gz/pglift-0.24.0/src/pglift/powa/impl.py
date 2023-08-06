from typing import TYPE_CHECKING, Optional

from .. import types

if TYPE_CHECKING:
    from ..ctx import BaseContext
    from ..settings import PowaSettings

# Extensions to load in shared_preload_libraries and to install.
# Order is important here, for example`pg_stat_statements` needs to be loaded
# before `pg_stat_kcache` in shared_preload_libraries
POWA_EXTENSIONS = [
    types.Extension.btree_gist,
    types.Extension.pg_qualstats,
    types.Extension.pg_stat_statements,
    types.Extension.pg_stat_kcache,
    types.Extension.powa,
]


def available(ctx: "BaseContext") -> Optional["PowaSettings"]:
    return ctx.settings.powa
