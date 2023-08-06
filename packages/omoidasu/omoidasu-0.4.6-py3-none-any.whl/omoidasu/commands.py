"""Async functions for CLI"""


import asyncio
import logging
import random
import subprocess
import tempfile
from typing import List, Optional

import click
import rich

from omoidasu import crud, models, utils
from omoidasu.exceptions import NotEnoughCardSidesException

logger = logging.getLogger(__name__)


async def list_cards(context, regular_expression, max_cards):
    """List all cards."""
    cards = await crud.get_cards(context, regular_expression)
    if len(cards) > max_cards:
        cards = cards[:max_cards]
    utils.show_cards_list_table(context, cards)


async def review_cards(context, regular_expression, max_cards):
    """Review all cards."""
    cards = await crud.get_cards(context, regular_expression)
    all_questions = []
    for card in cards:
        all_questions.extend(card.get_questions())
    random.shuffle(all_questions)
    for question in all_questions:
        question.ask()


async def add_card(context, sides: List[str]):
    card_content = [models.Side(
        id=i, content=content) for i, content in enumerate(sides)]
    card = models.Card(filename=None, sides=card_content)
    result = await crud.add_card(context, card)
    return result


def add_cards_interactively(context, editor: str):
    adding = True
    count = 0
    while adding:
        card: Optional[models.Card] = None
        with tempfile.NamedTemporaryFile() as file:
            subprocess.call([editor, file.name])
            try:
                card = crud.load_flashcard(file.name)
            except NotEnoughCardSidesException:
                adding = False
        if adding:
            asyncio.run(crud.add_card(context, card))
            count += 1
        else:
            rich.print(f"Added {count} cards.")
            click.Abort()
