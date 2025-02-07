---

# Setting up dev environment

---

### First time

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

Postgres setup:
* Create a file to hold environment variables:

File called .env inside the offle-assistant/docker/postgres folder. Make sure to fill in username/password 

```
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=offle-assistant-db
    POSTGRES_PORT=5432
```

* Start the container

```
    $ cd offle-assistant/docker/postgres/
    $ sudo docker-compose up -d
```

* To verify postgres is working, you can open up a sql shell with the following:
```
    $ docker-compose exec db psql -U myprojectuser -d offle-assistant

```

* If you want to stop the container:

```
    $ cd offle-assistant/docker/postgres/
    $ sudo docker-compose down
```

* Then, add the following to your .bashrc or .zshrc making sure to fill in a username/password:

```
export POSTGRES_USER=
export POSTGRES_PASSWORD=
export POSTGRES_DB=offle-assistant-db
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

```

* And source the newly edited .bashrc or .zshrc file

```
    $ source ~/.zshrc
```

* Now, apply all the migrations with:
```
    poetry run alembic upgrade head
```

* In the future, if you make database configuration change or container change,
you can test that you are still properly connecting with:
```
    $ poetry run alembic current
```

### Every time

* Start qdrant server
```
    $ cd offle-assistant/qdrant/
    $ sudo docker-compose up -d
```

* Start Redis Server
```
    $ redis-server

```

Start offle-assistant
```
    $ poetry run offle_assistant

```
    
---

    
