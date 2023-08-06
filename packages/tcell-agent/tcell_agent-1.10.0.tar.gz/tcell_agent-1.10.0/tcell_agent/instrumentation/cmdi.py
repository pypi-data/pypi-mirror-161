import os
import subprocess

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.instrumentation.utils import get_tcell_context
from tcell_agent.utils.compat import a_string
from tcell_agent.config.configuration import get_config
from tcell_agent.tcell_logger import get_module_logger


@catches_generic_exception(__name__,
                           "Error in command injection inspection",
                           return_value=False)
def should_block_shell_command(command):
    if command is None:
        return False

    if not a_string(command):
        command = " ".join(command)

    tcell_context = get_tcell_context()
    command_injection_policy = TCellAgent.get_policy(PolicyTypes.COMMAND_INJECTION)

    return command_injection_policy.block_command(command, tcell_context)


class TCellDefaultFlag(object):
        pass


def _tcell_os_system(_tcell_original_system, cmd):
    if should_block_shell_command(cmd):
        return 1

    return _tcell_original_system(cmd)


def _tcell_os_popen(func, *args, **kwargs):
    cmd = args[0] if args else kwargs.get('cmd', '')
    mode = args[1] if len(args) > 1 else (kwargs.get('mode') or 'r')

    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        result = TemporaryFile(mode)
        return result

    return func(*args, **kwargs)


def _tcell_os_popen_two(_tcell_original_popen_two, cmd, mode="t", bufsize=TCellDefaultFlag):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        output = TemporaryFile("r")
        return (writeable, output)

    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_two(cmd, mode)

    return _tcell_original_popen_two(cmd, mode, bufsize)


def _tcell_os_popen_three(_tcell_original_popen_three, cmd, mode="t", bufsize=TCellDefaultFlag):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        readable = TemporaryFile("r")
        error = TemporaryFile("r")
        return (writeable, readable, error)
    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_three(cmd, mode)

    return _tcell_original_popen_three(cmd, mode, bufsize)


def _tcell_os_popen_four(_tcell_original_popen_four, cmd, mode="t", bufsize=TCellDefaultFlag):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        output_n_error = TemporaryFile("r")
        return (writeable, output_n_error)
    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_four(cmd, mode)

    return _tcell_original_popen_four(cmd, mode, bufsize)


def _tcell_subprocess_call(func, *args, **kwargs):
    if len(args) > 0 and should_block_shell_command(args[0]):
        return 1

    return func(*args, **kwargs)


def _tcell_subprocess_check_output(func, *args, **kwargs):
    if len(args) > 0 and should_block_shell_command(args[0]):
        raise subprocess.CalledProcessError(1, args, b"Blocked by TCell")

    return func(*args, **kwargs)

def _tcell_popen2_popen_two(_tcell_original_popen_two, cmd, bufsize=TCellDefaultFlag, mode="t"):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        readable = TemporaryFile("r")
        return (readable, writeable)

    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_two(cmd, mode=mode)

    return _tcell_original_popen_two(cmd, bufsize, mode)

def _tcell_popen2_popen_three(_tcell_original_popen_three, cmd, bufsize=TCellDefaultFlag, mode="t"):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        readable = TemporaryFile("r")
        error = TemporaryFile("r")
        return (readable, writeable, error)

    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_three(cmd, mode=mode)

    return _tcell_original_popen_three(cmd, bufsize, mode)

def _tcell_popen2_popen_four(_tcell_original_popen_four, cmd, bufsize=TCellDefaultFlag, mode="t"):
    if should_block_shell_command(cmd):
        from tempfile import TemporaryFile
        writeable = TemporaryFile("w")
        readable_n_error = TemporaryFile("r")
        return (readable_n_error, writeable)

    if bufsize is TCellDefaultFlag:
        return _tcell_original_popen_four(cmd, mode=mode)

    return _tcell_original_popen_four(cmd, bufsize, mode)


def instrument_os_system():
    InstrumentationManager.instrument(os, "system", _tcell_os_system)
    InstrumentationManager.instrument(os, "popen", _tcell_os_popen)

    if hasattr(os, "popen2"):
        InstrumentationManager.instrument(os, "popen2", _tcell_os_popen_two)
    if hasattr(os, "popen3"):
        InstrumentationManager.instrument(os, "popen3", _tcell_os_popen_three)
    if hasattr(os, "popen4"):
        InstrumentationManager.instrument(os, "popen4", _tcell_os_popen_four)

    InstrumentationManager.instrument(subprocess, "call", _tcell_subprocess_call)
    InstrumentationManager.instrument(subprocess, "check_output", _tcell_subprocess_check_output)


    try:
        import popen2
        InstrumentationManager.instrument(popen2, "popen2", _tcell_popen2_popen_two)
        InstrumentationManager.instrument(popen2, "popen3", _tcell_popen2_popen_three)
        InstrumentationManager.instrument(popen2, "popen4", _tcell_popen2_popen_four)
    except ImportError:
        pass


@catches_generic_exception(__name__, "Could not instrument for cmdi")
def instrument_commands():
    if 'os-commands' in get_config().disabled_instrumentation:
        logger = get_module_logger(__name__)
        if logger is not None:
            logger.info("Skipping instrumentation for OS Commands feature")
        return
    instrument_os_system()
