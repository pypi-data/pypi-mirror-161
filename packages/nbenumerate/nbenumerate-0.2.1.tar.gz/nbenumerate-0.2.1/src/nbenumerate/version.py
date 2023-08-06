class Version:
    """A class that represents an incrementable version."""

    def __init__(self):
        self._version = []

    def increment(self, level: int = 1) -> None:
        """Increment the current version by one on the specified level.

        Args:
            level (int): Level that is used to increment. Defaults to 1.
        """
        # pad to length `level`
        self._version = (self._version + level * [0])[: level + 1]

        # increment at level
        self._version[level - 1] += 1

        # remove everything after level
        self._version = self._version[:level]

    def __repr__(self) -> str:
        return "".join([f"{n}." for n in self._version])
