# Offline Assistant
This is a self-hosted cli LLM framework.

## CLI Interface:

poetry run offle\_assistant\_cli chat Ralph --rag
poetry run offle\_assistant\_cli rag --add /path/to/doc.tex -c "new-collection"

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

### Refactor Create parent classes, interfaces, for Vectorizer and VectorDB (COMPLETED)
I need to make the interfaces for QdrantDB and Vectorizer so that we can trivially add new Vectorizers and Vector Databases


### RAG Improvements 1 (COMPLETED)
RAG query hits should have an object. This should allow us to provide the filename and the filepath at least.

We should also have a verbose flag, a few levels of it. So that people can see the documents that get returned. This
print out should also include how close to the hit the original sentence was.

Whether we're streaming or not streaming, I think the return value of the Persona.chat() method needs to be some sort of
object, not a bare iterator. (Side note, I think I have the type hints wrong, I have the Chat.response for streaming
marked as a generator instead of an iterator.)

### RAG Improvements 2 (COMPLETE)
Retrieval object should also provide a distance property. (COMPLETE)

Allow addition of LaTex files. (COMPLETE)

Create RAG options dict/struct so that we can set things like threshold, num of chunks, etc (COMPLETED)
    Eventually, I want this type of thing displayed in the UI.

### Switch out jsonSchema for Pydantic (COMPLETE)
    Pydantic is just way more legible

### Create a web server with a basic rest api (COMPLETE)
built with fastAPI. Just to test out a bit of its functionality


### I need to do a big refactor to get the rest api to work. (COMPLETE)
This mainly came down to my lack of understanding of pydantic. It's pretty sick actually. Really nifty.
A few key changes made the whole system of passing data way easier and safer.


### I need to make some design decisions

HPC/CLI
    main benefit of this I see is that the LLM server can run in one central location.
    sys admin runs the LLM server 24/7
    users have a docker container they can use to start the vector db and access cli
    A user has config in their home directory.
    Can add documents via command line.
    Users need to use their config file to point the client to the correct LLM server.
    Because a user might be on multiple projects, we may need a way of putting a persona
    in a group. This way, that persona can point to a specific vector db.
    This is just going to be a bit tricky for users unfortunately ://

HPC/OOD
    When a user wants an LLM session:
        the GPU node is allocated, llm server is spun up
        your available vector dbs are spun up
    in the web interface, you can select different collections/vector dbs
        but this is done with a gui and names, not with hostnames and ports
        though of course, behind the scenes, this is how its done.
    You can chat, add docs, etc
    User configuration is stored in home directory, but what's necessary here?
        personas
        conversation history
        As far as general settings go, I need log files? convo history location for sure
    
Business/Web Interface
    config files in the home directory don't really work here unfortunately :/
        I just need a sql database for the personas.
    So....
    someone from devops sets this up for their business.
        all local:
            docker-compose will do the following
                stand up an ollama container
                    starts ollama 
                stand up a qdrant container  # authentication can be done per-collection
                    starts qdrant
                stand up an offle-assistant container
                    likely, sysadmin will want to set some things like port it's listening on
                    starts offle-assistant fastapi server
                    starts sql database server

            sys admin sets up a reverse proxy on their system to direct traffic to a specific company
                owned url to go to the offle-assistant server once authentication has passed

        all cloud:
            a bit easier...
                the process of spinning everything up can be uniform
                web interface to start the services, get more storage/compute etc...
                gives the admin a url to give to employees
                there should be two interfaces for a company
                    admin
                        can create collections for anyone
                    employee
                        can create personal/group collections
             



### Build out the production REST api
NEXT Create a getPersonas(user\_id) route and hook it up to react.
Sending data
    send a message to a specific bot and get a response
        This requires loading the PersonaConfig

    send a message to a different bot
        This requires
            loading a different PersonaConfig
            saving message history
                I think this gets saved locally in .config/offle-assistant/<bot-name>/
                No need to send it to the client and then back, right? yes.

    update the config for a bot (what happens to message history?)
    load config for settings
    add a rag document
    view the document before/after markdown conversion

Recieving data
    request the config file on a user's system.
    request message history
    receive messages from bot

persona\_cache = {
    "persona": {
        "persona\_id": "p9823lfhap98h21n",  \# hash, primary key for sql database persona schema
        "timestamp": 123112421412  # so the oldest one can go when needed
    }
}

a few realizations:
    * vector db shouldn't be part of the persona. There's no reason to have multiple databases here.
    The vector db and the collection name(s) should be provided to the request for chat.
    in other words, there should be a rag payload like (vectordb, collection\_list)
    and the vectordb lives as a global variable that is created when the server is spun up and kept
    around to be passed into the chat request method on the persona when it comes time to make a query.
    This will honestly work with the cli version of this app as well. When you start a chat, you spin
    up the server. I just need to make minor modifications to the Persona Class. I should make the
    LLM server modifications at the same time. Specifically, taking "hostname/port" out of the constructor
    and replacing it with the server client itself.
    * Creating a wrapper for the LLM client is going to be 100% necessary in order to support multiple
    LLM clients. I should really make this change immediately so that I can work this into the rest api.
    How do I pick the client? It's based on the model choice, right? In the future, when I add a new model
    how do I want to update the code to account for this? I want to change it in 1 place only. 
    If I do create a set of client classes, when the REST server is started, I can "start" all of the client.
    What that really means is creating all of the client classes. Then, I can use a method on there to get
    a list of all available models. What this will mean for OpenAI is querying the OpenAI client to see which
    models your API key gives you access to (this may be user-based so I may have to do it for each user when 
    they start their connection). For ollama, it means running 'ollama ls'. So any model you have already pulled
    is accessible. Which ollama models are accessible on a locally run system should be administered by the sys
    admin because they might not want people running models bigger than they can actually run on their system.
    So we can use these values to populate a dictionary of lists, key is the api, list is the models available.
    So the models in the web ui will be populated by this dictionary, and then when the user requests use of
    a specific model, we look in the dictionary to see which key contains that model, and we use that model
    string with the appropriate client object to update the client object and then provide it to the persona.
    This object needs to be different from how the qdrant server is designed. This should really be more of a
    model factory object. It has global state information such as the hostname/port/available models but when
    the Persona uses it, they use it to spawn a model object which it can use to interface with the client
    Wait.. So what I have right now is actually really close. The individual personas don't need to have a model
    in their constructor. They SHOULDN'T, what we need to do is have the model as part of the chat method. This
    way, users can change model mid-conversation. It also works way better with the flow. In fact, there's
    absolutely no reason why a Persona should even be locked to an API. The only thing the persona constructor
    really needs is a system prompt, collections, name, description, and persona\_id.
    * With my current approach, every user is going to be hitting the same global variables. This isn't good.
    I think redis is going to be my best approach here but I need to research it a bit more.


What will this mean for the cli program and config files?
It means that all server configs will be in settings. That's honestly it I believe.

Persona Refactor:
constructor(name, description, model, system\_prompt, rag\_prompt)
    \# importantly, here model isn't used in the constructor to
    \# set anything aside form the self.model property.
    \# This can be changed when in a conversation. 
chat(msg, client)
    ChatResponse = client.chat(msg, self.model, stream)
get\_config() -> PersonaConfig:
    \# used when it's time to save a PersonaConfig to the sql db

PersonaConfig: This is used to populate the sql database and to load a Persona.


LLMClient:
chat(model, message\_chain, stream):
    \# Behind the scenes, this will look up which API the model belongs to
    \# and call the appropriate chat method: ollama\_chat(args), openai\_chat(args), etc
get\_model\_dict():
    \# {'open-ai': ['gpt4o', 'gpt4o3-mini'], "ollama": ["llama3.2", "llama3.1"]}  \# include tags
    \# This will be used internally to call the appropriate chat method.
    \# This will also be called by the rest api to send a list of models/apis to
    \# the web client. Eventually, the list will be determined by an API key for chatgpt models


Functions I need:
    All of these are going to require the user\_id to be sent in from the client
    so that the proper session info can be loaded from the redis cache.

    before I can make any of these other ones, I'm going to need to set up the sql
    database :/

add\_user(user\_info): (COMPLETE)
update\_user(user\_id, user\_info): (COMPLETE)
delete\_user(user\_id): (COMPLETE)

save\_persona(PersonaConfig) -> OK:
    \# This puts a new persona into the sql db
    \# Not necessarily called every time someone starts a conversation
    \# A conversation can be started with a new PersonaConfig before it
    \# gets saved

load\_persona(persona\_id) -> OK:
    \# This puts current persona into the cache
    \# and then loads the persona from the sql db
    \# and stores it in a global variable.

send\_message(msg, rag\_payload: Optional[RagPayload]) -> PersonaChatResponse:
    \# Sends a message to the currently loaded persona.

update\_persona(persona\_id, PersonaConfig) -> OK:
    \# This updates an existing entry in the Persona sql db

update\_conversing\_persona(PersonaConfig) -> OK:
    \# This is going to call the same function update\_persona()
    \# uses to update the entry in the database, but it also
    \# reloads the persona that you're conversing with.
    \# in other words, it's going to check the redis database
    \# for an entry and update it there.

upload\_document(document\_file) -> converted\_doc:
    \# this should take a doc, convert it into markdown and show
    \# it to the user. Both docs side-by-side
    \# It is likely a good idea to have a markdown editor 
    \# in this view. So that users can clean up their
    \# documents before sending it off to be stored.

save\_document(converted\_doc, collection\_name) -> OK:
    \# after cleaning up the document and marking
    \# the chunks, send it off to be saved.

add\_collection(collection\_name, password) -> OK:
    \# Users can add their own collections here behind
    \# their user password.
    \# Before I touch this, I need to better research how 
    \# qdrant authentications work.
    \# This function will likely change a lot



User Interface Functionality:

Persona Select Window (Landing page)
    New Persona -> opens a default Persona Configuration window

Persona Configuration Window
    Change name
    Change model
    Change system Prompt
    Change RAG prompt
    Change available collections
    [Start Chat Button]  [Save Persona Button]

Chat Window
    When there's a RAG hit, I want the markdown displayed in markdown nice and pretty.
    I also want a download button for the original RAG doc.
    [Download Document Button]
    I want code to be properly displayed with syntax highlighting
    [Copy output Button]
    Scrollbox for AI's text
    A dropdown to change the model. This should have an "update persona" button to save
    [Update Persona Button]
    the model selection to the configuration.

Settings Window
    Change some file locations?





vvvvv First draft of rest api plan vvvvv
send\_message(persona\_id, msg) -> PersonaChatResponse:
    \# Check if persona\_id is in cache
    \# if not, load persona
    \# send a message and wait for reply.
    \# The PersonaChatResponse object needs to keep the
    \# doc\_id and some other stuff around about the
    \# RAG document.

load\_persona(persona\_id) -> OK:
    \# The config lives on the host system, right? 
    \# So we can look up the PersonaConfig by persona\_id

save\_persona(persona\_id, PersonaConfig) -> OK:
    \# When we make changes to the persona in the browser,
    \# we've gotta save the changes on the server.

load\_settings(): -> OK:
    \# Again, config lives on system.

save\_settings(SettingsConfig): -> OK:
    \# When the user makes settings changes in browser
    \# these values must be saved in the server config

upload\_document(document\_file) -> converted\_file:
    \# This is just the upload step. Both images will be
    \# displayed side-by-side

save\_document\_to\_collection(converted\_doc, collection\_name) -> OK:
    \# Not sure how this is going to work on the back end yet.
    \# Probably, the chunking will happen on the back end after
    \# the save button has been pushed.

download\_document(doc\_id) -> file:
    \# When you get a doc hit on RAG, you should have the option
    \# to redownload the doc. The client will have get doc\_id
    \# So it will be trivial to find it to download.

add\_collection(collection\_name, collection\_description, vectorizer) -> OK:
    \# Users may need to add collections sometimes.

^^^^^^ First draft of rest api plan ^^^^^^




### refactor llm server 
I need to turn it into its own class so that I can interface with it like I do with the vectordb
This is the solution for providing openAI and ollama and whoever else.

### Write a test framework
something robust!!

### Create message history
I want at least a log of conversations per-persona. One file per conversation.

------------------------------------------------
General implementation thought/ideas
------------------------------------------------

I've been thinking about how to deploy an agent that you've created. I think the idea of a config file is the right one.
But with this, I do think that there needs to be a decision made about how to handle directing the bot to the correct
ollama/openAI/Qdrant server. Right now, url is handled in global state. However, the Persona actually only handles this
url at the time the request is made. side note: I should really also put the collections in here too. but basically,
what I have right now is a framework for BUILDING an agent. Yes, you can use it within this framework and make tweaks
and such. But this is really primarily for building and then exporting a yaml file that describes the bot. This yaml
file probably should be different from the one I built. I should group key/value pairs more along the lines of what makes
sense. In other words, key for persona (model, system-prompt, description, name, temperature, token limit, api-token), one 
for rag (server url, threshold, collections, api-token), and I think that's about it, right? Then you can share this file
with someone. Obviously, the tokens will be blank when you share the file. 

There will be a web interface exclusively for users. This has your available agents on the left and your that window in
the center. There will be a "load agent" button on the left side with the available agents.  When you load the config file
in, it will prompt you for your tokens. Once you input the tokens, you'll have full access to use the bot within this
interface.

------------------------------------------------
Further along in the future
------------------------------------------------


### Database improvements

I need to rethink how the DB will be used.

For example, If I'm looking for a specific piece of information from a specific source, i.e. a novel, I should be able to tell the agent exactly which source to look in.

So two use cases for the database I guess. 
    * One way to search is "Can you answer questions about a specific text?". 
    * The other way is, "What kinds of characteristics does mecury have?" or "What is my company's vacation policy?"


### Use case idea
In the user interface, when we are saying "Given this document, can you answer questions?" if the doc is too big,
we could read it into a database in chunks and query it with RAG.


### Installation instructions
Create installation instructions for macOS/Linux with a script that can automate the process.
    install ollama
    copy config to proper location
    poetry install

### User generated chunking rules
This is for way in the future. But I think there should be a way to mark up a document in the GUI for the kinds of chunks you want.
Once a user makes these markings, they can apply the same splits to every doc of the same general format.
To solve this, maybe we make LLM generated regex expressions to catch things.
The user should then be able to cycle through the documents in that folder to make sure they're getting parsed correctly.

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

### System check
There should really be a system check in this thing when you try to use a model. We should at least check to see if model size
exceeds VRAM and system RAM and give messages accordingly so people know that the model they're about to use is too big
for their system.

### RAG Future ideas
The more I research this, the more I feel like we need a custom solution. Table, charts, and images in latex files could be really important. Therefore,
some sort of text-based description of the image could be really important. In the case that we see something like this, we could have an image model
read the figure and create a textual description of the table and have this be the embedding. And then we store the path to the table in the metadata
for the PointStruct. If we get a hit, we return the textual original figure as well as some surrounding text.

### I just need to add support for both the ollama-python and the openai-python API
This is just going to be necessary unfortunately.
ollama/openai support isn't 100% done. nor is it guaranteed to keep existing in the future.


### Create smarter chunking algorithm
One big thing I need to consider is that there may be different chunking methods/retrievals required. 
* One example: Someone might want to chunk their docs manually. This could work where each chunk is in
its own doc, and a hit on one sentence with similarity search returns the entire doc.
* Another example: the similarity by chunks example we already have.
* Another example: chunks are returned in windows. That is, when a chunk gets a hit, we get x chunks before and y chunks after.

will these different methods require different database structures? Or can I keep all this info in the payload and have different
types of queries? 
    Maybe a specific type of query will return everything from the parent doc concatenated back together.
    This is probably the way. I can handle each of the above 3 methods with the current implementation
    So basically, we just need a parameter in VectorDb.query\_collection() that sets how we search the db?
        only weird thing about this is that the "window\_size" related options will be there regardless of
        whether we're doing a windowed search. This could be confusing but I can live with it. We should
        have a console log for this though. Like the window size defaults to None, and if you try to set it
        without using the windowed parameter, then it gives you a warning.

If I do need different implementations though, I may need to add more info to the metadata entry so that I can
initialize the right VectorDb class for the right database.

* maybe chunking with minimum token counts.
* Maybe with chunk overlaps
* What if I use the vectorizer for this? It would require some heuristics but I could:
    * Check if a chunk is too small to be on its own.
    * If it is, check if it has a cosine similarity above a specific threshold with the
    next chunk


------------------------------------------------
no longer relevant
------------------------------------------------

### Ollama wrapper to facilitate multi-user use cases.
There are certain aspects of ollama that don't lend it to easy use on a system with multiple users.
* models are stored in home directory by default
    * OLLAMA\_MODELS environment variable can be set to change this
Things that might work well:
* If two users pull the same model to the OLLAMA\_MODELS directory, will they sync up?
* How are user permissions handled in this case? Is the model owned by the person who pulled it? We may need to create an ollama user that owns the models.

### Ollama modelfile support 
Think about the ability to use ollama native modelfiles with the config. In the very least, we should be able to translate a modelfile into a config entry.
