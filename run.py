import sys

from app import models
from app.bank import BankApp


def main(argv=sys.argv[1:]):
    models.Client('JohnJones').save()
    return BankApp().run(argv)


if __name__ == '__main__':
    sys.exit(main())