from fabric.api import env, cd
from fabric.api import local as lrun
from fabric.api import task
import json
from fabric.colors import blue, red


# local processing just to get something done
# tonight and on a very sharp turnaround for
# the government shutdown, thanks, GOP!
# an example config
# {
#     "solr": {
#         "query": "q=*%3A*&sort=date+desc&wt=json&indent=true",
#         "start": 0,
#         "stop": 60000,
#         "interval": 10000,
#         "directory": "~/Documents/solr_responses/",
#         "connection": "Provider=http; User ID=USER; Password=PASSWORD; Host=localhost; Port=8080; Database=solr; Collection=collection1"
#     }
# }


env.hosts = ['localhost']


def _clear_outputs(base_path, empties):
    # list of directory paths (pipes/cleaned/*)
    with cd(base_path):
        for empty in empties.split(';'):
            lrun('rm -rf %s' % empty)


def _run_pipeline(base_path, workflow, local_config, local_directory, start, end, interval):
    with cd(base_path):
        lrun('python workflow_manager.py -w {0} -d {1} -c {2} -s {3} -e {4} -i {5}'.format(
            workflow, local_directory, local_config, start, end, interval))


def _query_solr(base_path, connection, query, directory, start, end, interval):
    with cd(base_path):
        lrun('python local/solr_tasks.py -c {0} -q {1} -d {2} -i {3} -s {4} -e {5}'.format(
            connection,
            query,
            directory,
            interval,
            start,
            end
        ))


@task
def clear_pipeline(clean_directories=""):
    if not clean_directories:
        print(red('Directory list empty. No deletes.'))
        return

    _clear_outputs(clean_directories)


@task
def run_local_pipeline(base_path, conf):
    with open(conf, 'r') as f:
        config = json.loads(f.read())
    workflow = config.get('workflow', {})
    _run_pipeline(
        base_path,
        workflow.get('workflow'),
        workflow.get('local_config'),
        workflow.get('local_directory'),
        workflow.get('start'),
        workflow.get('end'),
        workflow.get('interval')
    )


@task
def return_pipeline_counts(base_path, directories):
    counts = []
    with cd(base_path):
        for d in directories.split(';'):
            counts.append((d, lrun('ls -l {0} | wc -l'.format(d))))
    for d, c in counts:
        print(blue('{0} contains {1} files'.format(d, c)))


@task
def query_solr(base_path, conf):
    with open(conf, 'r') as f:
        config = json.loads(f.read())
    solr = config.get('solr', {})
    _query_solr(
        base_path,
        '"{0}"'.format(solr.get('connection', '')),
        '"{0}"'.format(solr.get('query', '')),
        solr.get('directory'),
        solr.get('start'),
        solr.get('stop'),
        solr.get('interval')
    )
