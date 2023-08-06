from pydantic import BaseModel


class AppConfig(BaseModel):
    """Config."""

    debug: bool
    verbose: bool
    interactive: bool
    data_dir: str
    config_dir: str
    state_dir: str
    log_dir: str
    flashcards_dir: str

    def save_to_file(self, filename: str):
        return

    def load_from_file(self, filename: str):
        return
