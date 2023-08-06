import unittest
import pytest
import sys

from mock import Mock, patch
from functools import partial

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.cmdi import should_block_shell_command, get_tcell_context
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation import cmdi
from tcell_agent.utils.compat import PY2

class CmdiTest(unittest.TestCase):
    def test_django_no_request_get_tcell_context(self):
        with patch("tcell_agent.instrumentation.utils.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=None) as patched_get_current_request:
                tcell_context = get_tcell_context()

                self.assertIsNone(tcell_context)
                self.assertTrue(patched_get_current_request.called)
                self.assertTrue(patched_django_active.called)

    def test_django_with_tcell_context_get_tcell_context(self):
        context = TCellInstrumentationContext()
        request = Mock(_tcell_context=context)

        with patch("tcell_agent.instrumentation.utils.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=request) as patched_get_current_request:
                tcell_context = get_tcell_context()

                self.assertEqual(tcell_context, context)
                self.assertTrue(patched_get_current_request.called)
                self.assertTrue(patched_django_active.called)

    def test_none_command_should_block_shell_command(self):
        with patch("tcell_agent.instrumentation.utils.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=None) as patched_get_current_request:
                # assertFalse returns true if it's None which is not the same test
                self.assertEqual(should_block_shell_command(None), False)
                self.assertFalse(patched_django_active.called)
                self.assertFalse(patched_get_current_request.called)

    def test_bytes_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(b"cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with(b"cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_unicode_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(u"cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with(u"cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_string_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command("cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_tuple_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(("cat", "passwd", "|", "grep", "root",))
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_list_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(["cat", "passwd", "|", "grep", "root"])
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)


@pytest.mark.usefixtures('disable_block')
class OsSystemTests(unittest.TestCase):
    def setUp(self):
        import os
        self._wrapper = partial(cmdi._tcell_os_system, os.system)

    def test_command_is_not_blocked(self):
        assert self._wrapper("echo test") == 0

    def test_command_is_blocked(self):
        self.block.return_value = True
        assert self._wrapper("echo test") == 1
        self.block.assert_called_once_with("echo test")


class OsPopenTests:
    def partials():
        import os
        return [partial(cmdi._tcell_os_popen, os.popen),
                partial(os.popen)]


    @pytest.mark.parametrize('wrapper', partials())
    @pytest.mark.parametrize('command,result', [("echo test", "test\n")])
    @pytest.mark.usefixtures('disable_block')
    class OsPopenTests:
        def test_command_is_not_blocked(self, wrapper, command, result):
            assert wrapper(command).read() == result

        def test_wrapper_accepts_args(self, wrapper, command, result):
            assert wrapper(command, 'r').read() == result
            assert wrapper(command, 'r', 2).read() == result

            with pytest.raises(Exception):
                assert wrapper(command, 'w').read() == result

        @pytest.mark.skipif(PY2, reason="Requires Python 3")
        def test_wrapper_accepts_kwargs(self, wrapper, command, result):
            assert wrapper(command, mode='r').read() == result
            assert wrapper(command, mode='r', buffering=2).read() == result

        @pytest.mark.skipif(not PY2, reason="Requires Python 2")
        def test_wrapper_rejects_kwargs(self, wrapper, command, result):
            with pytest.raises(TypeError):
                assert wrapper(command, mode='r')
                assert wrapper(command, bufsize='r')

        def test_command_is_blocked(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            self.block.return_value = True
            assert wrapper(command).read() == ""

        def test_block_function_called_with_args(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            wrapper(command)
            self.block.assert_called_once_with(command)


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
class Popen2Tests:
    def partials():
        if not PY2:
            return []

        import popen2, os
        return [partial(cmdi._tcell_popen2_popen_two, popen2.popen2),
                partial(cmdi._tcell_popen2_popen_three, popen2.popen3),
                partial(cmdi._tcell_popen2_popen_four, popen2.popen4),
                partial(popen2.popen2),
                partial(popen2.popen3),
                partial(popen2.popen4),
                partial(cmdi._tcell_os_popen_two, os.popen2),
                partial(cmdi._tcell_os_popen_three, os.popen3),
                partial(cmdi._tcell_os_popen_four, os.popen4),
                partial(os.popen2),
                partial(os.popen3),
                partial(os.popen4)]


    @pytest.mark.parametrize('wrapper', partials())
    @pytest.mark.parametrize('command,result', [("echo test", "test\n"), (["echo", "test", " test"], "test  test\n")])
    @pytest.mark.usefixtures('disable_block')
    class Popen2Tests:
        """ This class tests methods Popen methods from popen2 and os module. """
        def read_index(self, wrapper):
            """ popen2 methods, including tcell popen2 methods, will return
                a tuple, where the index 0 is for read. """
            if wrapper.func.__module__ == 'popen2' or \
               wrapper.func.__name__ in ['_tcell_popen2_popen_two', '_tcell_popen2_popen_three', '_tcell_popen2_popen_four']:
                return 0

            return 1


        def write_index(self, wrapper):
            """ popen2 methods, including tcell popen2 methods, will return
                a tuple, where the index 1 is for write. """
            if wrapper.func.__module__ == 'popen2' or \
               wrapper.func.__name__ in ['_tcell_popen2_popen_two', '_tcell_popen2_popen_three', '_tcell_popen2_popen_four']:
                return 1

            return 0


        def test_command_is_not_blocked(self, wrapper, command, result):
            stdout = self.read_index(wrapper)
            assert wrapper(command)[stdout].read() == result

        def test_stdin_command_is_not_blocked(self, wrapper, command, result):
            stdin = self.write_index(wrapper)
            stdout = self.read_index(wrapper)

            pipes = list(wrapper("cat"))

            pipes[stdin].write("testing1")
            pipes[stdin].write("testing2")
            pipes[stdin].write("testing3")

            pipes[stdin].close()
            assert pipes[stdout].read() == "testing1testing2testing3"

        def test_wrapper_accepts_args(self, wrapper, command, result):
            stdout = self.read_index(wrapper)

            # This test class also tests the os module, which uses a different ordering of arguments
            if ('popen2' in wrapper.func.__module__ or 'tcell_popen2' in wrapper.func.__name__):
                assert wrapper(command, 2, 't')[stdout].read() == result
            else:
                assert wrapper(command, 't', 2)[stdout].read() == result

        def test_wrapper_accepts_kwargs(self, wrapper, command, result):
            stdin = self.read_index(wrapper)

            assert wrapper(command, mode='t')[stdin].read() == result
            assert wrapper(command, mode='t', bufsize=2)[stdin].read() == result

        def test_command_is_blocked(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            self.block.return_value = True
            stdout = self.read_index(wrapper)

            assert wrapper(command)[stdout].read() == ""

        def test_block_function_called_with_args(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            wrapper(command)
            self.block.assert_called_once_with(command)


class SubprocessCallTests:
    def partials():
        import subprocess
        return [partial(cmdi._tcell_subprocess_call, subprocess.call),
                partial(subprocess.call)]


    @pytest.mark.parametrize('wrapper', partials())
    @pytest.mark.parametrize('command,result', [("echo", "\n",), (["echo", "test"], "test\n")])
    @pytest.mark.usefixtures('disable_block')
    class SubprocessCallTests:
        def test_command_is_not_blocked(self, wrapper, command, result):
            assert wrapper(command) == 0

        @pytest.mark.parametrize('args', [[1], [1, None], [1, None, None, None, None, None, None]])
        def test_wrapper_accepts_args(self, wrapper, command, result, args):
            from tempfile import TemporaryFile
            stdout = TemporaryFile('r+')
            kwargs = {}

            if len(args) < 3:
                kwargs['stdout'] = stdout
            else:
                args[3] = stdout

            wrapper(command, *args, **kwargs)
            stdout.seek(0)

            assert stdout.read() == result

        def test_wrapper_accepts_kwargs(self, wrapper, command, result):
            from tempfile import TemporaryFile
            stdout = TemporaryFile('r+')
            stderr = TemporaryFile('r+')

            wrapper(command, shell=True, stdout=stdout, stderr=stderr)
            stdout.seek(0)
            assert stdout.read() == "\n"

        def test_command_is_blocked(self, wrapper, command, result):
            from tempfile import TemporaryFile

            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            self.block.return_value = True

            assert wrapper(command) == 1

        def test_block_function_called_with_args(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            wrapper(command)
            self.block.assert_called_once_with(command)


class SubprocessCheckoutputTests():
    def partials():
        import subprocess
        return [partial(cmdi._tcell_subprocess_check_output, subprocess.check_output),
                partial(subprocess.check_output)]


    @pytest.mark.parametrize('wrapper', partials())
    @pytest.mark.parametrize('command,result', [("echo", b"\n",), (["echo", "test"], b"test\n")])
    @pytest.mark.usefixtures('disable_block')
    class SubprocessCheckoutputTests:
        def test_command_is_not_blocked(self, wrapper, command, result):
            assert wrapper(command) == result

        @pytest.mark.parametrize('args', [[1], [1, None], [1, None, None]])
        def test_wrapper_accepts_args(self, wrapper, command, result, args):
            assert wrapper(command, *args) == result

        def test_wrapper_accepts_kwargs(self, wrapper, command, result):
            from tempfile import TemporaryFile
            stderr = TemporaryFile('r+')

            assert wrapper(command, shell=True, stderr=stderr) == b"\n"
            assert wrapper(command, stderr=stderr, shell=True, ) == b"\n"

            if sys.version_info[0] == 2 or (sys.version_info[0] == 3 and sys.version_info[1] <= 5):
                pytest.skip('Remaining asserts are Python < 3.5 only.')

            assert wrapper(command, stderr=stderr, shell=True, errors=None) == b"\n"
            assert wrapper(command, stderr=stderr, shell=True, encoding=None) == b"\n"

        def test_command_is_blocked(self, wrapper, command, result):
            from tempfile import TemporaryFile

            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            self.block.return_value = True

            import subprocess
            with pytest.raises(subprocess.CalledProcessError):
                wrapper(command)

        def test_block_function_called_with_args(self, wrapper, command, result):
            if 'tcell' not in wrapper.func.__name__:
                pytest.skip('Test not applicable to non-instrumented functions.')

            wrapper(command)
            self.block.assert_called_once_with(command)
