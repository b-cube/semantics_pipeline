import os
import yaml
import json
from semproc.yaml_configs import import_yaml_configs
# from tasks.solr_tasks import SolrBulkJob

'''
general task methods

mainly, parse the yaml configuration file
'''


def parse_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        y = yaml.load(f.read())
    return y


def extract_task_config(yaml_config, task):
    return yaml_config.get(task, {})


def run_init(config):
    init_tasks = config.get('init', {})
    if not init_tasks:
        return

    # if 'query_solr' in init_tasks:
    #     # pull data based on the query in the yaml
    #     # that's a little unfortunate since we really
    #     # don't want to pull 200K+ things down but
    #     # again really don't care in favor of run it now
    #     solr_query = init_tasks.get('query_solr').get('query', '')
    #     solr_path = init_tasks.get('query_solr').get('output_path', '')
    #     solr_start = init_tasks.get('query_solr').get('start', '')
    #     solr_end = init_tasks.get('query_solr').get('end', '')
    #     solr_offset = init_tasks.get('query_solr').get('offset', '')
    #     solr = SolrBulkJob(
    #         solr_query, solr_path, solr_start, solr_end, solr_offset)
    #     solr.run()


def read_data(path):
    with open(path, 'r') as f:
        return json.loads(f.read())


def write_data(path, data):
    with open(path, 'w') as f:
        f.write(json.dumps(data, indent=4))


def generate_output_filename(
        input_file, output_path, postfix, extension_overwrite=''):
    file_name, file_ext = os.path.splitext(os.path.basename(input_file))
    file_ext = extension_overwrite if extension_overwrite else file_ext
    return os.path.join(output_path, '_'.join([file_name, postfix]) + file_ext)


def clear_directory(directory):
    for d in os.walk(directory):
        subdir = d[0]
        files = d[2]
        for f in files:
            os.remove(os.path.join(subdir, f))


def load_yamls(yamls):
    return import_yaml_configs(yamls)
