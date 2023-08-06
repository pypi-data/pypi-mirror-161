#!/usr/bin/env python
#
# This script refreshes the UKB showcase schema files that are built into
# FUNPACK. I run it by hand when releasing a new version of FUNPACK.
#


import itertools  as it
import subprocess as sp
import os.path    as op
import               glob
import               shlex


def download_file(url, dest):
    print(f'{url} -> {dest}')
    cmd = f'wget -O {dest} {url}'
    sp.run(shlex.split(cmd), stdout=sp.DEVNULL, stderr=sp.DEVNULL)


def main():
    basedir = op.join(op.dirname(__file__), '..', '..')
    datadir = op.join(basedir, 'funpack', 'data')

    baseurl = 'biobank.ctsu.ox.ac.uk/'

    download_file(f'{baseurl}/ukb/scdown.cgi?fmt=txt&id=1',
                  op.join(datadir, 'field.txt'))
    download_file(f'{baseurl}/ukb/scdown.cgi?fmt=txt&id=2',
                  op.join(datadir, 'encoding.txt'))

    codings = it.chain(
        glob.glob(op.join(datadir, 'coding',    '*.tsv')),
        glob.glob(op.join(datadir, 'hierarchy', '*.tsv')))

    for coding in codings:
        # all files are called "coding<ID>.tsv"
        cid = op.basename(coding)[6:-4]
        url = f'{baseurl}/crystal/codown.cgi?id={cid}'
        download_file(url, coding)


if __name__ == '__main__':
    main()
