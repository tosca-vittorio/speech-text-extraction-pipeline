# src/tests/test_cli_utils.py

import pytest
import builtins
import subprocess

import package.cli_utils as cli_utils
from package.errors import InvalidChoiceError

class DummyCompletedProcess:
    def __init__(self, stdout):
        self.stdout = stdout

@pytest.fixture(autouse=True)
def restore_platform(monkeypatch):
    # ripristina platform.system e platform.node dopo ogni test
    yield
    monkeypatch.undo()

def test_get_csproduct_name_non_windows(monkeypatch):
    monkeypatch.setattr(cli_utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(cli_utils.platform, "node", lambda: "my-host")
    assert cli_utils.get_csproduct_name() == "my-host"

def test_get_csproduct_name_windows_success(monkeypatch):
    monkeypatch.setattr(cli_utils.platform, "system", lambda: "Windows")
    monkeypatch.setattr(cli_utils.platform, "node", lambda: "fallback-host")

    # Simula WMIC che restituisce header + valore
    fake_output = "Name  \r\nProd-XYZ  \r\n"
    monkeypatch.setattr(subprocess, "run",
                        lambda *args, **kw: DummyCompletedProcess(stdout=fake_output))

    name = cli_utils.get_csproduct_name()
    assert name == "Prod-XYZ"

def test_get_csproduct_name_windows_no_value(monkeypatch):
    # se WMIC non restituisce una seconda riga valida, torna platform.node()
    monkeypatch.setattr(cli_utils.platform, "system", lambda: "Windows")
    monkeypatch.setattr(cli_utils.platform, "node", lambda: "fallback-host")

    fake_output = "NameOnly\n"
    monkeypatch.setattr(subprocess, "run",
                        lambda *args, **kw: DummyCompletedProcess(stdout=fake_output))

    assert cli_utils.get_csproduct_name() == "fallback-host"

def test_get_csproduct_name_windows_error(monkeypatch):
    monkeypatch.setattr(cli_utils.platform, "system", lambda: "Windows")
    monkeypatch.setattr(cli_utils.platform, "node", lambda: "fallback-host")

    def boom(*args, **kw):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["wmic", "csproduct", "get", "name"],
        )

    monkeypatch.setattr(subprocess, "run", boom)

    assert cli_utils.get_csproduct_name() == "fallback-host"

def test_stampa_orario_format(capsys, monkeypatch):
    # Fissa datetime.now() a un valore noto
    class FakeDateTime:
        @classmethod
        def now(cls):
            import datetime as _dt
            return _dt.datetime(2025, 5, 28, 9, 7, 5)

    monkeypatch.setattr(cli_utils, "datetime", FakeDateTime)
    cli_utils.stampa_orario()
    captured = capsys.readouterr().out
    # Deve stampare una riga vuota + 🕒 Ora attuale: 2025-05-28 09:07:05 + newline
    assert captured == "\n🕒 Ora attuale: 2025-05-28 09:07:05\n"


@pytest.mark.parametrize("user_inputs, expected, max_retries", [
    (["2"], "opt2", 3),
    ([" 3 "], "opt3", 3),
    (["bad", "1"], "opt1", 3),
])
def test_ask_choice_success(monkeypatch, user_inputs, expected, max_retries):
    opts = ["opt1", "opt2", "opt3"]
    inputs = iter(user_inputs)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    result = cli_utils.ask_choice("Scegli:", opts, max_retries=max_retries)
    assert result == expected

def test_ask_choice_no_options():
    with pytest.raises(InvalidChoiceError):
        cli_utils.ask_choice("Niente qui", [], max_retries=1)

def test_ask_choice_too_many_invalid(monkeypatch):
    opts = ["uno", "due"]
    # input sempre non valido
    monkeypatch.setattr(builtins, "input", lambda prompt="": "x")
    with pytest.raises(InvalidChoiceError) as exc:
        cli_utils.ask_choice("Menu", opts, max_retries=2)
    msg = str(exc.value)
    assert "troppi input non validi" in msg
    assert "Menu" in msg
