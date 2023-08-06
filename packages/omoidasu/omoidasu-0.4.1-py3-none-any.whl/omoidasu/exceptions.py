class NotEnoughCardSidesException(Exception):
    filename: str
    sides_count: int

    def __init__(self, filename, sides_count):
        self.filename = str(filename)
        self.sides_count = int(sides_count)


class FlashcardsDirectoryException(Exception):
    filename: str

    def __init__(self, filename):
        self.filename = str(filename)


class FlashcardsDirectoryDoesNotExists(FlashcardsDirectoryException):
    def __str__(self):
        return f'Flashcards directory "{self.filename}" does not exists.'


class FlashcardsDirectoryIsFile(FlashcardsDirectoryException):
    def __str__(self):
        return f'Flashcards directory "{self.filename}" is file.'
