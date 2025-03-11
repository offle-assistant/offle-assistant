import json
import logging
import pathlib
import time
from typing import List, Dict

from bs4 import BeautifulSoup
from pydantic import RootModel
import requests

from offle_assistant.constants import CACHE_DIR


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


def fetch_model_tags(model_url):
    """Fetch tags from a model's individual page."""
    response = requests.get(model_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tags_sections = soup.find_all('a', href=True)
        tags = []

        for section in tags_sections:
            tag_div = section.find('div')
            if tag_div:
                tags.append(tag_div.text.strip())

        return tags
    return []


class ModelTags(RootModel[Dict[str, List[str]]]):
    """

    a dictionary of the form {"model_name": ["tag1", "tag2"]}

    """
    pass


class AvailableLanguageModels(RootModel[Dict[str, ModelTags]]):
    """

    a dictionary of the form:

    {
        "provider_name": {
            "model_name": ["tag1", "tag2"]
        }
    }

    """
    pass


def retrieve_available_models(
    force_update=True
) -> AvailableLanguageModels:
    cache = pathlib.Path(CACHE_DIR, "available_models.json")

    if (cache.exists()) and (force_update is False):
        with open(cache, "r") as f:
            data = json.load(f)
            return AvailableLanguageModels(data)
    else:

        ollama_url = "https://ollama.com"

        models = fetch_model_list(url=ollama_url)

        counter = 0
        available_models_dict = {}
        available_models_dict["meta"] = {}
        for model, url in models.items():
            logging.info(f"Fetching tags for {model}...")
            tags = fetch_model_tags(url)
            available_models_dict["meta"][model] = tags
            time.sleep(1)
            counter += 1

        available_models: AvailableLanguageModels = AvailableLanguageModels(
            **available_models_dict
        )

        with open(cache, "w+") as outfile:
            json.dump(available_models.model_dump(), outfile, indent=2)
        return available_models


if __name__ == "__main__":
    retrieve_available_models(force_update=True)
