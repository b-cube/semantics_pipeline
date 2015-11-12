import glob
import os
from mpp.models import Response

import json as js  # name conflict with sqla
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker

with open('big_rds.conf', 'r') as f:
    conf = js.loads(f.read())

# our connection
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

files = glob.glob('pipeline_tests/docs/*.json')

for f in files:
    fname = f.split('/').replace('.json', '')

    r = session.query(Response).filter(Response.source_url_sha==fname).first()
    if not r:
        continue

    # delete the doc
    os.remove(f)

session.close()
