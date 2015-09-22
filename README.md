## B-Cube Semantics Pipeline

A Solr to triplestore workflow using [Luigi](https://pypi.python.org/pypi/luigi).

Depends on the BCube semantics-preprocessing and OwsCapable modules. 

Currently lets you run a bulk query request against the Solr harvest data (triggered by a fabric task), trigger the luigi pipeline remotely. Ends at generating triples as turtle files right now.

**Running the Solr CLI**

First put together the conf file (JSON):

```
{
	"solr": {
		"query": "q=*%3A*&sort=date+desc&wt=json&indent=true",
		"start": 0,
		"end": 100,
		"offset": 5,
		"output_path": "local-to-ec2/path/docs",
		"connection": "Provider=http; User ID=USER; Password=PASSWORD; Host=localhost; Port=8080; Database=solr; Collection=collection1"
	}
}
```

It will run a default query ("q=*%3A*&wt=json&indent=true") if one isn't provided. Otherwise, include a properly structured Solr query, without limit/offset, as the query term.

The connection string is similar to a standard postgres string where Provider is {http | https}, Database and Collection the Solr database name and collection to query, and Host, Port, User and Password should be self-explanatory. This conf is local to your fabfile.

The CLI will paginate the requests and disaggregate the response into individual `doc` files in the output_path location. THis process is not rolled in to the main luigi pipeline for a couple of reasons - first, the Workflow CLI is also an iterator (see below) for performance reasons on a single machine, second, the Solr pull does not need to be repeated for each run assuming that system is basically write-once (and it requests data at a different chunk size than the idempotent luigi inputs) and third, it's just a bit cleaner given the code flow now. 

To run the CLI locally:

```
python solr_tasks.py -c "Provider=http; User ID=USER; Password=PASSWORD; Host=localhost; Port=8080; Database=solr; Collection=collection1" -q q=*"%3A*&sort=date+desc&wt=json&indent=true" -d local/solr_docs -i 10 -s 0 -e 100
```


**Running the Workflow CLI**

The Workflow CLI provides a single, simple interface to the supported processing workflows. Single workflows can be executed without the CLI according to the standard luigi methods. The workflows and tasks have a normalized structure to handle simple parameter transfers between tasks while still allowing for more complex requirements per task. (I haven't calculated the performance hit for parsing this parse-at-init structure)

Supported Parameters

- workflow (`-w`): the class name of the workflow to run. 
- config (`-c`): the file path to the YAML configuration file.
- directory (`-d`): the file path to the directory containing the input files
- start (`-s`): the integer start index
- end (`-e`): the integer end index
- interval (`-i`): the integer interval for iteration


Configuration Structure

Each task to run contains its own configuration block, keyed by the task name (no 'Task'). Each task contains an `output_directory` key with the path for that set of output and *may* have a params dictionary containing task-specific values. 


Examples

```
Clean:
	output_directory: path/to/cleaned/outputs

Identify:
	output_directory: path/to/identify/outputs
	params:
	    identifiers:
			- my_identifiers.yaml

Parse:
	output_directory: path/to/parse/outputs
	params:
		parse_as_xml: False

```


**Running either remotely with fabric**

If running remotely, add a server section to your conf file:

```
{
	"server": {
		"user": "{EC2 local user}",
		"key_path": "{path to your PEM file}",
		"host": "{AWS EC2 public DNS}"
	}
}
```

You can test your configuration by running the `set_server` task:

```
>> fabfile set_server:path/to/settings.conf
```

The fabfile also provides a task to clear a set of remote directories for new pipeline runs (luigi is idempotent). Use the `clear_pipeline` task with a comma-delimited list of paths. 






