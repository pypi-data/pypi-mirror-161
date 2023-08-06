from pathlib import Path
import os
import warnings
import subprocess


class Datamover:
    """
    Python wrapper for the zih datamover tools that enable exchanging files between a project space on the cluster and a fileserver share via an export node.

    See also
    --------
    .. [0] https://doc.zih.tu-dresden.de/data_transfer/datamover/
    """

    def __init__(
            self, path_to_exe: str = '/sw/taurus/tools/slurmtools/default/bin/', blocking=True):
        """
        Sets up a project-space - fileserver-mount connection.

        Parameters
        ----------
        path_to_exe : str
            Path to the datamover executables on the cluster, default: /sw/taurus/tools/slurmtools/default/bin/
        target_project : str
            Project space on the cluster, e.g. /projects/p_my_project/
        """
        self.path_to_exe = Path(path_to_exe)
        self.blocking = blocking
        dtfiles = self.path_to_exe.glob('dt*')
        self.exe = [f.name for f in dtfiles if os.access(f, os.X_OK)]
        if 'dtls' in self.exe:
            self.current_command = 'dtls'
        elif len(self.exe) > 0:
            self.current_command = self.exe[0]
        else:
            self.current_command = None

    def __getattr__(self, attr):
        '''
        Modify the __getattr__ special function: Each executable name in self.exe becomes a callable function that executes the respective shell script.
        '''
        if attr in self.exe:
            self.current_command = attr
            return self._execute
        else:
            raise AttributeError(attr)

    def _execute(self, *args):
        """
        Execute the current command with arguments and return its output.

        Parameters
        ----------
        args : list of str
            The arguments to the command to be executed, e.g. for the command "dtls" sensible arguments would be ["-l", "/foo/bar"]

        Returns
        -------
        subprocess.Popen object (see: https://docs.python.org/3/library/subprocess.html#popen-constructor)
        """
        # we append the argument "--blocking" so that datamover uses srun
        # instead of sbatch for all arguments. That way, we can use
        # subprocess.poll to figure out whether the operation has finished.
        # Also, dtls behaves the same as all other processes (by default all
        # processes except dtls use sbatch)
        args = [self.path_to_exe / self.current_command] + list(args)
        if self.blocking:
            args += ['--blocking']
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        return proc

    def is_cluster(self):
        return len(self.exe) > 0


def waitfor(proc, timeout_in_s: float = -1):
    """
    Wait for a process to complete.

    Parameters
    ----------
    proc: subprocess.Popen object (e.g. returned by the Datamover class)
    timeout_in_s: float, optional (default: endless)
        Timeout in seconds. This process will be interrupted when the timeout is reached.
    Returns
    -------
    int exit code of the process
    """
    import time
    start_time = time.time()
    print("Waiting .", end='', flush=True)
    while proc.poll() is None:
        time.sleep(0.5)
        print(".", end='', flush=True)
        if timeout_in_s > 0 and (time.time() - start_time) > timeout_in_s:
            print("\n")
            warnings.warn(
                'Timeout while waiting for process: ' + ' '.join(proc.args))
            proc.kill()
            return proc.poll()
    return proc.poll()
