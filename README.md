# Offline Assistant
This is a self-hosted cli LLM framework.

## CLI Interface:

poetry run python assistant/main.py chat --persona Ralph
poetry run python assistant/main.py persona --list

## To-do:
### Config file for stylization, model selection (COMPLETED)
The config file will be a yaml file with a "personas" key. Each persona can be fully editable with visual stylizations, system-prompts, and model selection. There should also be an entry for the RAG docs that are accessible to them. Since some personas may share RAG docs/configurations, it may be best to have the RAG docs all stored in one spot and just have a list of available docs stored in this config file. (COMPLETED)

### Refactor: create Persona.chat() for chat functionality (COMPLETED)
I created the config. But with this method, I created separate Persona and Bot classes. I should really just move the Bot.chat method over to the Persona and have the Persona be the chat agent. (COMPLETED)

### Refactor: printing is in cli code instead of in chatbot code. (COMPLETED)
At some point, I need to pull apart the chat functionality from the printing. Chatting should really just take input text and return the "display name" and the output. So that the recipient can handle it and put it into whatever UI they deem fit. I need to make sure that I account for streaming with this method.

### Create default config file (COMPLETED)
Create default configuration file that can be copied to the necessary location.

### Refactor: create cli class (COMPLETED)
Separate CLI into its own class. __init__() will handle setting cli args, run() will handle running the program.

### Refactor: config file
Decide whether the server info should be stored in the same config file as the personas or a different one.
Maybe this should be a system configuration file store in /etc/offle-assistant/
On second though, I think it should be in a few places probably. 
Check in the following order:
* /etc/offle-assistant
* its own server block of the user config
* individual keys on each persona
* CLI arguments

In this task, I also need to fix the janky handling of the config file. I need to create a constants.py file that has the config locations.
I also need to figure out a better way to handle loading configs. I think that the config should be loaded earlier in the program. Probably
best way to do this is by having a configuration class which takes the configuration as a python dictionary and creates the configuration object.
I should also have a PersonaConfig class that holds all the necessary configuration values for the persona in a lightweight class that can
be passed directly to the Persona constructor like persona = Persona(persona\_config).

### Simplified RAG functionality
Create simplified RAG system. supply yaml file with a directory where the RAG docs live. If there is a RAG index file in the root of this directory,
then use this for RAG. If there isn't, create the index. For the time being, each document gets its own vector representation and a hit will return
the whole document. This will be well suited for reading papers. This should include another subcommand called "rag" which has --generate and --list
options. An isolated --generate option will generate RAG indices for all personas, but you can provide a persona name to generate RAG indices for
only that persona.

Indices should be per-sentence in each document. A hit will return the entire document.
This has obvious limitations. If a document is very long, it will fill up the entire context window.
For this method, documents will need to have a length maximum.

### Installation instructions
Create installation instructions for macOS/Linux with a script that can automate the process.
    install ollama
    copy config to proper location
    poetry install

### Ollama wrapper to facilitate multi-user use cases.
There are certain aspects of ollama that don't lend it to easy use on a system with multiple users.
* models are stored in home directory by default
    * OLLAMA\_MODELS environment variable can be set to change this
Things that might work well:
* If two users pull the same model to the OLLAMA\_MODELS directory, will they sync up?
* How are user permissions handled in this case? Is the model owned by the person who pulled it? We may need to create an ollama user that owns the models.

### Ollama modelfile support
Think about the ability to use ollama native modelfiles with the config. In the very least, we should be able to translate a modelfile into a config entry.

### PDF support
To start, I'm going to have RAG just handle text documents, but this should be able to support PDFs in the future.

### RAG framework tested with GNU documentation
While RAG docs should be added via a commandline tool, they should then be stored in a config file that is user-readable and user-editable.
Some notes on this... It might be better to enforce a structure to the documents. A separate tool can be developed to organize documents
into a structure/format that offle-assistant can parse easily.
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
