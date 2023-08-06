[![pipeline status](https://git.connect.dzd-ev.de/dzdtools/pubmedsucker/badges/master/pipeline.svg)](https://git.connect.dzd-ev.de/dzdtools/pubmedsucker/-/commits/master)

# PubMedSucker (PMS)

Load the [MEDLINE/PubMed](https://www.nlm.nih.gov/databases/download/pubmed_medline.html) "bulk download package" into a [Neo4j](https://neo4j.com/) database.

PMS is a software written in Python3 which downloads the [MEDLINE/PubMed](https://www.nlm.nih.gov/databases/download/pubmed_medline.html) [bulk downloadable data]()https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/ from the [US National Library of Medicine](https://www.nlm.nih.gov/), transforms it reasonable and loads a subset of all PubMed articles attributes into a Neo4j graph database.

**License**: MIT

**Maintainer**: Datamgmt Team of the [German Center of Diabetes Research / Deutsches Zentrum für Diabetesforschung e.V.](https://www.dzd-ev.de) 
            | [Tim Bleimehl](mailto:bleimehl@dzd-ev.de)

honourable mentionable external Python modules PMS is using:

* [graphio](https://github.com/kaiserpreusse/graphio/) - A tool to conveniently load sets of data into neo4j
* [py2neo](https://github.com/py2neo-org/py2neo) - A high level python Neo4j driver/framework
* [xmltodict](https://github.com/martinblech/xmltodict) - Convert xml into Python dicts
* [neobulkmp](https://git.connect.dzd-ev.de/dzdpythonmodules/neo-mp-loader) - Load tons of data in an organized manner with multiple processes into Neo4j

----
**Content**

[[_TOC_]]

----


# What can i do with PMS Graph?

Whatever you can imagen :) We could just calculate some statistics on authors, topics or keyword. A more advanced example: you could use the Neo4j [Graph Data Science Library](https://neo4j.com/docs/graph-data-science/current/) for community detection on entities in the graph to find groups of gene names that often form in publications.

At the DZD, we take this graph as base for a biomedical knowledge graph. We connect it with other Datasources and process the data with NLP libraries. This way we later want, for example, create new theses for our scientiest.


# Quickstart

You need to have [git](https://git-scm.com/) and [docker](https://www.docker.com/) installed.


Clone the PMS code repository to your computer

`git clone ssh://git@git.connect.dzd-ev.de:22022/dzdtools/pubmedsucker.git`
`cd pubmedsucker`

Build the image thats will run PMS

`docker-compose build`

Start PMS with Neo4j and Redis

`docker-compose up`

This will load the latest 10 XMLs from the PubMed baseline and will take around 20 Minutes on a decent Laptop.

You can visit http://localhost:7474 to inspect the result in the Neo4j Graphdatabase

# Setup

## Hardware Requirements

Depending on how much of the MEDLINE/PubMed Data you want to load into the graph in which time, the requirements vary widely.

### MAX

For a full import (Articles from 60s-70s till today, [baseline](ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline) + [annual update](ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/)), in reasonable time you need two full blown servers.

Neo4j Server:

* 256GB Ram
* at least 12cores, better more
* 1 x SDDs with ~128GB
* 1 x SDDs with ~512GB

Parser/Importer

* 12GB Ram
* at least 12Cores, better more (should approx. match neo4j server count)
* about 200GB of disk space

The full import should be completed in under 24hours. You can always save up on the requirements, PMS will still run, but this could increase the import duration drastical.

### MIN

A small sample import of 2-3 xml files from [baseline](ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline) should be done in under 10 minutes on your laptop

## DB / Neo4j setup


> **Dislaimer:** 
I am not claiming to be an expert on setting up a perfomant Neo4j instance. 
These are just some things i read/learned/catched/noticed on the way. Some of the facts could be [cargo cult](https://en.wikipedia.org/wiki/Cargo_cult_programming) or just plain wrong. if you have suggestions on how to improve this document, i would be happy :)  contact me or create an issue


You can use a plain Neo4j instance without any plugins.

There are a lot of manuals, on how to install a Neo4j instance, out there.

We recommend using docker to reduce deployment pain :)

### Demosetup via docker

For a small sample import, a tiny Neo4j instance will do it:

```bash
docker run\
    --publish=7474:7474 --publish=7687:7687 \
    -e NEO4J_AUTH=none \
    --name neo4jtests \
    -v $PWD/data:/data \
    neo4j:4.3
```

### Productive(-ish) setup via docker-compose

A basic conf via docker-compose for a large import server instance with docker-compose could look like this:

`docker-compose.yml`

```yaml
version: '3'
services:
  neo4j:
    image: neo4j:4.1
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/mysupersavepassword
      - NEO4J_dbms_memory_pagecache_size=200GB
      - NEO4J_dbms_memory_heap_max__size=30G
      - NEO4J_dbms_memory_heap_initial__size=30G
      - NEO4J_dbms_logs_query_enabled=off
      - NEO4J_dbms_default__listen__address=0.0.0.0
    volumes:
      - ./plugins:/plugins
      - ./data:/data
      - ./conf:/conf
      - ./logs:/logs
```

Start this with

`docker-compose up -d`

Very important is the [dbms.memory.pagecache.size / NEO4J_dbms_memory_pagecache_size](https://neo4j.com/docs/operations-mannual/current/reference/configuration-settings/#config_dbms.memory.pagecache.size) parameter. Max this out as far as you have memory.

Some more information on memory configuration for Neo4j https://neo4j.com/docs/operations-mannual/current/performance/memory-configuration/

To improve perfomance (and therefore import time) even more seperate disks for Neo4j database and transaction logs could be a reasonable way to go.
https://neo4j.com/docs/operations-mannual/current/performance/linux-file-system-tuning/

Some more hints on improving perfomance: https://neo4j.com/docs/operations-mannual/current/performance/

## Install PMS

### Via Docker

Just catch the needed image from the registries:

`docker pull registry-gl.connect.dzd-ev.de:443/dzdtools/pubmedsucker:prod`

`docker pull redis`

### Via Git

**Requirements**

* Python3
* pip
* A running redis DB

**Steps**

* Clone the repo

`git clone ssh://git@git.connect.dzd-ev.de:22022/dzdtools/pubmedsucker.git`

* cd into the repo

`cd pudmedsucker`

* Install the required python modules

`pip3 install -r reqs.txt`

## Start PMS



### Via docker
A small sample example.


First start the redis database in backround

`docker run --network=host --rm --name redis -d redis`

Then start PMS itself

```bash
docker run --rm \
    -v ${PWD}/data:/data \
    -v ${PWD}/log:/log \
    -e CONFIGS_NEO4J="{'host':'$HOSTNAME', 'user':'neo4j', 'password':'mysuperpw'}" \
    -e CONFIGS_PUBMED_SOURCE="https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed21n0001.xml.gz \
    --network=host \
    registry-gl.connect.dzd-ev.de:443/dzdtools/pubmedsucker:stable
```

### Via docker-compose


A larger import (~ last 10 years)

```yaml
version: '3'
services:
  redis:
    image: redis
    container_name: redis
    ports:
      - 6379:6379
    command:
      - redis-server
      - --save ""
      - --appendonly no
  pms_baseline:
    image: registry-gl.connect.dzd-ev.de:443/dzdtools/pubmedsucker:prod
    environment:
      - CONFIGS_NEO4J="{'host':'myNeo4jHost','port':'7687', 'user':'neo4j','password':'supersecret','name':'MyDBInstance'}"
      - CONFIGS_REDIS="{'host':'redis'}"
      - CONFIGS_PUBMED_SOURCE=350
      - CONFIGS_BASE_LINE_MODE=True
    volumes:
      - ./data:/data
      - ./log:/log
      - ./dump:/dump
```
And we need to run a second time `CONFIGS_BASE_LINE_MODE`set to `False`, to import the updates for the running year

```yaml                                                                                          
version: '3'
services:
  redis:
    image: redis
    container_name: redis
    ports:
      - 6379:6379
    command:
      - redis-server
      - --save ""
      - --appendonly no
  pms_updates:
    image: registry-gl.connect.dzd-ev.de:443/dzdtools/pubmedsucker:prod
    environment:
      - CONFIGS_NEO4J="{'host':'myNeo4jHost','port':'7687', 'user':'neo4j','password':'supersecret','name':'MyDBInstance'}"
      - CONFIGS_REDIS="{'host':'redis'}"
      - CONFIGS_BASE_LINE_MODE=False
    volumes:
      - ./data:/data
      - ./log:/log
      - ./dump:/dump
```

## Config parameters

Config for PMS is located in the file `pms/config.py`

All config parameters can be set/overwritten via environement variables, but then the prefix `CONFIGS_`is needed.
E.g. the parameter `PUBMED_SOURCE` set via environment variable must be `CONFIGS_PUBMED_SOURCE`

---

### `PUBMED_SOURCE`

- Parameter to define which xmls from MEDLINE/PubMed should be parsed

default: `"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline-2019-sample/pubmedsample.xml"`

* **None** - Download and process all pubmed xml files from the source ftp 
  * example: `CONFIGS_PUBMED_SOURCE=None`
* **int** - Download and process the most recent n xml files from the pubmed server
  * example: `CONFIGS_PUBMED_SOURCE=5`
* **str of remote file path** - Download and process a single file
  * example: `CONFIGS_PUBMED_SOURCE=https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1009.xml.gz`
* **str of local dir path** - Process all files in directory
  * example: `CONFIGS_PUBMED_SOURCE=/home/files/`
* **str of local file path** - Process a single file
  * example: `CONFIGS_PUBMED_SOURCE=/home/files/pubmed20n1008.xml`
* **list of local files paths** - Process the xml files in the list
  * example: `CONFIGS_PUBMED_SOURCE=["/home/files/pubmed20n1009.xml","/home/files/pubmed20n1008.xml"]`
* **list of remote files** - ftp,http urls to be downloaded and processed 
  * example: `CONFIGS_PUBMED_SOURCE=["https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1009.xml.gz","https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1008.xml.gz"]`

---


### `BASE_LINE_MODE`

- Define if  [baseline](https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/) or [annual update](https://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/) should be processed. When set to `True` the base line will be downloaded, parsed on loaded into Neo4j. When to `False`the annual update XMLs will be downloaded, parsed and loaded into Neo4j

default: `True`


# Datamodel

![datamodel](doc/schema/SchemaOverview.png "Datamodel")


## Changes in datamodel:

0.9.22 -> 1.2.13

* `PublicationType` and `PublicationTypeUI` are not longer attribute of `:PubMedArticle` but standalone Nodes related to `:PubMedArticle` via `PUBMEDARTICLE_HAS_PUBLICATIONTYPE`