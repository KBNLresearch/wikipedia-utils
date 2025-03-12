# Wikipedia utilities

This repo contains utility scripts for working with Wikipedia data dumps.

## wikidump.py

Get info about a dump from the dump status file ([example file here](https://dumps.wikimedia.org/nlwiki/20250201/dumpstatus.json)), and optionally download the files in either bz2 or 7z format.

### Usage

```
wikidump.py [-h] [--compression {bz2,7z}] [--fetch] statusFile
```

### positional arguments

- statusFile: input Wikipedia JSON dump status file. Ex

### optional arguments

- `--compression`, `-c`: compression type. Allowed values are bz2 (default) and 7z.
- `--fetch`, `-f`: download all files in the dump.

If the `--fetch` option is used, the script verifies the SHA1 hash of each downloaded file against its corresponding value in the dump status file.

### Output file

The script writes a JSON file with information on the dump and its underlying files. If the `--fetch` option is used, this includes information on whether the Sha1 verification was successful.