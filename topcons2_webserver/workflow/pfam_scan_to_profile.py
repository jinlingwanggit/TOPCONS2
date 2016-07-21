import sys
import os
import linecache
from random import randrange
import myfunc
import subprocess
from datetime import datetime

# modified by Nanjiang 2015-02-06
rundir = os.path.dirname(os.path.realpath(__file__))

# pfam_Dir = "../../pfam"
# pfamseqdb = "../database/pfamfull/uniref100.pfam27.pfamseq.nr90"
pfam_Dir = "%s/../database/pfam/"%(rundir)
pfamseqdb = "%s/../database/pfamfull/uniref100.pfam27.pfamseq.nr90"%(rundir)
path_pfamscan = "%s/../database/pfam_seq/PfamScan/"%(rundir)
pfamscan_scriptfile = "%s/pfam_scan.pl"%(path_pfamscan)
try:
    perl5lib = os.environ['PERL5LIB']
    os.environ['PERL5LIB'] = perl5lib + ":" + path_pfamscan
except KeyError:
    os.environ['PERL5LIB'] = path_pfamscan

# sys.path.append("/usr/local/bin") #added by Nanjiang

def createHitDB(pfamList, prot_name, work_dir):
    hdl = myfunc.MyDB(pfamseqdb)
    if hdl.failure:
        print "Error"
        return 1
    with open(work_dir + prot_name + ".hits.db.temp", "w") as outFile:
        for pfamid in pfamList:
            record = hdl.GetRecord(pfamid)
            if record:
                outFile.write(record)
        hdl.close()

    os.system("python my_uniqueseq.py " + work_dir + prot_name + ".hits.db.temp")

rundir = os.path.dirname(os.path.realpath(__file__))

def main(argvs):
    try:
        input_file = os.path.realpath(argvs[1])
        work_dir = os.path.realpath(argvs[2]) + "/"
    except IndexError:
        print >> sys.stderr, "Syntax error"
        return 1

    name_temp = (input_file[input_file.rfind("/")+1:])
    name = name_temp[:name_temp.rfind(".")]
    startDir = os.getcwd()
#     os.chdir(os.path.abspath("../database/pfam_seq/PfamScan/"))
#     os.chdir(path_pfamscan)
#     sCmd = "perl " + "pfam_scan.pl" + " -fasta " + input_file + " -dir " + pfam_Dir + " -outfile " + work_dir + name + ".txt"
    outfile = "%s/%s.txt" %(work_dir, name)
    sCmd = [pfamscan_scriptfile , "-fasta" , input_file , "-dir" , pfam_Dir , "-outfile", outfile]
    cmdline = " ".join(sCmd)
    print "cmdline=", cmdline
    rmsg = ""
    try:
        #rmsg = myfunc.check_call(sCmd, stderr=subprocess.STDOUT)
        rmsg = subprocess.check_call(sCmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print e
        print rmsg

#     os.system(sCmd)
#     os.chdir(startDir)

    pfamList = []
    pattern = "# <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>"
    bFoundStart = False
#     with open(work_dir + name + ".txt") as inFile:
    with open(outfile) as inFile:
        for line in inFile:
            if line.find(pattern) != -1:
                bFoundStart = True
            if bFoundStart is True:
                pos = line.find("PF")
                if pos != -1:
                    pfamList.append(line[pos:pos+7])

    createHitDB(list(set(pfamList)), name, work_dir)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
