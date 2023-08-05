import traceback

from efemarai.console import console


class BaseChecker:
    def _error(self, message, print_exception=False):
        console.print(f":poop: {message}", style="red")

        if print_exception:
            traceback.print_exc()

        raise AssertionError()

    def _warning(self, message):
        console.print(f":warning: {message}", style="orange1")

    def _get_required_item(self, definition, key, parent=None):
        item = definition.get(key)

        if item is None:
            message = f"Missing field '{key}'"
            if parent is not None:
                message += f" (in '{parent}')"
            self._error(message)

        return item
