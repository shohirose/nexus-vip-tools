#!/usr/bin/python3
import os
import subprocess as sp
from typing import Dict, Tuple
import re
import platform
import argparse
import sys


def get_stand_exe() -> str:
    """Get the path to standexe

    Returns:
        Path to standexe

    Raises:
        ValueError: If STAND_EXE is not found in environment variables.
    """
    if os.environ['STAND_EXE']:
        return os.environ['STAND_EXE']
    else:
        raise ValueError('STAND_EXE environment variable is not found.')


def get_nexus_exe() -> str:
    """Get the path to nexusexe

    Returns:
        Path to nexusexe

    Raises:
        ValueError: If NEXUS_EXE is not found in environment variables.
    """
    if os.environ['NEXUS_EXE']:
        return os.environ['NEXUS_EXE']
    else:
        raise ValueError('NEXUS_EXE environment variable is not found.')


def init(stand_exe: str, input_case: str, output_case: str, study: str,
         ncpus: int = 1, stdout=sp.PIPE, stderr=sp.PIPE) -> None:
    """Initialize a simulation case

    Args:
        stand_exe: Path to standexe
        input_case: Input case name
        output_case: Output case name
        study: Study name
        ncpus: Number of CPUs
        stdout: Stdout (optional)
        stderr: Stderr (optional)
    """
    cmd = [stand_exe, input_case, '-c', output_case, '-s', study]
    if ncpus > 1:
        cmd = ['mpiexec', '-np', str(ncpus)] + cmd
    proc = sp.run(cmd, stdout=stdout, stderr=stderr)
    if proc.returncode != 0:
        raise SystemExit(
            f'Initialization failed. Return code = {proc.returncode}')


def exec(nexus_exe: str, input_case: str, output_case: str, study: str,
         ncpus: int = 1, stdout=sp.PIPE, stderr=sp.PIPE) -> None:
    """Execute a simulation case

    Args:
        nexus_exe: Path to nexusexe
        input_case: Input case name
        output_case: Output case name
        study: Study name
        ncpus: Number of CPUs
        stdout: Stdout (optional)
        stderr: Stderr (optional)
    """
    cmd = [nexus_exe, input_case, '-c', output_case, '-s', study]
    if ncpus > 1:
        cmd = ['mpiexec', '-np', str(ncpus)] + cmd

    proc = sp.run(cmd, stdout=stdout, stderr=stderr)
    if proc.returncode != 0:
        raise SystemExit(
            f'Simulation failed. Return code = {proc.returncode}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse args for a Nexus simulation case.')
    parser.add_argument('input_case', help='Input case name')
    parser.add_argument('-o', '--output-case',
                        help='Output case name. If not specified, input case name will be used.')
    parser.add_argument(
        '-s', '--study', help='Study name or VDB directory name. If not specified, input case name will be used.')
    parser.add_argument(
        '--init-only', help='Run initialization only.', action='store_true')
    parser.add_argument(
        '--exec-only', help='Run a simulation without initialization.', action='store_true')
    parser.add_argument('-n', '--num-cpus',
                        help='Number of processes.', type=int, default=1)
    parser.add_argument('--log', help='Create log files.', action='store_true')
    args = parser.parse_args()

    stand_exe = get_stand_exe()
    nexus_exe = get_nexus_exe()

    if not args.output_case:
        args.output_case = args.input_case
    if not args.study:
        args.study = args.input_case

    if args.log:
        out = args.input_case + '.o.log'
        err = args.input_case + '.e.log'
        with open(out, mode='w') as fout, open(err, mode='w') as ferr:
            if not args.exec_only:
                init(stand_exe, args.input_case, args.output_case,
                     args.study, args.num_cpus, fout, ferr)
            if not args.init_only:
                exec(nexus_exe, args.input_case, args.output_case,
                     args.study, args.num_cpus, fout, ferr)
    else:
        if not args.exec_only:
            init(stand_exe, args.input_case,
                 args.output_case, args.num_cpus, args.study)
        if not args.init_only:
            exec(nexus_exe, args.input_case,
                 args.output_case, args.num_cpus, args.study)
