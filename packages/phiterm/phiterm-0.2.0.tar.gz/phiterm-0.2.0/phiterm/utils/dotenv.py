from pathlib import Path
from typing import Optional, Dict

from phiterm.utils.log import logger


def load_dotenv(workspace_root: Optional[Path]) -> bool:

    if workspace_root is None:
        return False

    dotenv_file = workspace_root.joinpath(f".env")
    if dotenv_file is not None and dotenv_file.exists() and dotenv_file.is_file():
        logger.debug(f"Reading {dotenv_file}")

        from os import environ
        from dotenv.main import dotenv_values

        dotenv_dict: Dict[str, Optional[str]] = dotenv_values(dotenv_file)
        env_dict: Optional[Dict[str, str]] = {
            k: v for k, v in dotenv_dict.items() if v is not None
        }
        if env_dict is not None:
            environ.update(env_dict)
        return True

    return False
