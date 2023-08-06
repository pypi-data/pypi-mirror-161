import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pglift import cmd
from pglift.exceptions import CommandError, SystemError


def test_execute_program(caplog: pytest.LogCaptureFixture, tmp_path: Path) -> None:
    command = ["/c", "m", "d"]
    with patch("os.execve") as execve, patch("os.execv") as execv:
        cmd.execute_program(command, env={"X": "Y"})
        execve.assert_called_once_with("/c", command, {"X": "Y"})
        assert not execv.called
    logger = logging.getLogger(__name__)
    with patch("os.execve") as execve, patch("os.execv") as execv, caplog.at_level(
        logging.DEBUG, logger=__name__
    ):
        cmd.execute_program(command, logger=logger)
        execv.assert_called_once_with("/c", command)
        assert not execve.called
    assert "executing program '/c m d'" in caplog.records[0].message


def test_start_program_terminate_program_status_program(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    logger = logging.getLogger(__name__)

    pidfile = tmp_path / "sleep" / "pid"
    p = cmd.Program(
        ["sleep", "10"], pidfile, timeout=0.01, env={"X_DEBUG": "1"}, logger=logger
    )
    assert p.pidfile == pidfile
    with pidfile.open() as f:
        pid = f.read()

    assert p.proc.pid == int(pid)

    proc = Path("/proc") / pid
    assert proc.exists()
    assert "sleep\x0010\x00" in (proc / "cmdline").read_text()
    assert "X_DEBUG" in (proc / "environ").read_text()

    assert cmd.status_program(pidfile) == cmd.Status.running

    with pidfile.open("a") as f:
        f.write("\nextra\ninformation\nignored")
    assert cmd.status_program(pidfile) == cmd.Status.running

    with pytest.raises(SystemError, match="running already"):
        cmd.Program(["sleep", "10"], pidfile, logger=logger)

    cmd.terminate_program(pidfile, logger=logger)
    r = subprocess.run(["pgrep", pid], check=False)
    assert r.returncode == 1

    assert not pidfile.exists()
    assert cmd.status_program(pidfile) == cmd.Status.not_running

    pidfile = tmp_path / "invalid.pid"
    pidfile.write_text("innnnvaaaaaaaaaaliiiiiiiiiiid")
    assert cmd.status_program(pidfile) == cmd.Status.dangling
    caplog.clear()
    with pytest.raises(CommandError) as excinfo, caplog.at_level(
        logging.DEBUG, logger=__name__
    ):
        cmd.Program(
            ["sleep", "well"], pidfile, logger=logger, env={"LANG": "C", "LC_ALL": "C"}
        )
    assert not pidfile.exists()
    assert "sleep is supposed to be running" in caplog.records[0].message
    assert "sleep: invalid time interval 'well'" in caplog.records[2].message
    assert "sleep: invalid time interval 'well'" in excinfo.value.stderr

    pidfile = tmp_path / "notfound"
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=__name__):
        cmd.terminate_program(pidfile, logger=logger)
    assert f"program from {pidfile} not running" in caplog.records[0].message


def test_program_context(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger(__name__)
    pidfile = tmp_path / "pid"
    pyprog = tmp_path / "prog.py"
    pyprog.write_text(
        "\n".join(
            [
                "import logging, time, signal, sys",
                "signal.signal(",
                "   signal.SIGTERM,",
                "   lambda signum, frame: logging.error('got signal %d', signum),",
                ")",
                "s = int(sys.argv[1])",
                "logging.warning('sleeping %ds', s)",
                "time.sleep(s)",
            ]
        )
    )
    with pytest.raises(ValueError, match="expected"), caplog.at_level(
        logging.DEBUG, logger=__name__
    ):
        with cmd.Program(
            [sys.executable, str(pyprog), "2"], pidfile, timeout=1, logger=logger
        ) as prog:
            assert pidfile.exists()
            assert prog.proc.returncode is None
            raise ValueError("expected")
    messages = caplog.messages
    startuplog, pylog, termlog, signallog = messages
    assert startuplog.startswith("starting program '")
    assert "sleeping 2s" in pylog
    assert "terminating program" in termlog
    assert "got signal 15" in signallog
    assert not pidfile.exists()

    loop = asyncio.get_event_loop()
    program = sys.executable
    with pytest.raises(RuntimeError, match="expected"), caplog.at_level(
        logging.DEBUG, logger=__name__
    ), cmd.Program(
        [program, "--version"], pidfile=None, timeout=0, logger=logger
    ) as prog:
        loop.run_until_complete(prog.proc.wait())
        raise RuntimeError("expected")
    terminating_msg, terminated_msg = caplog.messages[-2:]
    assert terminating_msg == f"terminating program '{program} --version'"
    assert terminated_msg == f"program {program} already terminated"
