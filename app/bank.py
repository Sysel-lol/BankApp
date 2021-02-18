from cliff.app import App
from cliff.commandmanager import CommandManager

from app import commands


class BankApp(App):
    """
    Configuration class for using the cliff package.

    Attributes
    ----------
    commands: dict
        A dictionary of available commands to perform, where key is a command name, and value is a BankCommand class
        which is used by a command.
    """
    commands = {
        'withdraw': commands.Withdraw,
        'deposit': commands.Deposit,
        'show_bank_statement': commands.ShowBankStatement,
        'new_client': commands.NewClient,
        'exit': commands.Exit
    }

    def __init__(self):
        manager = CommandManager('bank_prompt')
        self.NAME = 'Bank app'
        for command in self.commands:
            manager.add_command(command, self.commands[command])
        super(BankApp, self).__init__(
            description='Bank application',
            version='0.1',
            command_manager=manager,
            deferred_help=True,
        )
        print('Service has been started!')



