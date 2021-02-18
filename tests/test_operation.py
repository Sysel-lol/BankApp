import pytest
from datetime import datetime, timedelta

from app import models


def test_operation_creation():
    try:
        client = models.Client(name='Test')
        client.save()
        new_operation = models.Operation(
            client_id=client.get_id(),
            operation_type=models.Operation._operation_types[0],
            amount=100,
            description='Test'
        )
        new_operation.save()
    except Exception as error:
        pytest.fail(str(error))

    pytest.raises(TypeError, models.Operation, None)
    pytest.raises(TypeError, models.Operation,
                  operation_type=models.Operation._operation_types[0],
                  amount=100,
                  description='Test'
                  )


def test_operation_get_by_time():
    operation_list = models.Operation.get(client_id=0, since=datetime.fromtimestamp(0),
                                          till=datetime.today()+timedelta(days=10))
    assert len(operation_list) == 1

    new_operation = models.Operation(
        client_id=0,
        operation_type=models.Operation._operation_types[0],
        amount=100,
        description='Test'
    )
    new_operation.date = datetime.today()+timedelta(days=1)
    new_operation.save()
    operation_list = models.Operation.get(client_id=0, since=datetime.fromtimestamp(0),
                                          till=datetime.today() + timedelta(days=10))
    assert len(operation_list) == 2

    operation_list = models.Operation.get(client_id=0, since=datetime.today() + timedelta(hours=1),
                                          till=datetime.today() + timedelta(days=10))
    assert len(operation_list) == 1


