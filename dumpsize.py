import argparse
import json
import sys
#from urllib.request import urlopen

"""
Parse Wikipedia dump status file, and calculate total size of dumps
with complete page edit history (for both bz2 and 7z formats).

Example status file:

https://dumps.wikimedia.org/nlwiki/20250201/dumpstatus.json
"""

# Create argument parser
parser = argparse.ArgumentParser()


def parseCommandLine():
    """Parse command line"""

    parser.add_argument('statusFile',
                                action="store",
                                help="Input Wikipedia dump status file in JSON format")

    # Parse arguments
    args = parser.parse_args()

    return args


def getDumpInfo(dump):
    status = dump['status']
    updated = dump['updated']
    files = dump['files']
    # Total file size in bytes
    sizeBytes = 0
    for file in files.items():
        fileName = file[0]
        fileAttribs = file[1]
        fileSize = int(fileAttribs['size'])
        # Update total file size
        sizeBytes += fileSize
    # Convert sizeBytes to GB and GiB
    sizeGB = sizeBytes / 10**9
    sizeGiB = sizeBytes / 2**30
    info = {}
    info['status'] = status
    info['updated'] = updated
    info['sizeBytes'] = sizeBytes
    info['sizeGB'] = sizeGB
    info['sizeGiB'] = sizeGiB
    return info


def main():

    # Get input from command line
    args = parseCommandLine()
    dumpFile =  args.statusFile

    #data = urlopen(dumpFile)
    # Read JSON dump file
    with open(dumpFile) as fd:
        data = json.load(fd)

    jobs = data['jobs']

    msRecombineDump = jobs['articlesmultistreamdumprecombine']
    msRecombineDumpInfo = getDumpInfo(msRecombineDump)

    # Bz2 dump
    bz2Dump = jobs['metahistorybz2dump']
    bz2DumpInfo = getDumpInfo(bz2Dump)

    # 7z dump
    szDump = jobs['metahistory7zdump']
    szDumpInfo = getDumpInfo(szDump)

    print("total multistream recombine dump size: {} GB, {} GiB".format(round(msRecombineDumpInfo['sizeGB'], 2), round(msRecombineDumpInfo['sizeGiB'], 2)))
    print("total bz2 dump size: {} GB, {} GiB".format(round(bz2DumpInfo['sizeGB'], 2), round(bz2DumpInfo['sizeGiB'], 2)))
    print("total 7z dump size: {} GB, {} GiB".format(round(szDumpInfo['sizeGB'], 2), round(szDumpInfo['sizeGiB'], 2)))


if __name__ == "__main__":
    main()
