import pytest

from pglift import backup, instances, systemd
from pglift.ctx import Context
from pglift.models import system


def test_systemd_backup_job(ctx: Context, instance: system.Instance) -> None:
    scheduler = ctx.settings.scheduler
    if scheduler != "systemd":
        pytest.skip(f"not applicable for scheduler method '{scheduler}'")

    assert systemd.is_enabled(ctx, backup.systemd_timer(instance))

    assert not systemd.is_active(ctx, backup.systemd_timer(instance))
    with instances.running(ctx, instance, run_hooks=True):
        assert systemd.is_active(ctx, backup.systemd_timer(instance))
    assert not systemd.is_active(ctx, backup.systemd_timer(instance))
