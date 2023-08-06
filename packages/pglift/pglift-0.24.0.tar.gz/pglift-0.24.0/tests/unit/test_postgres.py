import asyncio
from typing import Any, NoReturn
from unittest.mock import patch

import pytest

from pglift import postgres
from pglift.ctx import Context
from pglift.models.system import Instance


def test_main_errors() -> None:
    with pytest.raises(SystemExit, match="2"):
        postgres.main(["aa"])
    with pytest.raises(SystemExit, match="2"):
        postgres.main(["12-"])
    with pytest.raises(SystemExit, match="2"):
        postgres.main(["12-test"])


def test_main(
    monkeypatch: pytest.MonkeyPatch, ctx: Context, instance: Instance
) -> None:
    calls = []

    class Process:
        def __init__(self, prog: str, *args: str, **kwargs: Any) -> None:
            cmd = [prog] + list(args)
            self.cmd = cmd
            calls.append(cmd)
            self.pid = 123
            self.returncode = 0

        async def communicate(input: Any) -> NoReturn:
            await asyncio.sleep(2)  # cmd.Program's timeout is 1
            assert False

    class logged_subprocess_exec:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.proc = Process(*args, **kwargs)

        async def __aenter__(self) -> Process:
            return self.proc

        async def __aexit__(self, *args: Any) -> None:
            pass

    with patch("pglift.cmd.logged_subprocess_exec", new=logged_subprocess_exec):
        postgres.main([f"{instance.version}-{instance.name}"], ctx=ctx)
    bindir = ctx.settings.postgresql.versions[instance.version].bindir
    assert calls == [[str(bindir / "postgres"), "-D", str(instance.datadir)]]
    assert (
        ctx.settings.postgresql.pid_directory
        / f"postgresql-{instance.version}-{instance.name}.pid"
    ).read_text() == "123"
