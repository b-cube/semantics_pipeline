import glob
import os

# a couple of typos in the generated triples
# not worth regenerating through the pipeline
# a soa local find & replace

# files = glob.glob('../pipeline_tests/triples/*.ttl')

# output_dir = '../pipeline_tests/revised_triples'

# for f in files:
#     with open(f, 'r') as g:
#         txt = g.read()

#     txt = txt.replace(
#         'bcube:reasonPhrase', 'http:reasonPhrase').replace(
#         'vcard:hasUrl', 'vcard:hasURL')

#     # inject the namespace
#     txt = '@prefix http: <http://www.w3.org/2011/http#> .\n' + txt
#     fname = f.split('/')[-1]
#     with open(os.path.join(output_dir, fname), 'w') as g:
#         g.write(txt)


files = glob.glob('../pipeline_tests/triples/*.ttl')

output_dir = '../pipeline_tests/revised_triples'
final_dir = '../pipeline_tests/final_triples'

# no unique constraints so if it was in the first batch,
# skip it
for f in files:
    fname = f.split('/')[-1]
    if os.path.exists(os.path.join(output_dir, fname)):
        continue

    with open(f, 'r') as g:
        txt = g.read()

    txt = txt.replace(
        'bcube:reasonPhrase', 'http:reasonPhrase').replace(
        'vcard:hasUrl', 'vcard:hasURL')

    # inject the namespace
    txt = '@prefix http: <http://www.w3.org/2011/http#> .\n' + txt
    with open(os.path.join(final_dir, fname), 'w') as g:
        g.write(txt)
