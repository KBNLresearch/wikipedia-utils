import argparse
import json
import os
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


def getDumpInfo(dump):
    """Get info onm dump and all its files"""

    # Initialize cumulative size of all files in this dump 
    sizeBytes = 0
    # Dump info dictionary
    dumpInfo = {}
    # Files info list
    filesInfo = []
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
            fileInfo['fileSha1Match'] = False 
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

    return dumpInfo


def main():

    # Get input from command line
    args = parseCommandLine()
    dumpFile =  args.statusFile
    compressionType = args.compressionType
    fetchFlag = args.fetchFlag

    # Flag that indicates whether we need to get dump info
    # from existing output file (useful for resuming earlier
    # failed runs)
    loadStatusFile = True

    # Flag that indicates whether hash match was successful for all downloaded files
    hashMatchFlag = True

    # Generate output file name from base name of dump file
    bName = os.path.splitext(os.path.basename(dumpFile))[0]
    outFile = ("wikidump-{}.json").format(bName)

    # If output file already exists, load contents to dumpInfo
    # dictionary.
    if os.path.isfile(outFile):
        with open(outFile) as fOut:
            dumpInfo = json.load(fOut)
            # If compression type is not identical to previous call
            # we still need to use the status file
            try:
                if dumpInfo['compressionType'] == compressionType:
                    loadStatusFile = False
            except KeyError:
                # Re-run on old-style file ...
                loadStatusFile = True

    # Create dumpInfo dictionary from dump file
    if loadStatusFile:
        with open(dumpFile) as fD:
            data = json.load(fD)
        jobs = data['jobs']

        if compressionType == "bz2":
            dump = jobs['metahistorybz2dump']
        elif compressionType == "7z":
            dump = jobs['metahistory7zdump']

        dumpInfo = getDumpInfo(dump)
        dumpInfo['compressionType'] = compressionType

    print("total dump size ({}): {} GB, {} GiB".format(dumpInfo['compressionType'],
                                                       dumpInfo['dumpSizeGB'],
                                                       dumpInfo['dumpSizeGiB']))

    # Download files
    if fetchFlag:
        for file in dumpInfo['files']:
            fileName = file['fileName']
            fileUrl = file['fileUrl']
            fileSha1 = file['fileSha1']
            fileSha1Match = file['fileSha1Match']

            # Skip any files that were already downloaded in a previous run 
            if not fileSha1Match:
                # Fetch one file
                computedHash, hashMatch = fetchFile(fileUrl, fileName, fileSha1)
                if not hashMatch:
                    hashMatchFlag = False
                # Update dumpInfo dictionary
                file.update({'fileSha1Match': hashMatch})
                dumpInfo.update()

            # Write dump info to JSON file
            with open(outFile, "w") as fOut: 
                json.dump(dumpInfo, fOut, indent=2)
        
        dumpInfo['hashMatchFlag'] = hashMatchFlag

        if hashMatchFlag:
            print("Sha1 verification was successful for all fetched files!")
        else:
            print("Sha1 verification failed for one or more fetched files!")

    # Write dump info to JSON file
    with open(outFile, "w") as fOut: 
        json.dump(dumpInfo, fOut, indent=2)


if __name__ == "__main__":
    main()
