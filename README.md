# Offline Assistant
This is a self-hosted cli LLM framework.

## CLI Interface:

poetry run python assistant/main.py chat --persona Ralph
poetry run python assistant/main.py persona --list

## To-do:
### Config file for stylization, model selection
(COMPLETED) The config file will be a yaml file with a "personas" key. Each persona can be fully editable with visual stylizations, system-prompts, and model selection. There should also be an entry for the RAG docs that are accessible to them. Since some personas may share RAG docs/configurations, it may be best to have the RAG docs all stored in one spot and just have a list of available docs stored in this config file. (COMPLETED)

(COMPLETED) I created the config. But with this method, I created separate Persona and Bot classes. I should really just move the Bot.chat method over to the Persona and have the Persona be the chat agent. (COMPLETED)

(COMPLETED) At some point, I need to pull apart the chat functionality from the printing. Chatting should really just take input text and return the "display name" and the output. So that the recipient can handle it and put it into whatever UI they deem fit. I need to make sure that I account for streaming with this method.

### RAG framework tested with GNU documentation
While RAG docs should be added via a commandline tool, they should then be stored in a config file that is user-readable and user-editable.
*  Structured Text:
    * like GNU docs
    * Ability to specify headers/subheaders
    * Ability for a user to load in documents
    * Should save docs and index to a location like ~/.assistant
* Unstructured Text:
    * Huge block of text
    * This should use windows.
    * User can specify window size
        * # of paragraphs
        * # of sentences
* Semi-Structured text
    * Novel with chapters
    * collection of news articles
    * scientific papers
    * This should have a mix of blocks and windows probably.


