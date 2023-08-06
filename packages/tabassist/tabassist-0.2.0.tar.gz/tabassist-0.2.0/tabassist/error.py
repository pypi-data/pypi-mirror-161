"""Objects which helps to work with errors easier."""
import click
from collections import defaultdict


class Error():
    """Error found in workbook."""

    def __init__(self, code, short_desc, context) -> None:
        """Init found error.

        Args:
            code ([string]): Error code.
            short_desc ([string]): Short error description.
            context ([object]): Scope where error was found.
        """
        self._code = code
        self._short_desc = short_desc
        self._context = context

    def __str__(self) -> str:
        """Show nice printable representation of error."""
        return f"{self._code}: '{self._context}' {self._short_desc}"

    def __repr__(self) -> str:
        """Show nice object representation of error."""
        return f"<class Error: {self._code} - '{self._context}'>"

    def __eq__(self, other: object) -> bool:
        """Allow error being compared to other errors."""
        if isinstance(other, Error):
            return self._code + self._context == other._code + other._context
        return False

    def __hash__(self) -> int:
        """Allow error being used in sets."""
        return hash(self._code + self._context)


class ErrorRegistry():
    """Container for found errors."""

    def __init__(self) -> None:
        """Init empty container."""
        self._found_errors = set()

    def add(self, error):
        """Register new error found in workbook."""
        if isinstance(error, Error):
            self._found_errors.add(error)
        else:
            raise TypeError('ErrorRegistry must contain Error objects only')

    def show_errors(self):
        """Print errors in console according to error's code order."""
        for e in sorted(self._found_errors, key=lambda x: x._code):
            click.echo(e)

    def show_summary(self):
        """Print statistics of found error in console."""
        result = defaultdict(Error)
        for error in self._found_errors:
            if error._code not in result:
                result[error._code] = 1
            else:
                result[error._code] += 1
        for k in sorted(result, key=lambda x: x):
            click.echo(f'{k}: {result[k]}')
