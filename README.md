## B-Cube Semantics Pipeline

A Solr to triplestore workflow using [Luigi](https://pypi.python.org/pypi/luigi).

Depends on the BCube semantics-preprocessing and OwsCapable modules. 

Currently lets you run a bulk query request against the Solr harvest data (triggered by a fabric task), trigger the luigi pipeline remotely. Ends at generating triples as turtle files right now.

