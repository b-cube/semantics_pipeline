from fabric.api import env, run, cd, sudo
from fabric.api import task
import json


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
    _pull_git('semantics_preprocessing', branch)


def _update_owscapable(branch=''):
    _pull_git('OwsCapable', branch)


def _build_preprocessing():
    _build_local('semantics_preprocessing')


def _build_owscapable():
    _build_local('OwsCapable')


def _clear_outputs(empties):
    # list of directory paths (pipes/cleaned/*)
    with cd("/home/%s/semantics_pipeline" % USER):
        for empty in empties.split(','):
            run('rm -rf %s' % empty)


def _run_pipeline(workflow, local_config, local_directory, start, end, interval):
    with cd(_build_cwd('semantics_pipeline')):
        run('python workflow_manager.py -w {0} -d {1} -c {2} -s {3} -e {4} -i {5}').format(
            workflow, local_directory, local_config, start, end, interval)


@task
def set_server(conf):
    config = json.loads(conf)
    env.user = config.get('server', {}).get('user')
    env.hosts = [config.get('server', {}).get('host')]
    env.key_filename = [config.get('server', {}).get('key_path')]


@task
def deploy_pipeline(clean_directories=""):
    _update_pipeline()
    if clean_directories:
        _clear_outputs(clean_directories)


@task
def deploy_processing(branch=""):
    _update_preprocessing(branch)
    _build_preprocessing()


@task
def deploy_owscapable(branch=""):
    _update_owscapable(branch)
    _build_owscapable()


@task
def run_remote_pipeline(workflow, local_config, local_directory, start, end, interval):
    _run_pipeline(workflow, local_config, local_directory, start, end, interval)


@task
def query_solr(conf):
    config = json.loads(conf)
    solr = config.get('solr', {})
    with cd(_build_cwd('semantics_pipeline')):
        run('python local/solr_tasks.py -c {0} -q {1} -d {2} -i {3} -s {4} -e {5}'.format(
            solr.get('connection'),
            solr.get('query'),
            solr.get('directory'),
            solr.get('interval'),
            solr.get('start'),
            solr.get('end')
        ))
