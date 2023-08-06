#!/usr/bin/env python
#
# test_config.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import site
import os
import shlex
import os.path as op

from unittest import mock

import funpack.config as config
import funpack.custom as custom

from . import clear_plugins, tempdir, touch

def get_fmrib_config_dir():
    for sitedir in site.getsitepackages():
        fmribdir = op.join(sitedir, 'funpack', 'configs', 'fmrib')
        if op.exists(fmribdir):
            return fmribdir

    raise RuntimeError('Cannot locate FMRIB configuration directory')


# This function is essentially testing funpack.util.findConfigFile
@clear_plugins
def test_parseArgs_configFilePaths():

    custom.registerBuiltIns()

    with tempdir() as td:
        cfgdir = op.join(td, 'a')
        os.makedirs(op.join(cfgdir, 'b'))
        with mock.patch.dict(os.environ, FUNPACK_CONFIG_DIR=cfgdir):
            cfgfile = op.join(cfgdir, 'b', 'myconfig.cfg')
            varfile = op.join(cfgdir, 'b', 'myvars.tsv')
            plgfile = op.join(cfgdir, 'b', 'myplugin.py')
            touch(cfgfile)
            touch(varfile)
            touch(plgfile)

            # full path
            args = config.parseArgs(shlex.split(f'-cfg {cfgfile} out in'))[0]
            assert args.config_file == [cfgfile]

            # rel path
            relp = op.join('a', 'b', 'myconfig.cfg')
            args = config.parseArgs(shlex.split(f'-cfg {relp} out in'))[0]
            assert args.config_file == [cfgfile]

            # rel to cfgdir
            relp = op.join('b', 'myconfig.cfg')
            args = config.parseArgs(shlex.split(f'-cfg {relp} out in'))[0]
            assert args.config_file == [cfgfile]

            # dotted rel to cfgdir
            args = config.parseArgs(shlex.split('-cfg b.myconfig out in'))[0]
            assert args.config_file == [cfgfile]

            argv = ['-vf', varfile,
                    '-vf', op.join('a', 'b', 'myvars.tsv'),
                    '-vf', op.join('b', 'myvars.tsv'),
                    '-vf', 'b.myvars',
                    'output',  'input']

            args = config.parseArgs(argv)[0]
            assert args.variable_file == [varfile, varfile, varfile, varfile]

            argv = ['-p', plgfile,
                    '-p', op.join('a', 'b', 'myplugin.py'),
                    '-p', op.join('b', 'myplugin.py'),
                    '-p', 'b.myplugin',
                    'output',  'input']
            args = config.parseArgs(argv)[0]
            assert args.plugin_file == [plgfile, plgfile, plgfile, plgfile]

@clear_plugins
def test_num_jobs():

    custom.registerBuiltIns()

    with mock.patch('multiprocessing.cpu_count', return_value=99):
        assert config.parseArgs('-nj -1 out in'.split())[0].num_jobs == 99
        assert config.parseArgs('-nj -5 out in'.split())[0].num_jobs == 99

    assert config.parseArgs('-nj 0 out in'.split())[0].num_jobs == 1
    assert config.parseArgs('-nj 1 out in'.split())[0].num_jobs == 1
    assert config.parseArgs('-nj 5 out in'.split())[0].num_jobs == 5


@clear_plugins
def test_multiple_config_file():

    custom.registerBuiltIns()
    with tempdir():

        with open('one.cfg',   'wt') as f:
            f.write('variable\t1\n')
            f.write('variable_file\tvf\n')
            f.write('processing_file\tpf1\n')
        with open('two.cfg',   'wt') as f:
            f.write('variable\t2\n')
            f.write('datacoding_file\tdf\n')
            f.write('processing_file\tpf2\n')
        with open('three.cfg', 'wt') as f:
            f.write('variable\t3\n')
            f.write('processing_file\tpf3\n')
        argv = '-cfg one.cfg -cfg two.cfg -cfg three.cfg out in'.split()
        args = config.parseArgsWithConfigFile(argv)[0]
        assert args.variable        == [1, 2, 3]
        assert args.variable_file   == ['vf']
        assert args.datacoding_file == ['df']
        assert args.processing_file ==  'pf3'


@clear_plugins
def test_recursive_config_file():

    custom.registerBuiltIns()
    with tempdir():

        with open('one.cfg',   'wt') as f:
            f.write('variable\t1\n')
            f.write('variable_file\tvf\n')
            f.write('processing_file\tpf1\n')
            f.write('config_file\ttwo.cfg\n')
        with open('two.cfg',   'wt') as f:
            f.write('variable\t2\n')
            f.write('datacoding_file\tdf\n')
            f.write('processing_file\tpf2\n')
            f.write('config_file\tthree.cfg\n')
            f.write('config_file\tfour.cfg\n')
        with open('three.cfg', 'wt') as f:
            f.write('variable\t3\n')
            f.write('processing_file\tpf3\n')
        with open('four.cfg', 'wt') as f:
            f.write('variable\t4\n')
            f.write('category_file\tcf\n')
            f.write('processing_file\tpf4\n')
        argv = '-cfg one.cfg out in'.split()
        args = config.parseArgsWithConfigFile(argv)[0]
        assert args.variable        == [1, 2, 3, 4]
        assert args.variable_file   == ['vf']
        assert args.datacoding_file == ['df']
        assert args.processing_file ==  'pf4'
        assert args.category_file   ==  'cf'
