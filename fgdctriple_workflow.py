import luigi
import glob
import os
from optparse import OptionParser
import json
from tasks.task_helpers import parse_yaml, extract_task_config
from tasks.task_helpers import generate_output_filename
from tasks.task_helpers import run_init
from semproc.process_router import Router
from semproc.serializers.rdfgraphs import RdfGrapher


class FgdcTripleWorkflow(luigi.Task):
    doc_dir = luigi.Parameter()
    yaml_file = luigi.Parameter()

    start_index = luigi.Parameter(default=0)
    end_index = luigi.Parameter(default=1000)

    def requires(self):
        return [
            FgdcTripleTask(
                input_file=f,
                yaml_file=self.yaml_file
            ) for f in self._iterator()
        ]

    def output(self):
        return luigi.LocalTarget('log.txt')

    def run(self):
        self._configure()
        print 'running'

    def _configure(self):
        config = parse_yaml(self.yaml_file)
        run_init(config)

    def _iterator(self):
        for f in glob.glob(
                os.path.join(self.doc_dir, '*.json')
        )[self.start_index:self.end_index]:
            yield f


class FgdcParseTask(luigi.Task):
    yaml_file = luigi.Parameter()
    input_file = luigi.Parameter()

    output_path = ''
    params = {}

    def requires(self):
        # we have no previous task (just run from some
        # set of identified task output)
        return []

    def output(self):
        return luigi.LocalTarget(
            generate_output_filename(
                self.input_file,
                self.output_path,
                'parsed'
            )
        )

    def run(self):
        '''  '''
        self._configure()

        f = self.input().open('r')
        data = json.loads(f.read())
        parsed = self.process_response(data)
        if parsed:
            with self.output().open('w') as out_file:
                out_file.write(json.dumps(parsed, indent=4))

    def _configure(self):
        config = parse_yaml(self.yaml_file)
        config = extract_task_config(config, 'Parse')
        self.output_path = config.get('output_directory', '')
        self.params = config.get('params', {})

    def process_response(self, data):
        content = data['content'].encode('unicode_escape')
        url = data['url']
        identity = data['identity']

        harvest_details = {
            "harvest_date": data['tstamp']
        }

        # TODO: update this for the identity as list
        processor = Router(
            identity,
            content,
            url,
            harvest_details,
            **{"parse_as_xml": self.params.get('parse_as_xml', True)}
        )
        if not processor:
            return {}

        processor.reader.parse()
        description = processor.reader.description

        # drop the source for a decent non-xml embedded in my json file
        del data['content']

        data["service_description"] = description
        return data


class FgdcTripleTask(luigi.Task):
    yaml_file = luigi.Parameter()
    input_file = luigi.Parameter()

    output_path = ''
    params = {}

    def requires(self):
        return FgdcParseTask(
            input_file=self.input_file, yaml_file=self.yaml_file)

    def output(self):
        return luigi.LocalTarget(
            generate_output_filename(
                self.input_file,
                self.output_path,
                'triples',
                '.ttl'
            )
        )

    def run(self):
        '''  '''
        self._configure()

        f = self.input().open('r')
        data = json.loads(f.read())
        triples = self.process_response(data)

        if triples:
            with self.output().open('w') as out_file:
                out_file.write(triples)

    def _configure(self):
        config = parse_yaml(self.yaml_file)
        config = extract_task_config(config, 'Triple')
        self.output_path = config.get('output_directory', '')
        self.params = config.get('params', {})

    def process_response(self, data):
        graph = RdfGrapher(data)
        graph.serialize()
        return graph.emit_format()


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('--interval', '-i', default=1000)
    op.add_option('--directory', '-d')
    op.add_option('--config', '-c')
    op.add_option('--start', '-s')
    op.add_option('--end', '-e')
    options, arguments = op.parse_args()

    if not options.config:
        op.error('No configuration YAML')
    if not options.directory:
        op.error('No input file directory')

    files = glob.glob(os.path.join(options.directory, '*.json'))
    if not files:
        op.error('Empty input file directory (no JSON)')

    try:
        interval = int(options.interval)
    except:
        op.error('Non-integer interval value')

    start_index = int(arguments.start) if 'start' in arguments else 0
    end_index = int(arguments.end) if 'end' in arguments else len(files)

    for i in xrange(start_index, end_index, interval):
        w = FgdcTripleWorkflow(
            doc_dir=options.directory,
            yaml_file=options.config,
            start_index=i,
            end_index=(i + interval)
        )
        luigi.build([w], local_scheduler=True)
