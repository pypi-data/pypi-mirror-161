"""CRUD functions."""


import logging
import os
import uuid
from typing import List

from rich import prompt

from omoidasu import exceptions
from omoidasu.models import Card, Side

logger = logging.getLogger(__name__)


def load_flashcard(filename) -> Card:
    """Loads flashcard from file."""
    sides: List[Side] = []
    if not os.path.isfile(filename):
        raise TypeError
    with open(filename, encoding="utf-8") as file:
        for index, line in enumerate(file.readlines()):
            line = line.replace("\n", "")
            if len(line) == 0:
                continue
            if line[0] == "#":
                continue
            sides.append(Side(id=index, content=line))
    if isinstance(filename, os.DirEntry):
        name = filename.name
    else:
        name = os.path.basename(filename)
    return Card(filename=name, sides=sides)


def check_directory(directory: str, interactive: bool):
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise exceptions.FlashcardsDirectoryIsFile(directory)
    else:
        if interactive:
            if not prompt.Confirm(f'Create flashcards directory "{directory}"?'):
                raise exceptions.FlashcardsDirectoryDoesNotExists(directory)
        os.makedirs(directory)


async def get_cards(context, regular_expression) -> List[Card]:
    """Get cards filtered by regular expression."""
    directory = context.obj.flashcards_dir
    check_directory(directory, context.obj.interactive)
    flashcards = [load_flashcard(file) for file in os.scandir(directory)]
    return flashcards


async def add_card(context, card: Card) -> Card:
    """Add new card. Returns created card."""
    file_content = "\n".join([side.content for side in card.sides])
    filename = str(uuid.uuid4())
    path = os.path.join(context.obj.flashcards_dir, filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write(file_content)
    result = load_flashcard(path)
    return result


# async def remove_card(context, card: Card) -> bool:
#     """Remove card. Returns true, if successfully removed."""
#     return False


# async def update_card(context, card: Card) -> Card:
#     """Update card. Returns updated card."""
#     result: Card
#     return result
