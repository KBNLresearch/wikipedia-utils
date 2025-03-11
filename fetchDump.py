import argparse
import json
import sys
import shutil
import hashlib
import urllib.request

"""
Parse Wikipedia dump status file, and download dump
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


def errorExit(msg):
    """Print error to stderr and exit."""
    msgString = "ERROR: " + msg + "\n"
    sys.stderr.write(msgString)
    sys.exit(1)


def generateChecksum(fileIn, algorithm):
    """Generate file checksum with user-define algorithm"""

    # fileIn is read in chunks to ensure it will work with (very) large files as well
    # Adapted from: http://stackoverflow.com/a/1131255/1209004

    blocksize = 2**20
    m = hashlib.new(algorithm)
    with open(fileIn, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def processFile(fileUrl, fileName, fileHash):
    """Download one file, and verify hash """

    hashMatch = False

    # Download the file
    with urllib.request.urlopen(fileUrl) as response, open(fileName, 'wb') as fOut:
        shutil.copyfileobj(response, fOut)

    # Verify hash
    computedHash = generateChecksum(fileName, 'sha1')
    if computedHash == fileHash:
        hashMatch = True

    return computedHash, hashMatch

def processDump(dump):

    # Prefix for dump URLs
    urlPrefix = 'https://dumps.wikimedia.org'

    status = dump['status']
    if status == "done":
        files = dump['files']
        for file in files.items():
            fileName = file[0]
            fileAttribs = file[1]
            fileSize = int(fileAttribs['size'])
            fileUrl = fileAttribs['url']
            fileUrl = urlPrefix + fileUrl
            fileMd5 = fileAttribs['md5']
            fileSha1 = fileAttribs['sha1']

            # Process one file
            computedHash, hashMatch = processFile(fileUrl, fileName, fileSha1)
            print(fileName, computedHash, str(hashMatch))

    else:
        msg = "incomplete dump"
        errorExit(msg)
    info = {}
    return info


def main():

    # Get input from command line
    args = parseCommandLine()
    dumpFile =  args.statusFile

    # Read JSON dump file
    with open(dumpFile) as fd:
        data = json.load(fd)

    jobs = data['jobs']

    # Bz2 dump
    #bz2Dump = jobs['metahistorybz2dump']
    #bz2DumpInfo = processDump(bz2Dump)

    # 7z dump
    szDump = jobs['metahistory7zdump']
    szDumpInfo = processDump(szDump)

    #print("total bz2 dump size: {} GB, {} GiB".format(round(bz2DumpInfo['sizeGB'], 2), round(bz2DumpInfo['sizeGiB'], 2)))
    #print("total 7z dump size: {} GB, {} GiB".format(round(szDumpInfo['sizeGB'], 2), round(szDumpInfo['sizeGiB'], 2)))


if __name__ == "__main__":
    main()
