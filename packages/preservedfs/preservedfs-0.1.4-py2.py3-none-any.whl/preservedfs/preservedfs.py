#!/usr/bin/python3
#    Copyright (C) 2022  Thibaud Toullier  <thibaud.toullier@inria.fr>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#
#    This code is largely inspired from the example of xmp.py at:
#    https://github.com/libfuse/python-fuse/blob/master/example/xmp.py
#
#    Based on the Userspace nullfs-alike, this Userspace only record the
#    modified files
#
#    It works with three directories:
#    - `mnt` the directory mounted (the one you'll browse)
#    - `target` the directory to browse files from
#    - `local` the directory that record changes
#
#    A removed file is a file in `local` with the same name but with the
#    prefix '[x]'.
#    Any writing is done in the `local` folder.
import os
import sys
import errno
import fcntl
import shutil
import functools
import subprocess
from threading import Lock
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse

import logging
logging.basicConfig(
    format="%(asctime)s @%(name)s [%(levelname)s]: %(message)s",
    level=os.environ.get("LOGLEVEL", "INFO"),
    filename='into-the-shell.log')
log = logging.getLogger("FUSE-logger")

if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)

fuse.feature_assert('stateful_files', 'has_init')


def flag2mode(flags):
    "Transforms file flags to human readable modes."
    md = {os.O_RDONLY: 'rb', os.O_WRONLY: 'wb', os.O_RDWR: 'wb+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m


def touch(path):
    "Create the file determined by `path`."
    with open(path, 'a'):
        os.utime(path, None)


class PreservedFS(Fuse):
    """Create a filesystem that keep only modifications.

    This code is largely inspired from the example of xmp.py
    [here](https://github.com/libfuse/python-fuse/blob/master/example/xmp.py)

    Based on the Userspace nullfs-alike, this Userspace only record the
    modified files

    It works with three directories:
    - `mnt` the directory mounted (the one you'll browse)
    - `root` (called also `target`) the directory to browse files from
    - `local` the directory that record changes

    A removed file is a file in `local` with the same name but with the
    prefix '[x]'.
    Any writing is done in the `local` folder.

    Attributes
    ----------
    local : str
        Location of the local folder
    root : str
        Location of the folder to be mounted
    """

    def __init__(self, local, root, *args, **kw):
        "Creates the Preserved FileSystem in Userspace."
        Fuse.__init__(self, *args, **kw)
        self.local = local
        self.root = root

    def _full_path(self, path):
        "Determines the true path (local or not)."
        if path == '/':
            return self._get_root(path)
        if os.path.exists(self._get_local(path)):
            return self._get_local(path)
        return self._get_root(path)

    def _make_it_local(self, path):
        "Create a copy in the `local` folder of the original file."
        if not os.path.exists(self._get_local(path)):
            shutil.copy2(self._get_root(path),
                         self._get_local(path))

    def _mark_as_removed(self, path):
        "Mark something as removed."
        fname = os.path.basename(path)
        fname = '[x]' + fname
        os.makedirs(self._get_local(os.path.dirname(path)), exist_ok = True)
        touch(self._get_local(os.path.join(os.path.dirname(path),fname)))

    def _get_local(self, path):
        "Get full local path from relative one."
        if path == '/':
            return self.local
        return os.path.join(self.local, path[1:])

    def _get_root(self, path):
        "Get full root path from relative one."
        if path == '/':
            return self.root
        return os.path.join(self.root, path[1:])

    def getattr(self, path):
        "Override `getattr`."
        return os.lstat(self._full_path(path))

    def readlink(self, path):
        "Override `readlink`."
        return os.readlink(self._full_path(path))

    def readdir(self, path, offset):
        "Override `readdir`."
        removed_items = None
        if not os.path.exists(self._get_local(path)) and not os.path.exists(self._get_root(path)):
            return -errno.ENOENT
        if os.path.exists(self._get_local(path)):
            removed_items = [x[3:] for x in os.listdir(self._get_local(path)) if x[:3] == '[x]']
            if removed_items:
                l = [x for x in list(set(os.listdir(self._get_local(path)) + os.listdir(self._get_root(path)))) if x not in removed_items and x[:3] != '[x]']
                for e in l:
                    yield fuse.Direntry(e)
            else:
                for e in set(os.listdir(self._get_local(path)) + os.listdir(self._get_root(path))):
                    yield fuse.Direntry(e)
        else:
            for e in os.listdir(self._get_root(path)):
                yield fuse.Direntry(e)

    def unlink(self, path):
        "Override `unlink`."
        self._mark_as_removed(path)

    def rmdir(self, path):
        "Override `rmdir`."
        # mark it as removed in local
        self._mark_as_removed(path)

    def symlink(self, path, path1):
        "Override `symlink`."
        self._make_it_local(path)
        os.makedirs(os.path.dirname(self._get_local(path1)), exist_ok = True)
        os.symlink(self._get_local(path), self._get_local(path1))

    def rename(self, path, path1):
        "Override `rename`."
        self._make_it_local(path)
        os.rename(self._get_local(path), self._get_local(path1))
        self._mark_as_removed(path)

    def link(self, path, path1):
        "Override `link`."
        self._make_it_local(path)
        os.makedirs(os.path.dirname(self._get_local(path1)), exist_ok = True)
        os.link(self._get_local(path), self._get_local(path1))

    def chmod(self, path, mode):
        "Override `chmod`."
        self._make_it_local(path)
        os.chmod(self._get_local(path), mode)

    def chown(self, path, user, group):
        "Override `chown`."
        self._make_it_local(path)
        os.chown(self._get_local(path), user, group)

    def truncate(self, path, size):
        "Override `truncate`."
        with open(self._full_path(path), "a") as f:
            f.truncate(size)

    def mknod(self, path, mode, dev):
        "Override `mknod`."
        os.mknod(self._full_path(path), mode, dev)

    def mkdir(self, path, mode):
        "Override `mkdir`."
        os.mkdir(self._get_local(path), mode)

    def utime(self, path, times):
        "Override `utime`."
        self._make_it_local(path)
        os.utime(self._get_local(path), times)

    def statfs(self):
        """
        Should return an object with statvfs attributes (f_bsize, f_frsize...).
        Eg., the return value of os.statvfs() is such a thing (since py 2.2).
        If you are not reusing an existing statvfs object, start with
        fuse.StatVFS(), and define the attributes.

        To provide usable information (ie., you want sensible df(1)
        output, you are suggested to specify the following attributes:

            - f_bsize - preferred size of file blocks, in bytes
            - f_frsize - fundamental size of file blcoks, in bytes
                [if you have no idea, use the same as blocksize]
            - f_blocks - total number of blocks in the filesystem
            - f_bfree - number of free blocks
            - f_files - total number of file inodes
            - f_ffree - nunber of free file inodes
        """
        return os.statvfs(".")


    class PreservedFSFile(object):
        """Custom PreservedFS file class.

        Get the right file to be opened
        depending on the specified flags and
        existence in `root` or `local` directory.

        Warning
        -------
        You should not call this class diretly from
        `python-fuse`.
        Instead, this class is wrapped with the function
        `wrap_parent` to get the outer class `PreservedFS`
        in its constructor.

        Attributes
        ----------
        parent : PreservedFS
            the outer instantiated class of the filesystem.
        path : str
            path of the file
        flags : int
            flags for opening the file
        mode : tuple
            modes used for opening the file
        fullpath : str
            the fullpath used to open the file
        file : FileObject
            the opened file Python object
        fd : FileObject
            the opened file Python object descriptor
        iolock : Lock
            a lock to do locking if `os.pread` not available
        """

        def __init__(self, parent, path, flags, *mode):
            "Called when opening a new file."
            self.parent = parent
            self.path = path
            self.flags = flags
            self.mode = mode

            if not os.path.exists(parent._full_path(path)):
                return
            local_modes = flag2mode(flags)
            if 'w' in local_modes or 'a' in local_modes:
                self.parent._make_it_local(self.path)

            self.fullpath = parent._full_path(path)
            self.file = os.fdopen(os.open(self.fullpath, flags, *mode),
                                  flag2mode(flags))
            self.fd = self.file.fileno()


            if hasattr(os, 'pread'):
                self.iolock = None
            else:
                self.iolock = Lock()

        def read(self, length, offset):
            "Override `read`."
            if self.iolock:
                self.iolock.acquire()
                try:
                    self.file.seek(offset)
                    return self.file.read(length)
                finally:
                    self.iolock.release()
            else:
                return os.pread(self.fd, length, offset)

        def write(self, buf, offset):
            "Override `write`."
            if self.iolock:
                self.iolock.acquire()
                try:
                    self.file.seek(offset)
                    self.file.write(buf)
                    return len(buf)
                finally:
                    self.iolock.release()
            else:
                return os.pwrite(self.fd, buf, offset)

        def release(self, flags):
            "Override `release`."
            if hasattr(self, 'file'):
                self.file.close()

        def _fflush(self):
            "Override `_fflush`."
            if 'w' in self.file.mode or 'a' in self.file.mode:
                self.file.flush()

        def fsync(self, isfsyncfile):
            "Override `fsync`."
            self._fflush()
            if isfsyncfile and hasattr(os, 'fdatasync'):
                os.fdatasync(self.fd)
            else:
                os.fsync(self.fd)

        def flush(self):
            "Override `flush`."
            self._fflush()
            # cf. xmp_flush() in fusexmp_fh.c
            os.close(os.dup(self.fd))

        def fgetattr(self):
            "Override `fgetattr`."
            if hasattr(self, 'fd'):
                return os.fstat(self.fd)

        def ftruncate(self, len):
            "Override `ftruncate`."
            self.file.truncate(len)

        def lock(self, cmd, owner, **kw):
            "Override `lock`."
            # The code here is much rather just a demonstration of the locking
            # API than something which actually was seen to be useful.

            # Advisory file locking is pretty messy in Unix, and the Python
            # interface to this doesn't make it better.
            # We can't do fcntl(2)/F_GETLK from Python in a platfrom independent
            # way. The following implementation *might* work under Linux.
            #
            # if cmd == fcntl.F_GETLK:
            #     import struct
            #
            #     lockdata = struct.pack('hhQQi', kw['l_type'], os.SEEK_SET,
            #                            kw['l_start'], kw['l_len'], kw['l_pid'])
            #     ld2 = fcntl.fcntl(self.fd, fcntl.F_GETLK, lockdata)
            #     flockfields = ('l_type', 'l_whence', 'l_start', 'l_len', 'l_pid')
            #     uld2 = struct.unpack('hhQQi', ld2)
            #     res = {}
            #     for i in xrange(len(uld2)):
            #          res[flockfields[i]] = uld2[i]
            #
            #     return fuse.Flock(**res)

            # Convert fcntl-ish lock parameters to Python's weird
            # lockf(3)/flock(2) medley locking API...
            op = { fcntl.F_UNLCK : fcntl.LOCK_UN,
                   fcntl.F_RDLCK : fcntl.LOCK_SH,
                   fcntl.F_WRLCK : fcntl.LOCK_EX }[kw['l_type']]
            if cmd == fcntl.F_GETLK:
                return -errno.EOPNOTSUPP
            elif cmd == fcntl.F_SETLK:
                if op != fcntl.LOCK_UN:
                    op |= fcntl.LOCK_NB
            elif cmd == fcntl.F_SETLKW:
                pass
            else:
                return -errno.EINVAL

            fcntl.lockf(self.fd, op, kw['l_start'], kw['l_len'])

    def main(self, *a, **kw):
        """Function called to lauch the FS.

        Overriding this functions makes possible
        to change the `file_class` attribute and
        therefore enables its customization.

        Please note the wrapping of such class
        to provide the `parent` parameter.
        """
        def wrap_parent(parent, *args, **kwds):
            class WrappedCls(self.PreservedFSFile):
                __init__ = functools.partialmethod(self.PreservedFSFile.__init__, parent, *args, **kwds)
            return WrappedCls

        self.file_class = wrap_parent(self)

        return Fuse.main(self, *a, **kw)

def run(root, mnt, local):

    usage = """
Userspace nullfs-alike: mirror the filesystem tree from some point on
while recording only modifications.

""" + Fuse.fusage

    if os.path.isdir(mnt) and os.path.ismount(mnt):
        subprocess.call(['sudo', 'umount', mnt, '--force'])
    else:
        os.makedirs(mnt, exist_ok=True)

    sys.argv.append(root)
    sys.argv.append(mnt)
    server = PreservedFS(local,
                         root,
                         version="%prog " + fuse.__version__,
                         usage=usage,
                         dash_s_do='setsingle')

    server.parse(errex=1)

    server.main()


if __name__ == '__main__':
    EXAMPLE_FOLDER = os.path.join(os.getcwd(), 'example')
    ROOT = os.path.join(EXAMPLE_FOLDER, 'target')
    MNT = os.path.join(EXAMPLE_FOLDER, 'mnt')
    os.makedirs(MNT, exists_ok=True)
    LOCAL = os.path.join(EXAMPLE_FOLDER, 'local')
    run(ROOT, MNT, LOCAL)
