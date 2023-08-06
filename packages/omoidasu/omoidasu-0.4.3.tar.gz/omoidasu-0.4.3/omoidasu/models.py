import logging
from typing import Iterator, List, Optional

import rich
from pydantic import BaseModel

from omoidasu.exceptions import NotEnoughCardSidesException

logger = logging.getLogger(__name__)


class Side(BaseModel):
    """Card side model."""

    id: int  # Line number.
    content: str

    def __str__(self):
        return self.content.replace("\n", "")


class Card(BaseModel):
    """Card model."""

    filename: Optional[str]  # Can be None, if not saved to file.
    sides: List[Side]

    def __init__(self, *args, filename: str, sides: List[Side]):
        length = len(sides)
        if length < 2:
            raise NotEnoughCardSidesException(filename, length)
        super().__init__(filename=filename, sides=sides)

    @classmethod
    def load_from_file(cls, filename: str):
        """Loads card from file."""
        logger.info("Loading card from %s", filename)
        sides: List[Side] = []
        with open(filename, "r", encoding="utf-8") as file:
            for i, line in enumerate(file.readline()):
                side = Side(id=i, content=line)
                sides.append(side)
        if len(sides) == 0:
            raise NotEnoughCardSidesException(filename, len(sides))
        card = cls(filename=filename, sides=sides)
        logger.info("Loaded %s from %s", card, filename)
        return card

    def get_questions(self) -> Iterator:
        for side_1 in self.sides:
            for side_2 in self.sides:
                yield Question(card=self, question=side_1, answer=side_2)


class Question(BaseModel):
    card: Card
    question: Side
    answer: Side

    def ask(self):
        rich.print(f'[grey]Card "{self.card.filename}"[/grey]')
        _ = input(self.question)
        result = input(self.answer)
        if result not in ["", "y", "Y", "\n"]:
            rich.print("[red]Wrong.[/red]")
        else:
            rich.print("[green]Correct.[/green]")
