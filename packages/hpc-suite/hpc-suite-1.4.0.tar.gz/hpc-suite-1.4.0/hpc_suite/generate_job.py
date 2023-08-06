import sys
import os
import stat
import socket


class Generic:
    """
    Generic submission script class

    Attributes
    ----------
        shell : str
            Shell running the script
        verbose : bool
            Trigger to activate info message printing

    """

    def __init__(self, env_vars={}, header=[], env=[], exit_code=[],
                 job_name="", shell="bash", omp=1, verbose=True, **kwargs):
        """

        Parameters
        ----------
        env_vars : dict
            Dictionary containing name/value pairs of env variables
        header : list
            List containing the header lines
        env : list
            List containing the environment lines
        exit_code : list
            List containing the exit_code lines
        shell : str
            Shell running the script
        omp : int
            If > 1, number of cores to use in an OpenMP environment
        verbose : bool
            Trigger to activate info message printing
        """
        self.shell = shell
        self.verbose = verbose

        if self.shell == "bash":
            self.header = ["#!/bin/bash --login"] + header
            self.env = env + [
                "export {}={}".format(name, var)
                for name, var in env_vars.items()
            ]
        else:
            sys.exit("Error: Shell {} not available!".format(self.shell))

        if job_name:
            self.header += ["### Job name: {}".format(job_name)]

        self.exit_code = exit_code + ["exit $?"]

        self.unused_kwargs_warning(**kwargs)

    def unused_kwargs_warning(self, **kwargs):

        def is_empty_iterable(it):
            try:
                _ = iter(it)
                return len(it) == 0
            except TypeError:
                return False

        unused = "\n".join([
            "    {key}: {item}".format(key=key, item=item)
            for key, item in kwargs.items()
            if not (item is None or is_empty_iterable(item))
        ])

        if unused != "":
            print(
                "Warning: Unused keyword arguments in submission script ",
                "generation:\n{}".format(unused)
            )

    def write(self, f_name, body):
        """
        Function to write submission script file

        Parameters
        ----------
            f_name : str
                Name of submission script
            body : str
                Body of submission script

        Returns
        -------
            None
        """
        with open(f_name, "w") as f:

            if self.header:
                f.write("{}\n\n".format("\n".join(self.header)))

            if self.env:
                if self.shell in ["bash", "csh"]:
                    f.write("### Set up environment\n")
                f.write("{}\n\n".format("\n".join(self.env)))

            if body:
                if self.shell in ["bash", "csh"]:
                    f.write("### Main body\n")
                f.write("{}\n".format(body))

            if self.exit_code:
                f.write("{}\n\n".format("\n".join(self.exit_code)))

        # make executable
        st = os.stat(f_name)
        os.chmod(f_name, st.st_mode | stat.S_IEXEC)

        # print message
        if self.verbose:
            self.print_message(f_name)

    def print_message(self, f_name):
        print('The job script has been written to {}'.format(f_name))


class Modules(Generic):

    def __init__(self, purge_modules=False, modules=[], env=[], **kwargs):

        if purge_modules is None:
            _purge_modules = []
        else:
            _purge_modules = ["module purge_modules"] if purge_modules else []

        if modules is None:
            _modules = []
        else:
            _modules = ["module load {}".format(mod) for mod in modules]

        _env = _purge_modules + _modules + env

        super().__init__(env=_env, **kwargs)

        return


class SGE(Modules):

    def __init__(self, job_name="jobname", cwd=True, pass_env=True, wait=False,
                 pe=None, hpc_extra={}, header=[], env=[], array=[], **kwargs):

        # configure sge environment
        # set variable to default value if passed None from the cli interface
        sge_conf = self.configure(
            job_name="jobname" if job_name is None else job_name,
            cwd=True if cwd is None else cwd,
            pass_env=True if pass_env is None else pass_env,
            wait=False if wait is None else wait,
            pe=None if pe is None else pe,
            array=None if array == [] else array,
            **{} if hpc_extra is None else hpc_extra
        )

        # expand header by sge configuration
        header = [
            "#$ -{} {}".format(flag, param)
            for flag, param in sge_conf.items()
        ] + header

        if array:
            env = ["TASK_ID=$SGE_TASK_ID"] + env

        if pe:
            env = ["export OMP_NUM_THREADS=$NSLOTS"] + env

        super().__init__(header=header, env=env, **kwargs)

    def configure(self, job_name="jobname", cwd=True, pass_env=True,
                  wait=False, pe=None, array=[], **hpc_extra):

        config = {'N': job_name}

        if cwd:
            config['cwd'] = ""
        if pass_env:
            config['V'] = ""
        if wait:
            config['sync'] = "yes"
        if pe is not None:
            config['pe'] = pe
        if array is not None:
            config['t'] = "1-{:d}".format(len(array))

        for key, val in hpc_extra.items():
            config[key] = val

        return config

    def print_message(self, f_name):

        print('Submit this job with:')
        print('qsub {}'.format(f_name))


class SLURM(Modules):

    def __init__(self, job_name="jobname", cwd=True, pass_env=True, wait=False,
                 pe=None, hpc_extra={}, header=[], env=[], array=[], **kwargs):

        # configure slurm environment
        # set variable to default value if passed None from the cli interface
        slurm_conf = self.configure(
                job_name="jobname" if job_name is None else job_name,
                pass_env=True if pass_env is None else pass_env,
                wait=False if wait is None else wait,
                pe=None if pe is None else pe,
                array=None if array == [] else array,
                **{} if hpc_extra is None else hpc_extra)

        # expand header by slurm configuration
        header = [
            "#SBATCH {}{}".format(flag, param)
            for flag, param in slurm_conf.items()
        ] + header

        if array:
            env = ["TASK_ID=$SLURM_ARRAY_TASK_ID"] + env

        if pe:
            env = ["export OMP_NUM_THREADS=$SLURM_NTASKS"] + env

        super().__init__(header=header, env=env, **kwargs)

        return

    def configure(self, job_name="jobname", pass_env=True,
                  wait=False, pe=None, partition=None, array=[], **hpc_extra):

        config = {'--job-name=': job_name}

        # Set partition if given
        if partition is not None and pe is None:
            config['-p'] = ' {}'.format(partition)
        elif partition is not None and pe is not None:
            sys.exit("Error: Cannot set partition name and OMP")

        # OMP
        if pe is not None:
            config['-p'] = ' multicore'
            config['-n'] = pe
        if array is not None:
            config['--array'] = '=-1-{:d}'.format(len(array))

        for key, val in hpc_extra.items():
            config[key] = val

        return config

    def print_message(self, f_name):

        print('sbatch {}'.format(f_name))


class CSF3(SGE):
    def __init__(self, omp=1, hpc_extra={}, node_type=None, **kwargs):

        if omp < 1:
            sys.exit('Error: Number of cores cannot be less than 1')
        elif omp > 1:
            pe = "smp.pe {:d}".format(omp)
        else:
            pe = None

        if node_type == "high_mem":
            hpc_extra["l"] = "mem256"
        super().__init__(pe=pe, hpc_extra=hpc_extra, omp=omp, **kwargs)


class CSF4(SLURM):
    def __init__(self, omp=1, hpc_extra={}, **kwargs):

        if omp < 1:
            sys.exit('Error: Number of cores cannot be less than 1')
        elif omp > 1:
            pe = " {:d}".format(omp)
        else:
            pe = None

        super().__init__(pe=pe, hpc_extra=hpc_extra, omp=omp, **kwargs)


class Cerberus(Generic):
    def __init__(self, omp=1, env=[], **kwargs):

        if omp < 1:
            sys.exit('Error: Number of cores cannot be less than 1')
        elif omp > 1:
            env = ["OMP_NUM_THREADS={:d}".format(omp)] + env

        super().__init__(env=env, **kwargs)


class Medusa(Generic):
    def __init__(self, omp=1, env=[], **kwargs):

        if omp < 1:
            sys.exit('Error: Number of cores cannot be less than 1')
        elif omp > 1:
            env = ["OMP_NUM_THREADS={:d}".format(omp)] + env

        super().__init__(env=env, **kwargs)


def generate_job(profile='read_hostname', submit_file="submit.sh", body="",
                 env=[], array=[], **kwargs):

    """
    Generates jobscript for given profile (system)

    Parameters
    ----------

    profile : str, default = 'read_hostname'
        {'read_hostname', 'csf3, 'csf4, 'cerberus', 'medusa'}
        Name of machine
    submit_file : str, default = "submit.sh"
        Submission script filename
    body : str
        Body of submission script

    Returns
    -------
        None

    """

    if array:
        f_list = os.path.splitext(submit_file)[0] + '.txt'

        with open(f_list, "w") as f:
            for item in array:
                f.write("{}\n".format(item))

        env = [r'STEM=`sed -n "${TASK_ID}p" ' + f_list + '`'] + env

    gen_funcs = {
        "csf3": CSF3,
        "csf4": CSF4,
        "cerberus": Cerberus,
        "medusa": Medusa
    }

    if profile == 'read_hostname':
        machine = parse_hostname()
    else:
        machine = profile

    try:
        job = gen_funcs[machine](env=env, array=array, **kwargs)
    except KeyError:
        sys.exit("Error: Profile {} is not available".format(profile))

    job.write(submit_file, body)

    return


def parse_hostname():
    """
    Reads hostname and detect machine type

    Parameters
    ----------
        None

    Returns
    -------
        str
            Machine type
    """

    hostname = socket.gethostname()

    if 'csf3' in hostname:
        machine = 'csf3'
    elif 'csf4' in hostname:
        machine = 'csf4'
    elif 'cerberus' in hostname:
        machine = 'cerberus'
    elif 'medusa' in hostname:
        machine = 'medusa'
    else:
        sys.exit("Error: Hostname unsupported")
    return machine
