from rich import print as rich_print
from rigelcore.exceptions import RigelError


class ErrorLogger:
    """
    A class that provides a common interface to display error messages.
    """

    def log(self, err: RigelError) -> None:
        """
        Display error message.

        :type err: rigel.exceptions.RigelError
        :param err: The error.
        """
        rich_print(f'[bold red]{err}[/bold red] ([bold]Error: {err.code}[/bold])')
