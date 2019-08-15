# entityfactspicturesharvester - EntityFacts pictures harvester

entityfactspicturesharvester is a commandline command (Python3 program) that reads depiction information (images URLs) from given [EntityFacts](https://www.dnb.de/EN/Professionell/Metadatendienste/Datenbezug/Entity-Facts/entity-facts_node.html) sheets* (as line-delimited JSON records) and retrieves and stores the pictures and thumbnails contained in this information

*) EntityFacts are "fact sheets" on entities of the Integrated Authority File ([GND](https://www.dnb.de/EN/Professionell/Standardisierung/GND/gnd_node.html)), which is provided by German National Library ([DNB](https://www.dnb.de/EN/Home/home_node.html))

## Usage

It eats EntityFacts sheets as line-delimited JSON records from *stdin*.

It retrieves and stores the pictures (/thumbnails) linked in the depiction information of the EntityFacts sheets one by one as file into the give directory.

```
entityfactspicturesharvester

optional arguments:
  -h, --help                           show this help message and exit
```

* example:
    ```
    example: entityfactspicturesharvester < [INPUT LINE-DELIMITED JSON FILE WITH ENTITYFACTS SHEETS]
    ```

### Note

If you run into '429' responses ("too many requests", see, e.g., [HTTP status code 429 at httpstatuses.com](https://httpstatuses.com/429)), then you may try to reduce the number of threads of the thread pool schedulers (line 31 and 32) and/or enable (+ (optionally) setup) the time delays before emitting the picture/thumbnail URLs (line 68 and 146) and/or before doing a request (line 157).

## Run

* clone this git repo or just download the [entityfactspicturesharvester.py](entityfactspicturesharvester/entityfactspicturesharvester.py) file
* run ./entityfactspicturesharvester.py
* for a hackish way to use entityfactspicturesharvester system-wide, copy to /usr/local/bin

### Install system-wide via pip

```
sudo -H pip3 install --upgrade [ABSOLUTE PATH TO YOUR LOCAL GIT REPOSITORY OF ENTITYFACTSPICTURESHARVESTER]
```
(which provides you ```entityfactssheetsharvester``` as a system-wide commandline command)
