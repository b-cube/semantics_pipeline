import json
import os
import requests


class SolrBulkPullJob():
    '''
    not a proper task, just a way to pull, from a
    prebuilt query, some chunk of docs from solr
    that will then be sent to the initializing
    iterator instead of a glob. a remote glob.
    '''
    output_path = ''

    def __init__(self, solr_query):
        # this is gross and i don't like it
        # but there's not a lot of time for
        # dicking around
        self.solr_host = os.environ.get('HARVEST_SOLR_HOST')
        self.solr_port = os.environ.get('HARVEST_SOLR_PORT')
        solr_auth = os.environ.get('HARVEST_SOLR_AUTH')
        self.solr_auth = tuple(solr_auth.split(','))
        self.solr_query = solr_query

    def _generate_url(self):
        host = 'http://' + self.solr_host
        if self.solr_port:
            host += ':' + self.solr_port
        return '/'.join([
            host, 'solr', 'collection1', 'query', self.solr_query])

    def _query(self):
        req = requests.get(self._generate_url(), auth=self.solr_auth)

        if req.status_code != 200:
            raise Exception('Solr failed %s' % req.status_code)

        return req.json()

    def _parse_contents(self, contents):
        # run through the docs array
        output_pattern = os.path.join(self.output_path, '%s.json')

        responses = contents.get('responses', [])
        for doc in responses.get('reponse', {}).get('docs', []):
            response_sha = ''
            with open(output_pattern % response_sha, 'w') as f:
                f.write(json.dumps(doc, indent=4))

    def run(self):
        contents = self._query()
        self._parse_contents(contents)
