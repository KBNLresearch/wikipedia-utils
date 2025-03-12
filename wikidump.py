import argparse
import json
import sys
import shutil
import hashlib
import urllib.request

"""
Parse Wikipedia dump status file, and show information about dump.
Optionally download / fetch dump if fetch flag is used. 

Example status file:

https://dumps.wikimedia.org/nlwiki/20250201/dumpstatus.json
"""

# Create argument parser
parser = argparse.ArgumentParser()


def parseCommandLine():
    """Parse command line"""

    parser.add_argument('statusFile',
                         action="store",
                         help="input Wikipedia JSON dump status file")
    parser.add_argument('--compression', '-c',
                        action='store',
                        dest='compressionType',
                        choices=['bz2', '7z'],
                        default='bz2',
                        help='compression type')
    parser.add_argument('--fetch', '-f',
                        action='store_true',
                        dest='fetchFlag',
                        default=False,
                        help='Download dump')

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


def fetchFile(fileUrl, fileName, fileHash):
    """Download one file, and verify hash """

    hashMatch = False

    print("downloading {}".format(fileName))
    # Download the file
    with urllib.request.urlopen(fileUrl) as response, open(fileName, 'wb') as fOut:
        shutil.copyfileobj(response, fOut)

    # Verify hash
    computedHash = generateChecksum(fileName, 'sha1')
    if computedHash == fileHash:
        hashMatch = True
        print("Sha1 verification OK!")
    else:
        print("Sha1 verification failed!")

    return computedHash, hashMatch


def processDump(dump, fetchFlag):
    """Process one dump"""

    # Initialize cumulative size of all files in this dump 
    sizeBytes = 0
    # Dump info dictionary
    dumpInfo = {}
    # Files info list
    filesInfo = []
    # Initial value of hash match flag
    hashMatchFlag = True
    # Prefix for dump URLs
    urlPrefix = 'https://dumps.wikimedia.org'
    # Dump status
    status = dump['status']
    dumpInfo['dumpStatus'] = status
    if status == "done":
        files = dump['files']
        for file in files.items():
            # File info dictionary
            fileInfo = {}
            # Read file info
            fileName = file[0]
            fileAttribs = file[1]
            fileSize = int(fileAttribs['size'])
            sizeBytes += fileSize
            fileUrl = fileAttribs['url']
            fileUrl = urlPrefix + fileUrl
            fileMd5 = fileAttribs['md5']
            fileSha1 = fileAttribs['sha1']
            # Add file info to dictionary
            fileInfo['fileName'] = fileName
            fileInfo['fileSizeBytes'] = fileSize
            fileInfo['fileUrl'] = fileUrl
            fileInfo['fileMd5'] = fileMd5
            fileInfo['fileSha1'] = fileSha1

            if fetchFlag:
                # Fetch one file
                computedHash, hashMatch = fetchFile(fileUrl, fileName, fileSha1)
                if not hashMatch:
                    hashMatchFlag = False
                #fileInfo['fileSha1Computed'] = computedHash
                fileInfo['sha1Match'] = hashMatch
            
            # Add file info dictionary to filesInfo list
            filesInfo.append(fileInfo)
    else:
        msg = "incomplete dump"
        errorExit(msg)

    # Convert sizeBytes to GB and GiB
    sizeGB = sizeBytes / 10**9
    sizeGiB = sizeBytes / 2**30
    dumpInfo['dumpSizeBytes'] = sizeBytes
    dumpInfo['dumpSizeGB'] = round(sizeGB, 2)
    dumpInfo['dumpSizeGiB'] = round(sizeGiB, 2)
    dumpInfo['files'] = filesInfo
    if fetchFlag:
        dumpInfo['hashMatchFlag'] = hashMatchFlag

    return dumpInfo


def main():

    # Get input from command line
    args = parseCommandLine()
    dumpFile =  args.statusFile
    compressionType = args.compressionType
    fetchFlag = args.fetchFlag

    # Read JSON dump file
    with open(dumpFile) as fd:
        data = json.load(fd)

    jobs = data['jobs']

    if compressionType == "bz2":
        dump = jobs['metahistorybz2dump']
    elif compressionType == "7z":
        dump = jobs['metahistory7zdump']

    dumpInfo = processDump(dump, fetchFlag)

    # Write dump info to JSON file
    with open("wikidump.json", "w") as fOut: 
        json.dump(dumpInfo, fOut)

    print("total dump size: {} GB, {} GiB".format(dumpInfo['dumpSizeGB'], dumpInfo['dumpSizeGiB']))

    if fetchFlag:
        hashMatchFlag = dumpInfo['hashMatchFlag']
        if hashMatchFlag:
            print("Sha1 verification was successful for all fetched files!")
        else:
            print("Sha1 verification failed for one or more fetched files!")


if __name__ == "__main__":
    main()
