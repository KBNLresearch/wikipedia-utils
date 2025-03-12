# Wikipedia utilities

This repo contains utility scripts for working with Wikipedia data dumps.

## wikidump.py

Get info about a dump from the dump status file ([example file here](https://dumps.wikimedia.org/nlwiki/20250201/dumpstatus.json)), and optionally download the files in either bz2 or 7z format.

### Usage

```
wikidump.py [-h] [--compression {bz2,7z}] [--fetch] statusFile
```

### positional arguments

- statusFile: input Wikipedia JSON dump status file.

### optional arguments

- `--compression`, `-c`: compression type. Allowed values are bz2 (default) and 7z.
- `--fetch`, `-f`: download all files in the dump.

If the `--fetch` option is used, the script verifies the SHA1 hash of each downloaded file against its corresponding value in the dump status file.

### Output file

The script writes a JSON file with information on the dump and its underlying files. If the `--fetch` option is used, this includes information on whether the Sha1 verification was successful. Here's an example:

```json
{
  "dumpStatus": "done",
  "dumpSizeBytes": 471341446,
  "dumpSizeGB": 0.47,
  "dumpSizeGiB": 0.44,
  "files": [
    {
      "fileName": "nlwiki-20250201-pages-meta-history1.xml-p1p4491.7z",
      "fileSizeBytes": 231165739,
      "fileUrl": "https://dumps.wikimedia.org/nlwiki/20250201/nlwiki-20250201-pages-meta-history1.xml-p1p4491.7z",
      "fileMd5": "2d793bdf2f0130cc82250ea1a40e33e3",
      "fileSha1": "a047757aea7c815cf787970956332c0234104c22",
      "sha1Match": true
    },
    {
      "fileName": "nlwiki-20250201-pages-meta-history1.xml-p4492p13457.7z",
      "fileSizeBytes": 240175707,
      "fileUrl": "https://dumps.wikimedia.org/nlwiki/20250201/nlwiki-20250201-pages-meta-history1.xml-p4492p13457.7z",
      "fileMd5": "e6b25fbc39802f9b5f41ba45146259ba",
      "fileSha1": "1f0d1453841387164395e060f89dcee4519b0a66",
      "sha1Match": true
    }
  ],
  "hashMatchFlag": true
}
```
