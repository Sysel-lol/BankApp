import pytest, os

from app.bank import BankApp


def test_startup(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "exit")
    print(os.getcwd())
    try:
        BankApp().run(None)
    except Exception as error:
        pytest.fail(str(error))

