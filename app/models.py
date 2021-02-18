import abc
import re
import copy
import datetime


class Model(metaclass=abc.ABCMeta):
    """
    Abstract class for creating new models in the project.

    Attributes
    ----------
    list: list
        A list of all objects of the model saved by the save method. Can be considered as the simplest database.

    Methods
    ---------
    get(id: int) -> Current class object
        Using for getting an object of a current class from the class list. Returns an object if the object with such
        id exists and False otherwise.
    get_id() -> int
        Returns ID of the current object.
    validate() -> bool
        Using for validating the Model object fields. Uses _is_validate_[field_name] methods of the class.
        Returns True if fields are valid and raises ValueError otherwise.
    save() -> None
        Using for saving the object in the current class list of all objects. Can be considered as a DB saving method.
    delete() -> None
        Using for deleting the current object from the class list (DB).
    """
    list = []

    def __init__(self, *args, **kwargs):
        if len(self.__class__.list) > 0:
            self._id = max(self.__class__.list, key=lambda model: model.get_id()).get_id()+1
        else:
            self._id = 0

    @classmethod
    def get(cls, id: int):
        obj = [obj for obj in cls.list if obj.get_id() == id]
        if obj:
            return copy.deepcopy(obj[0])
        return False

    def get_id(self):
        return self._id

    def validate(self):
        validators = [validator for validator in dir(self.__class__) if validator.find('_is_valid_') != -1]
        for validator in validators:
            validator_method = getattr(self, validator)
            field = re.findall(r'_is_valid_(.*)', validator)[0]
            validator_method(getattr(self, field))
        return True

    def save(self):
        self.validate()
        obj = self.get(id=self._id)
        if not obj:
            new_obj = copy.deepcopy(self)
            self.__class__.list.append(new_obj)
        else:
            obj_index = [index for index, obj in enumerate(self.__class__.list) if obj.get_id() == self._id][0]
            new_obj = copy.deepcopy(self)
            self.__class__.list[obj_index] = new_obj
        return copy.deepcopy(new_obj)

    def delete(self):
        obj = [obj for obj in self.__class__.list if obj.get_id() == self._id]
        if not obj:
            raise ValueError("Can't find such object in the database.")
        obj_index = self.__class__.list.index(obj[0])
        self.__class__.list.pop(obj_index)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        print(vars(self))
        print(vars(other))
        if vars(self) == vars(other):
            return True
        return False


class Client(Model):
    """
    Client model, which is used for creating and storing clients.
    """
    list = []

    def __init__(self, name, balance=0, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        if [client for client in Client.list if client.name == name]:
            raise ValueError('Client with such name is already on the database.')
        self.name = name
        self._balance = 0
        if balance:
            self.deposit(balance, 'Initial deposit')

    def deposit(self, amount, description):
        old_balance = self._balance
        self._balance += float(amount)
        try:
            self.save()
            new_operation = Operation(
                client_id=self.get_id(), amount=amount, description=description, operation_type='deposit'
            )
        except ValueError as error:
            self._balance = old_balance
            raise error
        new_operation.save()

    def withdraw(self, amount, description):
        old_balance = self._balance
        self._balance -= float(amount)
        try:
            self.save()
            new_operation = Operation(
                client_id=self.get_id(), amount=amount, description=description, operation_type='withdraw'
            )
        except ValueError as error:
            self._balance = old_balance
            raise error
        new_operation.save()

    def get_balance(self):
        return self._balance

    @classmethod
    def get(cls, id=None, name=None):
        if id is not None:
            return super().get(id=id)
        if name is not None:
            obj = [obj for obj in cls.list if obj.name == name]
            if obj:
                return copy.deepcopy(obj[0])
        return False

    @staticmethod
    def _is_valid__balance(balance):
        balance = float(balance)
        if balance < 0:
            raise ValueError("Amount of remaining client's money can't be less then 0")
        return balance


class Operation(Model):
    """
    Operation model, which is used for managing operations.

    Attributes
    ----------
    _operation_types: list
        A list of available operations (choices).
    date_format: str
        Date format which is used for display and parsing dates.
    """
    list = []

    _operation_types = ['withdraw', 'deposit']
    date_format = "%Y-%m-%d,%H:%M:%S"

    def __init__(self, operation_type, amount, description, client_id=None, client=None, *args, **kwargs):
        super(Operation, self).__init__(*args, **kwargs)
        if client_id is None and client is None:
            raise TypeError('To create an operation object you need to provide either client ID or his name.')
        if client_id is not None:
            self.client_id = self._is_valid_client_id(client_id)
        else:
            self.client_id = self._validate_client_name(client)
        self.amount = self._is_valid_amount(amount)
        self.operation_type = self._is_valid_operation_type(operation_type)
        self.description = description
        self.date = datetime.datetime.now()
        self.current_balance = Client.get(self.client_id).get_balance()

    @classmethod
    def get(cls, id=None, client_id=None, since=None, till=None):
        if id is not None:
            return super().get(id=id)
        if client_id is None or since is None or till is None:
            return False
        if not isinstance(since, datetime.datetime):
            since = datetime.datetime.strptime(since, Operation.date_format)
        if not isinstance(till, datetime.datetime):
            till = datetime.datetime.strptime(till, Operation.date_format)
        return [operation for operation in Operation.list if since <= operation.date <= till and operation.client_id == client_id]

    @staticmethod
    def _is_valid_client_id(client_id):
        if not Client.get(id=client_id):
            raise ValueError("A client with such ID hasn't been found.")
        return client_id

    @staticmethod
    def _is_valid_operation_type(operation_type):
        if operation_type not in Operation._operation_types:
            raise ValueError('Incorrect operation type.')
        return operation_type

    @staticmethod
    def _is_valid_amount(amount):
        amount = float(amount)
        if amount < 0:
            raise ValueError('Incorrect amount of money.')
        return amount

    @staticmethod
    def _validate_client_name(client_name):
        client = [obj for obj in Client.list if obj.name == client_name]
        if not client:
            raise ValueError("A client with such name hasn't been found.")
        return client[0].get_id()



