import glob
import os
import subprocess

import json as js  # name conflict with sqla

files = glob.glob('../pipeline_tests/docs/*.json')

for f in files:
    fname = f.split('/')[-1].replace('.json', '')

    cmd = 'grep %s existing_shas.txt' % fname
    s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = s.communicate()

    if err:
        print f, err
        continue

    if not out:
        continue

    # delete the doc
    os.remove(f)
