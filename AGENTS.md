# AGENTS

## PLAN AND ASK BEFORE DO
CRITICAL: NEVER EVER DO ANY ACTION READING, MODIFYING OR RUNNING without explaining the plan
Each set of intended actions needs to be explained in the format:
I understood that <YOUR ANALYSIS> so that i plan to <GOALS YOU PURSUE> by <ACTIONS TO BE CONFIRMED> estimating <# of ITEMS> <ITEMS> to be worked on. confirm with go!
YOU WILL NEVER PROCEED WITHOUT POSITIVE CONFIRMATION by go!

## Efficiency
* Do NOT do unneeded file lookups based on guessing or assuming typos.
* Do NOT use TodoWrite for tasks with fewer than 4 steps.
* Do NOT read files you already have contents for.
* Keep summaries to 2-3 lines max unless asked for detail.
* Minimize tool calls. Batch parallel calls. Avoid redundant calls.

## SECURITY
CRITICAL: NEVER leak credentials, passwords, hashes, internal hostnames, IPs, or any infrastructure details to public platforms (GitHub, Discourse, etc.). Firing offense.

## Project: ProceedingsTitleParser
Shallow semantic parser extracting metadata from scientific proceedings titles; deprecated since 2023 in favour of pysotsog, kept running as a service.
- Python: >=3.9
- License: Apache-2.0
- Source: https://github.com/WolfgangFahl/ProceedingsTitleParser
- Wiki: http://wiki.bitplan.com/index.php/ProceedingsTitleParser
- Demo: https://ptp.bitplan.com

## Structure
```
ptp/                 # the package
  __init__.py        # version string
  webserver.py       # Flask app (port 5004): / , /settings, /parse
  titleparser.py     # TitleParser, ProceedingsTitleParser, Title, Dictionary, TokenStatistics
  lookup.py          # Lookup - combines the event sources
  event.py           # Event, EventManager
  location.py        # City/Province/CountryManager
  signature.py       # token categories (regexp, parsing, enum, ordinal)
  relevance.py       # Tokenizer, TokenSequence, Token, Category
  ontology.py        # Ontology, Schema, Property
  ceurws.py confref.py crossref.py dblp.py gnd.py openresearch.py wikicfp.py wikidata.py  # event sources
dictionary.yaml      # parser dictionary
examples.yaml        # example titles
queries.yaml         # SPARQL/SQL queries
templates/           # Flask templates
tests/               # unittest test suite
scripts/             # install, test, doc, release, blackisort, getsamples, run
```
Data outside git: cache/, sampledata/ (scripts/getsamples), storage/.

## Running
```bash
scripts/install     # venv, pip install ., spacy model, geograpy nltk data
scripts/getsamples  # fetch sample data
scripts/run         # client mode
scripts/run -s      # server only, log in /var/log/ptp
```

## Testing
```bash
scripts/test        # unittest discover
scripts/test -g     # green
```

## Build & Format
```bash
scripts/blackisort  # black + isort on ptp and tests
scripts/doc         # mkdocs API documentation (-d deploys)
scripts/release     # docs deploy, release commit and push
hatch build
```
