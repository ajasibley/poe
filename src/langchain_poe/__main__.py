import os
import importlib

from fastapi_poe import run

import poe
from poe import LangChainCatBot

if __name__ == "__main__":
    # Reload the 'poe' module to apply the changes
    importlib.reload(poe)

    run(LangChainCatBot(os.environ["OPENAI_API_KEY"]))
