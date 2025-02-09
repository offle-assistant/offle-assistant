---

# Setting up dev environment

---

### Initial setup

---

* Make sure that you have poetry installed.
Check if it's installed with:
```

    $ which poetry

```
If this doesn't display the path to your poetry binary, gotta install it. This is the only package
that I'd say is okay to install via a pip install --user poetry, but you can also install it with
your distro's package manager, probably preferred that way.

* Then clone the repo
```

    $ git clone 'main-branch'

```

* Install the python environment
```

    $ cd offle-assistant
    $ poetry install

```

#### MongoDB setup:
* Create a file to hold environment variables:

File called .env inside the offle-assistant/docker/mongodb folder. Make sure to fill in username/password 

```
    MONGO_USER=
    MONGO_PASSWORD=
```

* Start the container

```
    $ cd offle-assistant/docker/mongodb/
    $ sudo docker-compose up -d
```

* To verify mongodb is working
```
    $

```

* If you want to stop the container:

```
    $ cd offle-assistant/docker/mongodb/
    $ sudo docker-compose down
```

* Then, add the following to your .bashrc or .zshrc making sure to fill in a username/password:

```
export MONGO_USER=
export MONGO_PASSWORD=

```

* And source the newly edited .bashrc or .zshrc file

```
    $ source ~/.zshrc
```

---

### Every other time 

---

Every other time that you start developing, you need to make sure all the servers are up and going.

* Start mongodb server
```

    $ cd offle-assistant/docker/mongodb/
    $ sudo docker-compose up -d

```

* Start qdrant server
```

    $ cd offle-assistant/qdrant/
    $ sudo docker-compose up -d

```

* Start Redis Server
```
    
    $ cd offle-assistant/redis/
    $ sudo docker-compose up -d

```

* Start offle-assistant
```

    $ poetry run offle_assistant

```
    
---

---

# Some helpful commands

---

