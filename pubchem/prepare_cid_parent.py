import base64
import hashlib
import logging

out = open("/filestore/pubchem/cid-parent-prepared.txt", "w")

ins = [
    '/filestore/pubchem/CID-Parent',
]

for infile in ins:
    with open(infile) as f:
        i = 0
        print("---- reading file %s ----" % f)
        for line in f:
            i += 1
            #print(line)
            splitted = line.strip('\n').split("\t")
            if len(splitted) == 1:
                cid = splitted[0]
                cid_parent = splitted[0]
            elif len(splitted) == 2:
                cid = splitted[0]
                cid_parent = splitted[1]
            else:
                print("ERROR")
                break

            out.write("%s\t%s\n" % (cid, cid_parent))

            if not i % 1000:
                print(i)
            # if i >= 100:
            #     break

out.close()