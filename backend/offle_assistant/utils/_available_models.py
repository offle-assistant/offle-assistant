import json
from filelock import FileLock
import logging
import pathlib
import time
from typing import List

from bs4 import BeautifulSoup
import requests

from offle_assistant.constants import CACHE_DIR
from offle_assistant.models import (
    LanguageModelsCollection, TagInfo
)


def fetch_model_list(url):
    """Fetch all model names and their URLs from the Ollama library."""
    response = requests.get(url + "/library/")
    models = {}

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        model_links = soup.find_all('a', href=True)

        for link in model_links:
            href = link['href']
            if href.startswith('/library/'):
                model_name = href.split('/')[-1]
                models[model_name] = f"{url}{href}/tags"

    return models


def fetch_model_tag_list(model_url) -> List[TagInfo]:
    """Fetch tags from a model's individual page."""
    response = requests.get(model_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        model_info_blocks = soup.find_all("div", class_="flex-1")
        tag_info_list = []
        for block in model_info_blocks:

            tag_name_div = block.find(
                "div",
                class_=(
                    "break-all font-medium text-gray-900 group-hover:underline"
                )
            )
            tag_name = tag_name_div.text.strip() if tag_name_div else "Unknown"

            details_span = block.find("span")
            if details_span:
                details = details_span.text.strip().split(" • ")
                tag_hash = details[0] if len(details) > 0 else "Unknown"
                size = details[1] if len(details) > 1 else "Unknown"
                updated_time = details[2] if len(details) > 2 else "Unknown"
            else:
                tag_hash, size, updated_time = "Unknown", "Unknown", "Unknown"

            tag_info = {
                "name": tag_name,
                "hash": tag_hash,
                "size": size,
                "updated": updated_time
            }

            tag_info_list.append(tag_info)

        return tag_info_list
    else:
        return None


def retrieve_available_models(
    force_update=False
) -> LanguageModelsCollection:
    """
        This is really just a place holder. It only grabs ollama models rn.
    """

    cache = pathlib.Path(CACHE_DIR, "available_models.json")
    lock_file = cache.with_suffix(".lock")

    with FileLock(lock_file):
        if (cache.exists()) and (force_update is False):
            print("Found existing json file.")
            with open(cache, "r") as f:
                data = json.load(f)
                return LanguageModelsCollection(**data)
        else:

            print("No existing json file. Pulling data remotely.")
            ollama_url = "https://ollama.com"

            models = fetch_model_list(url=ollama_url)

            counter = 0
            available_models_list = []
            for model, url in models.items():
                # if counter > 2:
                #     break

                logging.info(f"Fetching tags for {model}...")
                tags = fetch_model_tag_list(url)
                current_model = {}
                current_model["name"] = model
                current_model["provider"] = "meta"
                current_model["api"] = "ollama"
                current_model["tags"] = tags
                available_models_list.append(current_model)
                time.sleep(1)
                counter += 1

            available_models: LanguageModelsCollection = (
                LanguageModelsCollection(
                    models=available_models_list
                )
            )

            with open(cache, "w+") as outfile:
                json.dump(available_models.model_dump(), outfile, indent=2)
            return available_models


if __name__ == "__main__":
    retrieve_available_models(force_update=True)
