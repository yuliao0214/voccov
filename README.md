voccov is a tool based on freeq to count vocabulary coverage

Usage
=====

```
usage: voccov.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [-s SORT] [-r] [-p]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE
  -o OUTPUT_FILE, --output OUTPUT_FILE
  -s SORT, --sort SORT  sorted by coca or occ
  -r, --reverse         reverse sort result
  -p, --plot            show coverage figure
```
for example:
```
    ./voccov.py -i test/Jane_Eyre.txt -o output
```

Licenses
========
The voccov is released under the BSD-2-Clause license.

The lemmas.txt, which is derrived from the collective work by Keven Atkinson and many others, is released under the licenses mentioned in COPYRIGHT.

Thanks to
=========
freeq: https://github.com/Enaunimes/freeq

12dicts word list: http://wordlist.aspell.net/12dicts-readme/

lemmas.txt is derrived from 2+2+3lem.txt in version 6 of 12dicts word list

