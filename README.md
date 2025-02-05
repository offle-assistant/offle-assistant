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

### Refactor: config file (COMPLETED)
Decide whether the server info should be stored in the same config file as the personas or a different one.
Maybe this should be a system configuration file store in /etc/offle-assistant/
On second though, I think it should be in a few places probably. 
Check in the following order:
* /etc/offle-assistant
* its own server block of the user config
* individual keys on each persona
* CLI arguments

Server config should be overwritten by configs later in the chain, personas should be appended to the persona list.

In this task, I also need to fix the janky handling of the config file. I need to create a constants.py file that has the config locations.
I also need to figure out a better way to handle loading configs. I think that the config should be loaded earlier in the program. Probably
best way to do this is by having a configuration class which takes the configuration as a python dictionary and creates the configuration object.
I should also have a PersonaConfig class that holds all the necessary configuration values for the persona in a lightweight class that can
be passed directly to the Persona constructor like persona = Persona(persona\_config).

# Game plan for this task:
    * Add new config file to /etc/offle-assistant/config.yaml and test loading from it.
    * Create some format check for the yaml file.
    * Create Config class. This class should store personas as a list of persona dictionaries

# Main goals
    * I want the persona class to be config agnostic. I want it to just have a bunch of input parameters with default values.
    * I want the config file to be loaded by a class so that I can handle indexing into the dictionary in one place only.

# Subtasks
* format checking for yaml (COMPLETED)
* Create Config and PersonaConfig classes (COMPLETED)
* Add checks for system and user config files. (COMPLETED)

### I need to fix the formatting stuff (COMPLETED)
Right now, I think there's still some formatting stuff tied into the individual personas and there shouldn't be.
Maybe the formatting options for individual personas should be removed for now. Formatting stuff is only global

### Simplified RAG functionality (COMPLETED)
Create simplified RAG system. supply yaml file with a directory where the RAG docs live. If there is a RAG index file in the root of this directory,
then use this for RAG. If there isn't, create the index. For the time being, each document gets its own vector representation and a hit will return
the whole document. This will be well suited for reading papers. This should include another subcommand called "rag" which has --generate and --list
options. An isolated --generate option will generate RAG indices for all personas, but you can provide a persona name to generate RAG indices for
only that persona.

Indices should be per-sentence in each document. A hit will return the entire document.
This has obvious limitations. If a document is very long, it will fill up the entire context window.
For this method, documents will need to have a length maximum.

# Subtasks
* Create directory in ~/.config/offle-assistant/rag/ralph/ which will house the docs. (COMPLETED)
* Update the config file accordingly (COMPLETED)
* Populate the directory with PDF files in the ./src/ (COMPLETED)
* Choose a vector database provider: (COMPLETE)
    * We can actually support multiple.
    * For now, lets go with qdrant
* Set up the database
    This is as simple as running a docker container. I should make sure to set it up with docker-compose for maintainability.
* Create subcommand which indexes all the documents and stores the vectors in the database
    * Takes everything from the src dir and converts them into parseable formats with pymupdf4llm
    * Sentence-level or paragraph-level vector embeddings
    * Store them in the database
        This will require payloads.
        {
            "doc\_id": "12i1qrf8",  # This is a hash of the document. Guarantees uniqueness and will change if the doc changes.
            "file\_name: "scientific\_paper.pdf",
            "chunk\_idx": 4,  # useful when I want to provide text from around the hit. "select embedded\_text where doc\_id is 12i1qrf8 and chunk\_idx is 3"
            "file\_path": "path/to/file/scientific\_paper.pdf",  # path may change. Further case for add/delete documents tools in the cli tool
            "embedded\_text": "This is very important information that you just queried for.",
            "subset\_id": "ralph",  # For now, this will be set by the bot. But user's should be able to select a list of subsets they'd like to query.
        }
    * I need a single function which takes a PDF and then:
        * Creates a hash of the PDF (COMPLETED)
        * Checks to see if the hash (doc\_id) exists in the database. (COMPLETED)
        If it does
        * return
        If it doesn't
        * Converts it into markdown (COMPLETED)
        * Chunks it into separate paragraphs (COMPLETED)
        * Performs embeddings on each paragraph making sure to take note of the index of each chunk  (COMPLETED)
            this will be its own function so I can try to parallelize here but also so i can plug in different vectorizers trivially.
            use sentence-transformers. Where is the model stored locally?
        * returns a list of entries to the Qdrant database. (a dictionary with a vector and a payload) (COMPLETED)
    * Current issues:
        Right now, I don't have a great way to handle different models

* Create function that performs the same embedding process on a query sentence. (COMPLETED)
* Create function which queries the database. (NEXT ON THE LIST)
    Part of this is going to be reformatting the config file so that the correct database collection is queried.
    Ideas:
        * For now, let's just have one DB. The DB is specified in the global\_settings key of the config.
        * Users can specify which collections they have access to.
        * Down the road, we should have collections have "ownership" so that users can create new collections and have full read/write access to them
            or they can use the administrator's collections.
    GamePlan:
    * Catch some sort of query phrase "query test\_db: What is a large language model?"
    * Persona connects to the qdrant server and grabs the vectorizer from the specific collection.
    * Persona uses Vectorizer.embed\_sentence(query)
    * Persona queries the qdrant database for a hit from the database.
    * Persona uses this context for it's response.
    I need to think about this more. Where should the retrieval happen? What should be retrieved? Just the string for the chunk? Or should there be a more
    informative, rich return?
    Should there be a chat interface method that redirects to normal chat and rag chat methods? I need a break.

* Create new Persona.chat\_w\_rag(user\_query) which performs chat but with the context prepended to the query.
    * I also want this to provide the excerpt that was the hit to the user and tell the user explicitly where it got it from.
    * It must include path to the file and line number.
* Create a catch in the cli which intercepts messages including something like "Search Database for: " and calls the new Persona.chat\_w\_rag method
* Add a test to make sure it's working. One possible automated test would be to check a query that exactly matches a line in the corpus.
* Create --add option to the rag subcommand that gives you the ability to add documents to the rag dir.

### Refactor QdrantServer (COMPLETED)
* This needs to be a child class of a more general VectorDatabase class.
* This needs to be able to connect to the server, add new collections, somehow manage which vectorizer is used for each
collection. I think this task and the Vectorizer refactor need to happen in tandem.
* A TEMPORARY SOLUTION: in the metadata for a collection, I store a "vectorizer\_string". In the Vectorizer module,
there will be a dictionary with a translator that takes a key and outputs the Vectorizer object. This grants us
the ability to load the correct Vectorizer when we open an existing database. 
* Part of this refactor, I need to change how this class deals with collections. This class should be able to manage multiple collections at the same time.
This means that it should be able to create new collections, add docs to specific collections, delete collections, etc.
This allows us to provide collection names, model names, and Vectorizers only when we're creating new collections.
When we are querying existing collections or adding documents to existing collections, all we need is the collection name and the rest will be taken care of
automatically.

### Refactor Vectorizer (COMPLETED)
Right now the embeddings are just done with a bunch of loose functions. This should really be a Vectorizer parent class with a SentenceTransformerVectorizer subclass.
the SentenceTransformerVectorizer constructor will take the model name as a parameter.
This way, I'll be able to share one interface for all vectorizers.

### Refactor Create parent classes, interfaces, for Vectorizer and VectorDB (Completed)
I need to make the interfaces for QdrantDB and Vectorizer so that we can trivially add new Vectorizers and Vector Databases


### RAG Improvements 1 (COMPLETED)
RAG query hits should have an object. This should allow us to provide the filename and the filepath at least.

We should also have a verbose flag, a few levels of it. So that people can see the documents that get returned. This
print out should also include how close to the hit the original sentence was.

Whether we're streaming or not streaming, I think the return value of the Persona.chat() method needs to be some sort of
object, not a bare iterator. (Side note, I think I have the type hints wrong, I have the Chat.response for streaming
marked as a generator instead of an iterator.)

### RAG Improvements 2
Retrieval object should also provide a distance property. (COMPLETE)

Allow addition of LaTex files. (COMPLETE)

Create smarter chunking algorithm 
    * maybe chunking with minimum token counts.
    * Maybe with chunk overlaps

Create RAG options dict/struct so that we can set things like threshold, num of chunks, etc
    Eventually, I want this type of thing displayed in the UI.

### Database improvements
I need to rethink how the DB will be used.

For example, If I'm looking for a specific piece of information from a specific source, i.e. a novel, I should be able to tell the agent exactly which source to look in.

So two use cases for the database I guess. 
    * One way to search is "Can you answer questions about a specific text?". 
    * The other way is, "What kinds of characteristics does mecury have?" or "What is my company's vacation policy?"

### RAG Future ideas
The more I research this, the more I feel like we need a custom solution. Table, charts, and images in latex files could be really important. Therefore,
some sort of text-based description of the image could be really important. In the case that we see something like this, we could have an image model
read the figure and create a textual description of the table and have this be the embedding. And then we store the path to the table in the metadata
for the PointStruct. If we get a hit, we return the textual original figure as well as some surrounding text.

### Switch out jsonSchema for Pydantic
    Pydantic is just way more legible

### Create message history
I want at least a log of conversations per-persona. One file per conversation.

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
        * \# of paragraphs
        * \# of sentences
* Semi-Structured text
    * Novel with chapters
    * collection of news articles
    * scientific papers
    * This should have a mix of blocks and windows probably.
