from os import listdir
from re import search, match
from subprocess import Popen, PIPE


def available_cpu_count():
    """
    Determine the number of available virtual or physical CPUs on the system,
    running the scripts, i.e. user/real as output by time(1) when called with
    an optimally scaling userspace-only program.
    :return: int, number of available virtual or physical CPUs
    """

    # cpuset, preferred if available
    # Note that: cpuset may restrict the number of *available* processors
    try:
        with open('/proc/self/status') as f:
            m = search(r'(?m)^Cpus_allowed:\s*(.*)$', f.read())
        if m:
            res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        pass

    # Python 2.6+, covers most use cases where cpuset is not available
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass

    # https://github.com/giampaolo/psutil preferred fallback, if installed
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        from psutil import cpu_count
        return cpu_count()
    except ImportError:
        try:
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            from psutil import NUM_CPUS
            return NUM_CPUS
        except ImportError:
            pass

    # POSIX
    try:
        from os import sysconf
        res = int(sysconf('SC_NPROCESSORS_ONLN'))

        if res > 0:
            return res
    except (ImportError, ValueError):
        pass

    # Windows
    try:
        from os import environ
        res = int(environ['NUMBER_OF_PROCESSORS'])

        if res > 0:
            return res
    except (ImportError, KeyError, ValueError):
        pass

    # jython
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        from java.lang import Runtime

        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()

        if res > 0:
            return res
    except ImportError:
        pass

    # BSD
    try:
        sysctl = Popen(['sysctl', '-n', 'hw.ncpu'],
                       stdout=PIPE)
        sc_stdout = sysctl.communicate()[0]
        res = int(sc_stdout)

        if res > 0:
            return res
    except (OSError, ValueError):
        pass

    # Linux
    try:
        with open('/proc/cpuinfo') as f:
            res = f.read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        pass

    # Solaris
    try:
        pseudo_devices = listdir('/devices/pseudo/')
        res = 0
        for pd in pseudo_devices:
            if match(r'^cpuid@[0-9]+$', pd):
                res += 1

        if res > 0:
            return res
    except OSError:
        pass

    # Other UNIXes (heuristic)
    try:
        try:
            with open('/var/run/dmesg.boot') as f:
                dmesg = f.read()
        except IOError:
            dmesg_process = Popen(['dmesg'], stdout=PIPE)
            dmesg = dmesg_process.communicate()[0]

        res = 0
        while '\ncpu' + str(res) + ':' in dmesg:
            res += 1

        if res > 0:
            return res
    except OSError:
        pass

    raise Exception('Can not determine number of CPUs on this system')
