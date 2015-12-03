import glob
import os

# a couple of typos in the generated triples
# not worth regenerating through the pipeline
# a soa local find & replace

files = glob.glob('triples/*.ttl')

output_dir = 'revised_triples'

for f in files:
    with open(f, 'r') as g:
        txt = g.read()

    txt.replace(
        'bcube:reasonPhrase', 'http:reasonPhrase').replace(
        'vcard:hasUrl', 'vcard:hasURL')
    fname = f.split('/')[-1]
    with open(os.path.join(output_dir, fname), 'w') as g:
        g.write(txt)
