import abc
import datetime
import sys

from cliff import command
from prettytable import PrettyTable

from app import models


class BankCommand(command.Command, metaclass=abc.ABCMeta):
    """
    Abstract class for creating new commands for the app.

    Attributes
    -----------
    args: dict
        A dictionary of available arguments for the command, where keys are arguments, and values are help messages.

    Methods
    ----------
    abstract take_action(parsed_args)
        Actions to perform after calling the command. All passed arguments are in the 'parser_args' parameter
        gathered in the Namespace class and available via '.'. For example: parsed_args.name
    """

    args = {}

    def get_parser(self, prog_name):
        """Command argument parsing."""
        parser = super(BankCommand, self).get_parser(prog_name)
        group = parser.add_argument_group()

        for arg in self.args:
            group.add_argument(
                arg,
                help=self.args[arg],
                required=True
            )

        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args):
        pass


class Withdraw(BankCommand):
    """
    A command which gives an ability to withdraw money from account.
    """

    args = {
        '--client': 'Name of a client.',
        '--amount': 'Amount of money to withdraw.',
        '--description': 'Description of the operation.',
    }

    def take_action(self, parsed_args):
        client = models.Client.get(name=parsed_args.client)
        if not client:
            return print("A client with given name hasn't been found")
        try:
            client.withdraw(parsed_args.amount, parsed_args.description)
        except ValueError as error:
            return print(f'Withdraw operation has failed with the error: {error}')
        return print(f"Withdrawal operation was successful! (${client.get_balance():.2f} available for {client.name})")


class Deposit(BankCommand):
    """
    A command which gives an ability to deposit money to a client's account
    """

    args = {
        '--client': 'Name of a client.',
        '--amount': 'Amount of money to deposit.',
        '--description': 'Description of the operation.',
    }

    def take_action(self, parsed_args):
        client = models.Client.get(name=parsed_args.client)
        if not client:
            return print("A client with given name hasn't been found")
        try:
            client.deposit(parsed_args.amount, parsed_args.description)
        except ValueError as error:
            return print(f'Deposit operation has failed with the error: {error}')
        return print(f"Deposit operation was successful! (${client.get_balance():.2f} available for {client.name})")


class ShowBankStatement(BankCommand):
    """
    Print all operations in a chosen period using PrettyTable.
    """

    args = {
        '--client': 'Name of a client.',
        '--since': 'Time since when operations displayed.',
        '--till': 'Time till when operations displayed.',
    }

    def take_action(self, parsed_args):
        client = models.Client.get(name=parsed_args.client)
        if not client:
            return print("A client with such name hasn't been found")
        operations = models.Operation.get(client_id=client.get_id(), since=parsed_args.since, till=parsed_args.till)
        table = PrettyTable()
        table.field_names = ['Date', 'Description', 'Withdrawals', 'Deposits', 'Balance']
        previous_operations = models.Operation.get(
            client_id=client.get_id(),
            since=datetime.datetime.fromtimestamp(0),
            till=parsed_args.since)

        previous_balance = 0
        if len(previous_operations) > 0:
            previous_balance = previous_operations[-1].current_balance

        table.add_row(['', 'Previous balance', '', '', f'${previous_balance:.2f}'])
        withdraw_total, deposit_total = 0, 0
        for operation in operations:
            row = [operation.date.strftime(models.Operation.date_format), operation.description]
            if operation.operation_type == 'withdraw':
                row += [f'${operation.amount:.2f}', '']
                withdraw_total += operation.amount
            if operation.operation_type == 'deposit':
                row += ['', f'${operation.amount:.2f}']
                deposit_total += operation.amount
            row += [f'${operation.current_balance:.2f}']
            table.add_row(row)

        balance_total = 0
        if len(operations) > 0:
            balance_total = operations[-1].current_balance

        table.add_row(['', 'Totals', f'${withdraw_total:.2f}', f'${deposit_total:.2f}', f'${balance_total:.2f}'])
        return print(table)


class NewClient(BankCommand):
    """
    Serves for adding new clients to the database.
    """

    args = {
        '--client': 'Name of a client.',
        '--amount': 'Amount of money for the initial deposit.'
    }

    def take_action(self, parsed_args):
        new_client = models.Client(name=parsed_args.client, balance=parsed_args.amount)
        try:
            new_client.save()
        except ValueError as error:
            return print(error)
        return print(f'New client "{new_client.name}" has been added to the database! '
                     f'(${new_client.get_balance()} available for him)')


class Exit(BankCommand):
    def take_action(self, parsed_args):
        return sys.exit()
