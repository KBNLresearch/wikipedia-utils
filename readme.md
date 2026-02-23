# Wikipedia utilities

This repo contains utility scripts for working with Wikipedia data dumps.

## wikidump.py

Get info about a dump from the dump status file ([example file here](https://dumps.wikimedia.org/nlwiki/20260101/dumpstatus.json)), and optionally download the files (full history + metadata) in either bz2 or 7z format.

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

The script writes a JSON file with information on the dump and its underlying files. This includes information on whether the Sha1 verification was successful. The name of the output file is based on the basename of the dump status file. Here's an example:

```json
{
  "dumpStatus": "done",
  "dumpSizeBytes": 345023943,
  "dumpSizeGB": 0.35,
  "dumpSizeGiB": 0.32,
  "files": [
    {
      "fileName": "nlwiki-20250301-pages-meta-history1.xml-p132305p134538.7z",
      "fileSizeBytes": 9121886,
      "fileUrl": "https://dumps.wikimedia.org/nlwiki/20250301/nlwiki-20250301-pages-meta-history1.xml-p132305p134538.7z",
      "fileMd5": "715138c7e383f977d3cd628b9453e07c",
      "fileSha1": "ba027d605ba0131c9e02d806684baa3960e9a20c",
      "fileSha1Match": true
    },
    {
      "fileName": "nlwiki-20250301-pages-meta-history5.xml-p2447631p2601583.7z",
      "fileSizeBytes": 143717317,
      "fileUrl": "https://dumps.wikimedia.org/nlwiki/20250301/nlwiki-20250301-pages-meta-history5.xml-p2447631p2601583.7z",
      "fileMd5": "b916ca6dcd727d264f2e0e90bc772bc6",
      "fileSha1": "c89f62bec8ef6a76a1e2e4c35644d2fe7d43721b",
      "fileSha1Match": true
    },
    {
      "fileName": "nlwiki-20250301-pages-meta-history6.xml-p5118941p5145455.7z",
      "fileSizeBytes": 192184740,
      "fileUrl": "https://dumps.wikimedia.org/nlwiki/20250301/nlwiki-20250301-pages-meta-history6.xml-p5118941p5145455.7z",
      "fileMd5": "72af09babb6a5f7dd9b11d3d51842a97",
      "fileSha1": "609472080020bb6e9ab07e3446b6171da49b62b7",
      "fileSha1Match": true
    }
  ],
  "compressionType": "7z",
  "hashMatchFlag": true
}
```

### Resuming failed download attempts

The script initially writes a "false" value for all "fileSha1Match" occurrences. If the `--fetch` option is used, these values (and the output file) are updated at each successful download attempt. This allows the script to resume failed or aborted download attempts without having to download every file in the dump again: if it detects an output file already exists, it reads it contents, and then only fetches the data files for which "fileSha1Match" is "false", skipping any files with a "true" value.
