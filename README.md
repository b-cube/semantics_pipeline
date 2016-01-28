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
		"stop": 100,
		"interval": 5,
		"directory": "local-to-ec2/path/docs",
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
- directory (`-d`): the file path to the directory containing the input files.
- start (`-s`): the integer start index.
- end (`-e`): the integer end index.
- interval (`-i`): the integer interval for iteration.
- filetype (`-f`): extension of the input files (default: json).


Configuration Structure

Each task to run contains its own configuration block, keyed by the task name (no 'Task'). Each task contains an `output_directory` key with the path for that set of output and *may* have a params dictionary containing task-specific values. 


Examples

```
Clean:
	output_directory: path/to/cleaned/outputs

Identify:
	output_directory: path/to/identify/outputs
	params:
		# list of identifier yaml configuration files to use
		# anything not found in these files in unknown
	    identifiers:
			- my_identifiers.yaml
		# flag for capturing unknown xml types
		# currently has no triple output structure
		save_unknown: false

Parse:
	output_directory: path/to/parse/outputs
	params:
		# if unknown and saved, should it be parsed?
		parse_as_xml: False
		# list of protocols, as tagged in the configuration files
		# to exclude from the json parsing even if identified
		exclude:
			- RDF
			- OAI-PMH

Triple:
	output_directory: path/to/triples/directory

# also works for SimpleParliament (just post
# using the triples directory for inputs)
Parliament:
	output_directory: path/to/parliament/outputs
	params:
		endpoint: 'https://my.parliament.db/sparql'
		named_graph: 'urn:graph:triples'
		auth: 'user:password'

```

Order doesn't matter (that's defined within the tasks currently). 

To run the CLI, and we'll use the YAML example above as the workflow (in this case, the ParseWorkflow), run:

```
python workflow_manager.py -w ParseWorkflow -c parse.yaml -d data/solr_docs -s 0 -e 1000 -i 100
```

to execute a parse workflow from clean to identify to parse for the set of Solr docs in the solr_docs directory for the first thousand at 100 per iteration. Note for running the Parliament or SimpleParliament tasks (post to the triplestore), you need to set the filetype to `ttl`.

I note also that luigi, as set up here, is not being used as intended, ie, not clustered and not through the server. It is less than ideal. As such, we have this workflow wrapper to iterate over a set of inputs. This batching hack is still prone to memory issues (building that dependency tree is non-trivial); we've found on a medium to large EC2, not high RAM, you can run 100K inputs in 2-4K intervals. 

####The pipeline workflow

The basic pipeline workflow is as follows:

1. Extract the documents using the SOLR CLI described above. Depending on the current state of the index, you may be able to query the system from some date forward. 
2. Write the workflow YAML describing the desired workflow, making sure that the output directories exist and have all required permissions.
3. Execute the pipeline using the workflow_manager CLI, pointing to the output SOLR directory and using the desired workflow name.

(Note: the pipeline codebase includes several tasks and/or workflows not described here. These can safely be ignored and, in some cases, the functionality is found in other processing code. See the Response-Identification-Info repository for more details.)


**Running either remotely with fabric**

You will need to have fabric installed.

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

(We are assuming some AWS EC2 Ubuntu 14.04 instance.)

You can test your configuration by running the `set_server` task:

```
>> fabfile set_server:path/to/settings.conf
```

The fabfile also provides a task to clear a set of remote directories for new pipeline runs (luigi is idempotent). Use the `clear_pipeline` task with a semicolon-delimited list of paths:

```
>> fabfile set_server:path/to/settings.conf clear_pipeline:"path/cleaned;path/identified;path/parsed"
```

Note that the `clear_pipeline` parameter is quoted!

To run a deploy for any of the BCube-related dependencies:

```
>> fabfile set_server:path/to/settings.conf deploy_owscapable 
>> # note this identifies a branch for the build, but can be executed with the master branch from deploy_processing
>> # and the branch option is available for any of the deploy_* methods
>> fabfile set_server:path/to/settings.conf deploy_processing:branch=iso-rdf-serializer
>> fabfile set_server:path/to/settings.conf deploy_pipeline
```

The Solr CLI can also be run remotely:

```
>> fabfile set_server:path/to/settings.conf query_solr:path/to/local.conf
```

and the Workflow CLI:

```
>> fabfile set_server:path/to/settings.conf run_remote_pipeline:ParseWorkflow,pipeline/settings.conf,pipeline/solr_docs,0,1000,100
```

While you can run the workflows through this fabric option, it is not set up to handle screens. For short runs and testing, this is not an issue but for any significant processing, it is less than ideal. 








