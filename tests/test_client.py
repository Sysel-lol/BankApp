import pytest

from app import models


def test_client_creation():
    try:
        models.Client(name='Test')
        models.Client(name='Test2', balance=100)
    except Exception as error:
        pytest.fail(str(error))

    pytest.raises(Exception, models.Client, balance=100)
    pytest.raises(Exception, models.Client, name='Test', balance=-100)


def test_client_deposit():
    client = models.Client(name='Test')
    client.deposit(100, 'test')
    assert client.get_balance() == 100

    client = models.Client(name='Test', balance=100)
    assert client.get_balance() == 100


def test_client_withdraw():
    client = models.Client(name='Test', balance=100)
    client.withdraw(amount=100, description='Test')
    assert client.get_balance() == 0

    pytest.raises(ValueError, client.withdraw, amount=100, description='Test')


def test_get_client_by_name():
    client = models.Client(name='test_get_client_by_name', balance=100).save()
    db_client = models.Client.get(name='test_get_client_by_name')

    assert db_client == client
