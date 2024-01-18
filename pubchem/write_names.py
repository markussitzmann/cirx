import hashlib
import logging

out = open("/home/app/pubchem/pubchem-names-hashed.txt", "w")

ins = [
    '/instore/pubchem/extras/compound/CID-IUPAC',
    '/instore/pubchem/extras/compound/CID-Synonym-filtered'
]

for infile in ins:
    with open(infile) as f:
        i = 0
        logging.info("reading file %s" % f)
        for line in f:
            i += 1
            name = "".join(line.split()[1:])
            if "InChI" in name:
                continue
            if "UNII" in name:
                continue
            name = name.replace("\\", "")
            hash = hashlib.md5(str(name).encode('UTF-8')).hexdigest()
            out.write("%s\t%s\n" % (hash, name))
            if not i % 1000:
                print(i)
            # if i >= 2000:
            #     break

out.close()