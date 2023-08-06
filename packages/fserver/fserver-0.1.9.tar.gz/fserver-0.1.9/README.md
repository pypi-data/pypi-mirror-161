# fserver

File Sharing Server implemented with flask and gevent


### Install or Upgrade 

```shell
$ pip install fserver -U
```


### Usage 

```text
usage: fserver [-h] [-d] [-u] [-o] [-i IP] [-p PORT] [-r PATH] [-a PATH [PATH ...]] [-b PATH [PATH ...]] [-s STRING]
               [-v] [-g] [--git_path GIT_PATH] [--username USERNAME] [--password PASSWORD]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           run with debug mode
  -u, --upload          run with upload file function
  -o, --override        override mode for upload file
  -i IP, --ip IP        ip address for listening, default 0.0.0.0
  -p PORT, --port PORT  port for listening, default 2000
  -r PATH, --root PATH  root path for server, default current path
  -a PATH [PATH ...], --allow PATH [PATH ...]
                        run with allow_list. Only [PATH ...] will be accessed
  -b PATH [PATH ...], --block PATH [PATH ...]
                        run with block_list. [PATH ...] will not be accessed
  -s STRING, --string STRING
                        share string only
  -v, --version         print version info
  -g, --git             open git http service for project in root
  --git_path GIT_PATH   path for git executable file
  --username USERNAME   username for git authentication
  --password PASSWORD   password for git authentication
```

### Matching Rule

argument for `-a` and `-b` support wildcards "\*" and "\*\*". 

"*" match multiple arbitrary character in a file name or directory name.

"**" match arbitrary multi-Level directories.

**example:** 

|          | */a2 | *1/a2 | b1/* | **/an | b1/** |
| -------- | ---- | ----- | ---- | ----- | ----- |
| a1/a2    | yes  | yes   |      |       |       |
| a1/an    |      |       |      | yes   |       |
| a1/a2/an |      |       |      | yes   |       |
| b1/a2    | yes  | yes   | yes  |       | yes   |
| b1/a2/an |      |       |      | yes   | yes   |




### License
[MIT](LICENSE)