import pytest

from app import models


def test_save():
    try:
        models.Model().save()
    except Exception as error:
        pytest.fail(str(error))
    assert len(models.Model.list) == 1


def test_get_by_id():
    model = models.Model().save()
    db_model = models.Model().get(id=model.get_id())
    assert db_model == model


def test_delete():
    db_model = models.Model().get(id=1)
    db_model.delete()
    assert len(models.Model.list) == 1


def test_id_auto_increment():
    first = models.Model().save()
    second = models.Model().save()
    assert first.get_id() == 1 and second.get_id() == 2

    third = models.Model().save()
    second.delete()
    fourth = models.Model().save()
    assert fourth.get_id() == 4

    fourth.delete()
    fifth = models.Model().save()
    assert fifth.get_id() == 4