import hashlib
import logging

out = open("/filestore/pubchem/sid-map-cleaned.txt", "w")

# ins = [
#     '/instore/pubchem/extras/compound/CID-IUPAC.100000',
#     '/instore/pubchem/extras/compound/CID-Synonym-filtered'
# ]

ins = [
    '/instore/pubchem/SID-Map',
#    '/instore/pubchem/extras/compound/CID-Synonym-filtered'
]

for infile in ins:
    with open(infile) as f:
        i = 0
        print("---- reading file %s ----" % f)
        for line in f:
            i += 1
            #print(line)
            splitted = line.strip('\n').split("\t")
            if len(splitted) == 4:
                sid, source, regid, cid = splitted
            else:
                continue
                #sid, source, regid = splitted
                #cid = None
            #print("%s : %s : %s : %s" % (sid, source, regid, cid))

            # name = "".join(splitted[1:])
            # cid = splitted[0]

            #name = name.replace("\\", "")
            #hash = hashlib.md5(str(name).encode('UTF-8')).hexdigest()

            out.write("%s\t%s\t%s\t%s\n" % (sid, source, regid, cid))

            if not i % 100000:
                print(i)
            # if i >= 1000:
            #     break

out.close()