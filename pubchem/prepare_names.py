import hashlib
import logging

out = open("/filestore/pubchem/pubchem-names-hashed.txt", "w")

# ins = [
#     '/instore/pubchem/extras/compound/CID-IUPAC.100000',
#     '/instore/pubchem/extras/compound/CID-Synonym-filtered'
# ]

ins = [
    #'/instore/pubchem/CID-IUPAC.100000',
    '/instore/pubchem/CID-Synonym-filtered'
]

for infile in ins:
    with open(infile) as f:
        i = 0
        print("---- reading file %s ----" % f)
        for line in f:
            #print(line)
            i += 1
            splitted = line.split()
            #print(splitted)
            name = " ".join(splitted[1:])
            cid = splitted[0]
            if "InChI" in name:
                continue
            if "UNII" in name:
                continue
            name = name.replace("\\", "")
            hash = hashlib.md5(str(name).encode('UTF-8')).hexdigest()
            out.write("%s\t%s\t%s\n" % (hash, cid, name))
            if not i % 10000:
                print(i)
            # if i >= 2000000:
            #     break

out.close()