from shlex import split
from typing import Union, List, Callable
from pathlib import Path
from asyncio import create_subprocess_exec, run
from asyncio.subprocess import PIPE
from shutil import which
from os import name as os_name
from datetime import datetime


def arg_split(args, platform=os_name):
    """
    Like calling shlex.split, but sets `posix=` according to platform
    and unquotes previously quoted arguments on Windows
    :param args: a command line string consisting of a command with arguments, e.g. 'dir "C:/Program Files"'
    :param platform: a value like os.name would return, e.g. 'nt'
    :return: a list of arguments like shlex.split(args) would have returned
    """
    return [a[1:-1].replace('""', '"') if a[0] == a[-1] == '"' else a
            for a in (split(args, posix=False) if platform == 'nt' else split(args))]


class Py7za:
    """
    Wrapper class for running 7za.exe.

    Attributes
    ----------
    executable_7za: str (class)
        full file path to 7za.exe, executable from calling relative dir (or just pre-installed '7za' on non-Windows)
    progress: int
        7za operation progress
    files: List[str]
        files that were processed in the operation
    done: bool
        whether operation has completed
    errors: bytes
        stderr of operation, once it completes (or fails)
    """
    executable_7za = str(Path(__file__).parent / 'bin/7za.exe') if os_name == 'nt' else '7za'

    def __init__(self, arguments: Union[str, List[str]], on_start: Callable = None, working_dir: str = '.'):
        """
        Creates an (awaitable) object ready to run 7za with given arguments
        :param arguments: arguments to pass to 7za, after processing (always pass progress and output>1, disable log)
        :param on_start: callback to be called just before starting a 7za subprocess is started
        :param working_dir: working directory for 7za
        """
        if which(self.executable_7za) is None:
            raise FileNotFoundError(f'7za executable "{self.executable_7za}" not found.')

        if isinstance(arguments, str):
            # replacing backslashes with forward slashes, to allow split to interpret correctly; this works as long
            # as the Windows version supports it, but as this script only work on Python 3.8>, no issue
            arguments = arg_split(arguments)

        # ignore output arguments passed, always pass progress and output to 1, disable log
        self.arguments = [a for a in arguments if a[:3] not in ['-bs', '-bb']] + ['-bsp1', '-bso1', '-bb']

        self.progress = 0
        self.files = []

        self.done = False
        self.errors = None
        self.return_code = None

        self.working_dir = working_dir

        self.on_start = on_start

    def __await__(self):
        return self.arun().__await__()

    def _parse_stdout(self, line):
        if line:
            line = line.decode()
            if line[0] in '+U':
                self.files.append((line[0], line[2:]))
            if len(line) >= 4 and line[3] == '%':
                self.progress = int(line[:3].strip())

    async def arun(self) -> 'Py7za':
        """
        Run 7za asynchronously, updating .progress and .files during the run and .done and errors when it completes
        :return: self (with updated attributes, like .return_code and .errors)
        """
        self.progress = 0
        self.files = []

        self.done = False
        self.errors = None

        if self.on_start is not None:
            self.on_start(self)

        proc = await create_subprocess_exec(
            self.executable_7za, *self.arguments, stdout=PIPE, stderr=PIPE, cwd=self.working_dir)

        line = b''
        while True:
            b = await proc.stdout.read(1)
            if b == b'\r':
                self._parse_stdout(line)
                line = b''
            else:
                line += b
            # stdout read will return b'' when the process has ended
            if b == b'':
                self.errors = await proc.stderr.read()
                await proc.wait()
                self.done = True
                if proc.returncode == 0:
                    self.progress = 100
                self.return_code = proc.returncode
                return self

    def run(self) -> int:
        """
        Run and await arun()
        :return: return code of process
        """
        return run(self.arun())

    @classmethod
    async def list_archive(cls, archive: str, meta_data_only: bool = False) -> tuple:
        """
        Opens and lists contents of archive, returning either just metadata or metadata and a file list with details
        :param archive: name of the archive to list
        :param meta_data_only: whether to only return metadata, or parse and include archive contents details
        :return: tuple of size, compressed size, number of files, number of directories, and list of files
                 list of files is empty or a list of tuples of datetime, attributes, size, compressed size, and name
        """
        proc = await create_subprocess_exec(
            cls.executable_7za, 'l', archive, stdout=PIPE)
        line = '\n'
        listing = False
        files = []
        while line:
            line = await proc.stdout.readline()
            if line.startswith(b'----------'):
                line = await proc.stdout.readline()
                if listing:
                    break
                listing = not listing
            if not meta_data_only and listing:
                t = line.decode().split()
                if len(t) == 6:
                    d, t, a, s, c, n = t
                else:
                    d, t, a, s, n = t
                    c = 0
                files.append((datetime(*map(int, d.split('-')), *map(int, t.split(':'))), a, int(s), int(c), n))
        await proc.wait()
        metadata = line.decode().split()
        if not metadata:
            s, c, f, d = 0, 0, 0, 0
        elif len(metadata) == 8:
            __, __, s, c, f, __, d, __ = metadata
        else:
            __, __, s, c, f, __ = metadata
            d = 0
        return int(s), int(c), int(f), int(d), files
