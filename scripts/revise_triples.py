import glob
import os

# a couple of typos in the generated triples
# not worth regenerating through the pipeline
# a soa local find & replace

files = glob.glob('../pipeline_tests/triples/*.ttl')

output_dir = '../pipeline_tests/revised_triples'

for f in files:
    with open(f, 'r') as g:
        txt = g.read()

    txt = txt.replace(
        'bcube:reasonPhrase', 'http:reasonPhrase').replace(
        'vcard:hasUrl', 'vcard:hasURL')

    # inject the namespace
    txt = '@prefix http: <http://www.w3.org/2011/http#> .\n' + txt
    fname = f.split('/')[-1]
    with open(os.path.join(output_dir, fname), 'w') as g:
        g.write(txt)
