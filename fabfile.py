from fabric.api import env, run, cd, sudo
from fabric.api import task
import json
from fabric.colors import green, blue, red


def _pull_git(cwd, branch=""):
    with cd(_build_cwd(cwd)):
        run('git pull origin {0}'.format(branch))


def _build_local(cwd):
    with cd(_build_cwd(cwd)):
        sudo('python setup.py install')


def _build_cwd(subdir):
    return '/home/{0}/{1}'.format(env.user, subdir)


def _update_pipeline(branch=""):
    _pull_git('semantics_pipeline', branch)


def _update_preprocessing(branch=''):
    _pull_git('semantics-preprocessing', branch)


def _update_owscapable(branch=''):
    _pull_git('OwsCapable', branch)


def _build_preprocessing():
    _build_local('semantics-preprocessing')


def _build_owscapable():
    _build_local('OwsCapable')


def _clear_outputs(empties):
    # list of directory paths (pipes/cleaned/*)
    with cd(_build_cwd('semantics_pipeline')):
        for empty in empties.split(';'):
            run('rm -rf %s' % empty)


def _run_pipeline(workflow, local_config, local_directory, start, end, interval):
    with cd(_build_cwd('semantics_pipeline')):
        run('python workflow_manager.py -w {0} -d {1} -c {2} -s {3} -e {4} -i {5}'.format(
            workflow, local_directory, local_config, start, end, interval))


def _query_solr(connection, query, directory, start, end, interval):
    print(red(directory))
    with cd(_build_cwd('semantics_pipeline')):
        run('python local/solr_tasks.py -c {0} -q {1} -d {2} -i {3} -s {4} -e {5}'.format(
            connection,
            query,
            directory,
            interval,
            start,
            end
        ))


@task
def set_server(conf):
    with open(conf, 'r') as f:
        config = json.loads(f.read())
    env.user = config.get('server', {}).get('user')
    env.hosts = [config.get('server', {}).get('host')]
    env.key_filename = [config.get('server', {}).get('key_path')]


@task
def clear_pipeline(clean_directories=""):
    if not clean_directories:
        print(red('Directory list empty. No deletes.'))
        return

    _clear_outputs(clean_directories)


@task
def deploy_pipeline(branch=""):
    _update_pipeline(branch)
    print(green('semantics_pipeline deploy complete!'))


@task
def deploy_processing(branch=""):
    _update_preprocessing(branch)
    _build_preprocessing()
    print(green('semantics-preprocessing deploy complete!'))


@task
def deploy_owscapable(branch=""):
    _update_owscapable(branch)
    _build_owscapable()
    print(green('OwsCapable deploy complete!'))


@task
def run_remote_pipeline(conf):
    with open(conf, 'r') as f:
        config = json.loads(f.read())
    workflow = config.get('workflow', {})
    _run_pipeline(
        workflow.get('workflow'),
        workflow.get('local_config'),
        workflow.get('local_directory'),
        workflow.get('start'),
        workflow.get('end'),
        workflow.get('interval')
    )


@task
def return_pipeline_counts(directories):
    counts = []
    with cd(_build_cwd('semantics_pipeline')):
        for d in directories.split(';'):
            counts.append((d, run('ls -l {0} | wc -l'.format(d))))
    for d, c in counts:
        print(blue('{0} contains {1} files'.format(d, c)))


@task
def query_solr(conf):
    with open(conf, 'r') as f:
        config = json.loads(f.read())
    solr = config.get('solr', {})
    _query_solr(
        '"{0}"'.format(solr.get('connection', '')),
        '"{0}"'.format(solr.get('query', '')),
        solr.get('directory'),
        solr.get('start'),
        solr.get('stop'),
        solr.get('interval')
    )
