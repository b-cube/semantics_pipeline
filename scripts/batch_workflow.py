import subprocess

'''
this is like the saddest luigi workaround to date.
'''

for i in xrange(0, 865000, 50000):
    cmd = 'python workflow_manager.py -w IdentifyWorkflow -d pipeline_tests/docs -s {0} -e {1} -i 50000 -c pipeline_tests/run_through_triples.yaml'.format(i, i+50000)

    s = subprocess.call(cmd, shell=True)

    print '************COMPLETED %s' % i
