import hashlib

out = open("pubchem-names-hashed.txt", "w")

with open('/home/app/pubchem/CID-Synonym-filtered') as f:
    i = 0
    for line in f:
        i += 1
        name = "".join(line.split()[1:])
        if "InChI" in name:
            continue
        name = name.replace("\\", "")
        hash = hashlib.md5(str(name).encode('UTF-8')).hexdigest()
        out.write("%s\t%s\n" % (hash, name))
        if not i % 1000:
            print(i)
        if i >= 10000000:
           break

out.close()