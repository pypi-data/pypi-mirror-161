#!/bin/false
# -*- coding: utf-8 -*-

""" Tools to simplify spawning child processes and capturing, logging, or processing output. """


# =======================================================================================================================
# Main imports
# =======================================================================================================================
import os
import subprocess
import threading
import shlex
import time
import datetime
from enum import Enum
from typing import Any, Callable, Dict, Generator, IO, List, Optional, Tuple, Union
from queue import Queue, Empty
from ptutils.time import dt, now
from ptutils.typing import is_string


# ------------------------------------------------------------------------------------------------------------------------
# Logging config
# ------------------------------------------------------------------------------------------------------------------------
from ptutils.logging import getLogger
logger = getLogger(__name__)


# =======================================================================================================================
# Globals
# =======================================================================================================================
""" Environment variables that are copied by default to child `Program` environments. """
__COPIED_ENV_ARGNAMES__ = [
    'LANG', 'LANGUAGE', 'LC_ALL',
    'DISPLAY', 'LS_COLORS',
    'HOST_TYPE',
    'USER', 'HOME', 'NAME', 'SHELL',
    'DOCKER_HOST', 'TERM', 'PATH'
]


# =======================================================================================================================
# Class: Program
# =======================================================================================================================
class Program(object):  # pragma: no cover
    """ A child process. """

    # --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def run(
        args,
        cwd:             Optional[str]            = None,
        capture:         bool                     = True,
        display:         bool                     = True,
        raise_on_error:  bool                     = False,
        env:             Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float]          = None,
        silent:          bool                     = True
    ) -> Union[int, Tuple[int, List[str], List[str]] ]:
        """
        Convenience method to run a child process synchronously and await the result.

        Parameters
        ----------
        args : Union[str, List[str]]
            A list of program invocation arguments, or a string of such arguments separated by
            spaces. If providing a string, be aware that arguments containing spaces won't be
            handled appropriately and will be split into multiple arguments.
        cwd : Optional[str], optional
            When specified, change the current directory to the path provided, by default None
        capture : bool, optional
            When True, capture standard output and error streams of the child program. By default True
        display : bool, optional
            When True, log the standard output and error streams of the child program. By default True
        raise_on_error : bool, optional
            Raise an exception when the child process returns a return code other than 0, by default False
        env : Optional[Dict[str, Any]], optional
            A dictionary of environment arguments for the child program, by default None.
            When omitted, the child process inherits the parent environment as per
            `subprocess.Popen`.
            When present and `copy_shell_env` is True, the child environment will be the result
            of merging the supplied environment with a selected subset of the current process's
            environment. See `__COPIED_ENV_ARGNAMES__` to see what gets copied.
        timeout_seconds : float, optional
            When specified, kill the child process with SIGTERM if it hasn't completed in the
            specified number of seconds, by default None
        silent : bool, optional
            When true, disable logging about child process start/stop, except in the case of
            errors, by default True

        Returns
        -------
        Union[int, Tuple[int, List[str], List[str]] ]
            If `capture` is True, this will be a tuple of (return code, standard output line, standard error lines).
            If `capture` is False, this will be a just the return code.
        """
        if is_string(args):
            args = args.split(' ')
        p = Program(
            args,
            cwd             = cwd,
            capture_stdout  = capture,
            capture_stderr  = capture,
            display_stderr  = display,
            display_stdout  = display,
            silent          = silent,
            env             = env,
            timeout_seconds = timeout_seconds
        )
        p.start()
        rc = p.wait()
        if raise_on_error:
            if rc != 0:
                raise subprocess.CalledProcessError(rc, str(p), p.stdout, p.stderr)

        if capture:
            return (rc, p.stdout_lines, p.stderr_lines)
        else:
            return rc

    # --------------------------------------------------------------------------------------------------------------------
    class Channel(Enum):
        """ Identifies the output stream of a child processes. """

        """ The standard output stream. """
        STDOUT = 0

        """ The standard error stream. """
        STDERR = 1

    # --------------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """
        String representation of the program invocation.

        Returns
        -------
        str
            [description]
        """
        return ' '.join([shlex.quote(arg) for arg in self.args])

    # --------------------------------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        String representation of the program invocation.

        Returns
        -------
        str
            A terse string representation.
        """
        return "Program(%s)" % self

    # --------------------------------------------------------------------------------------------------------------------
    def __init__(
            self,
            args:            Union[str, List[str]],
            capture_stdout:  bool                                                        = True,
            capture_stderr:  bool                                                        = True,
            display_stdout:  bool                                                        = True,
            display_stderr:  bool                                                        = True,
            timeout_seconds: float                                                       = None,
            listener:        Optional[Callable[[Channel, str, datetime.datetime], None]] = None,
            env:             Optional[Dict[str, Any]]                                    = None,
            log_prefix:      Optional[str]                                               = None,
            silent:          bool                                                        = True,
            copy_shell_env:  bool                                                        = True,
            cwd:             Optional[str]                                               = None
    ):
        """
        A child process runner that captures and or logs outputs.

        Parameters
        ----------
        args : Union[str, List[str]]
            A list of program invocation arguments, or a string of such arguments separated by
            spaces. If providing a string, be aware that arguments containing spaces won't be
            handled appropriately and will be split into multiple arguments.
        capture_stdout : bool, optional
            When True, capture standard output stream of the child program. By default True
        capture_stderr : bool, optional
            When True, capture standard error stream of the child program. By default True
        display_stdout : bool, optional
            When True, log the standard output stream of the child program. By default True
        display_stderr : bool, optional
            When True, log the standard error stream of the child program. By default True
        timeout_seconds : float, optional
            When specified, kill the child process with SIGTERM if it hasn't completed in the
            specified number of seconds, by default None
        listener : Optional[Callable[[Channel, str, datetime.datetime], None]], optional
            A handler which, when specified, will be called with the channel, line content, and
            timestamp of each line of standard output or error streams of the child program,
            by default None
        env : Optional[Dict[str, Any]], optional
            A dictionary of environment arguments for the child program, by default None.
            When omitted, the child process inherits the parent environment as per
            `subprocess.Popen`.
            When present and `copy_shell_env` is True, the child environment will be the result
            of merging the supplied environment with a selected subset of the current process's
            environment. See `__COPIED_ENV_ARGNAMES__` to see what gets copied.
        log_prefix : Optional[str], optional
            An opptional line prefix for child log entries when logging child output, by
            default None
        silent : bool, optional
            When true, disable logging about child process start/stop, except in the case of
            errors, by default True
        copy_shell_env : bool, optional
            When specified and `env` is also provided, first copy a subset of the current
            environment and then update the child's environment with supplied entries in `env`,
            by default True. See `__COPIED_ENV_ARGNAMES__` to see what gets copied.
        cwd : Optional[str], optional
            When specified, change the current directory to the path provided, by default None
        """
        if is_string(args):
            args = args.split(' ')
        self.args             = [str(arg) for arg in args]
        self.capture_stdout   = capture_stdout
        self.capture_stderr   = capture_stderr
        self.display_stdout   = display_stdout
        self.display_stderr   = display_stderr
        self.timeout          = timeout_seconds
        self.listener         = listener
        self.env              = env
        self.log_prefix       = log_prefix
        self.silent           = silent
        self.cwd              = cwd

        self._proc            = None
        self._return_code     = None
        self._output          = []
        self._stopped         = threading.Event()
        self._stderr_thread   = None
        self._stdout_thread   = None
        self._handler_thread  = None
        self._watchdog_thread = None
        self._queue           = Queue()
        self._T_start         = None
        self.timed_out        = threading.Event()

        if (env is not None) and copy_shell_env:
            for k in __COPIED_ENV_ARGNAMES__:
                v = os.environ.get(k, None)
                if v is not None:
                    env[k] = v

    # --------------------------------------------------------------------------------------------------------------------
    def _watchdog(self) -> None:
        """
            Watchdog thread to kill the process if it runs longer than `self.timeout`.
        """
        if self.timeout is not None:
            while self._proc.poll() is None:
                t_now   = now()
                elapsed = dt(self._T_start, t_now)
                if elapsed > self.timeout:
                    logger.warning("Program failed to complete in %s seconds." % self.timeout)
                    self.timed_out.set()
                    self.terminate()
                    while self._proc.poll() is None:
                        time.sleep(0.01)
                else:
                    time.sleep(0.01)

    # --------------------------------------------------------------------------------------------------------------------
    def _pipe_reader(
        self,
        queue: Queue,
        pipe: IO[bytes],
        channel: Channel,
        capture: bool,
        display: bool
    ) -> None:
        """
        Generic thread to read froma pipe and insert into an inbox queue.
        This thread will automatically shutdown when the pipe is closed.

        Parameters
        ----------
        queue : Queue
            The queue into which to place the log entries.
        pipe : IO[bytes]
            The pipe to read from.
        channel : Channel
            The channel that the input pipe corresponds to.
        capture : bool
            Flag indicating that `channel` is configured to be captured.
        display : bool
            Flag indicating that `channel` is configured to be displayed.
        """
        try:
            with pipe:
                for line in iter(pipe.readline, b''):
                    queue.put(
                        (channel, capture, display, line, now())
                    )
        finally:
            queue.put(
                (channel, capture, display, None, now())
            )

    # --------------------------------------------------------------------------------------------------------------------
    def _handler(self, queue: Queue, stopped: threading.Event) -> None:
        """
        Output stream processing handler.
        Handles logging, capture, and dispatch to any custom handler.

        Parameters
        ----------
        queue : Queue
            The queue on which to receive stream output records
        stopped : threading.Event
            An event used to signal processing should be stopped.
        """
        prefix = (self.log_prefix + ' ') if self.log_prefix else ''
        while not stopped.is_set():
            try:
                (channel, capture, display, line, timestamp) = queue.get_nowait()
                if line is not None:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8').rstrip()
                    if capture:
                        self._output.append((channel, line, timestamp))
                    if display:
                        logger.info( prefix + line )
                    if self.listener:
                        try:
                            self.listener(channel, line, timestamp)
                        except Exception:  # pylint: disable=broad-except
                            logger.exception("⚠️ Error during user-supplied message handler. (IGNORED)")
                queue.task_done()

            except Empty:
                time.sleep(0.05)

            except Exception:  # pylint: disable=broad-except
                logger.exception("🐞 Error processing program output")

    # --------------------------------------------------------------------------------------------------------------------
    def start(self) -> None:
        """
        Start the child program.
        """
        if not self.silent:
            msg = f"Starting program: {self}"
            if self.env:
                msg += f"\n environment = {self.env}"
            logger.info(msg)

        self._T_start = now()

        # start the process
        self._proc = subprocess.Popen(
            self.args,
            stdout             = subprocess.PIPE,
            stderr             = subprocess.PIPE,
            bufsize            = 0,
            close_fds          = False,
            env                = self.env,
            universal_newlines = False,
            cwd                = self.cwd
            # ,
            # encoding           = 'utf-8'
        )

        # start the watchdog thread if required
        if self.timeout:
            self._watchdog_thread = threading.Thread( target=self._watchdog )
            self._watchdog_thread.start()

        # start the handler thread
        self._handler_thread = threading.Thread(
            target = self._handler,
            args   = [
                self._queue,
                self._stopped
            ]
        )
        self._handler_thread.start()

        # start the reader threads
        self._stdout_thread  = threading.Thread(
            target = self._pipe_reader,
            args   = [
                self._queue,
                self._proc.stdout,
                Program.Channel.STDOUT,
                self.capture_stdout,
                self.display_stdout
            ]
        )
        self._stdout_thread.start()

        self._stderr_thread  = threading.Thread(
            target = self._pipe_reader,
            args   = [
                self._queue,
                self._proc.stderr,
                Program.Channel.STDERR,
                self.capture_stderr,
                self.display_stderr
            ]
        )
        self._stderr_thread.start()

    # --------------------------------------------------------------------------------------------------------------------
    def wait(self) -> int:
        """
        Wait for the child program to complete and return it's return code.

        Returns
        -------
        int
            The child program's return code.
        """
        # wait for readers to see EOF
        self._stdout_thread.join()
        self._stderr_thread.join()
        self._queue.join()
        self._stopped.set()
        self._handler_thread.join()
        if self.timeout:
            self._watchdog_thread.join()
        self._return_code = self._proc.wait()
        if not self.silent:
            logger.info("Program completed: %s --> %s" % (self, self._return_code))
        return self._return_code

    # --------------------------------------------------------------------------------------------------------------------
    def send_signal(self, sig: int) -> None:
        """
        Send a signal to the child process.

        Parameters
        ----------
        sig : int
            The signal to send.
        """
        if not self.silent:
            logger.info("Terminating program: %s with signal %s" % (self, sig))
        self._proc.send_signal(sig)

    # --------------------------------------------------------------------------------------------------------------------
    def terminate(self) -> None:
        """
        Terminate the child process by sending SIGTERM
        """
        if not self.silent:
            logger.info("Terminating program: %s" % self)
        self._proc.terminate()

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def return_code(self) -> Optional[int]:
        """
        The program's return code, or return None if the program is still running.

        Returns
        -------
        Optional[int]
            The return code.
        """
        if self._return_code is None:
            self._return_code = self._proc.poll()
        return self._return_code

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def is_finished(self) -> bool:
        """
        Test if the child program has completed.

        Returns
        -------
        bool
            True if the child program is still running, False otherwise.
        """
        return self.return_code is not None

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def records(self) -> Generator[Tuple[Channel, str, datetime.datetime], None, None]:
        """
        Captured output records from either of the child program's streams.

        Yields
        -------
        Tuple[Channel, str, datetime.datetime]
            A record for each line captured from the child process as a tuple (channel, line, timestamp).
        """
        for x in self._output:
            yield x

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def lines(self) -> Generator[str, None, None]:
        """
        Captured output lines from either of the child program's streams.
        Generator yielding individual output lines from either channel of the child.

        Yields
        -------
        str
            A line for each captured line on either stream of the child program.
        """
        for (_, line, __) in self._output:
            yield line

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def stdout_lines(self) -> Generator[str, None, None]:
        """
        Captured output lines from the child program's standard output stream.

        Yields
        -------
        str
            A line for each captured line on the child program's standard output stream.
        """
        for (channel, line, _) in self._output:
            if channel == Program.Channel.STDOUT:
                yield line

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def stderr_lines(self) -> Generator[str, None, None]:
        """
        Captured output lines from the child program's standard error stream.

        Yields
        -------
        str
            A line for each captured line on the child program's standard error stream.
        """
        for (channel, line, _) in self._output:
            if channel == Program.Channel.STDERR:
                yield line

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def output(self) -> str:
        """
        The combined output of the child process as a linux newline-terminated block of text.

        Returns
        -------
        str
            The combined output.
        """
        return '\n'.join(self.lines)

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def stdout(self) -> str:
        """
        The output of the child process's standard output stream as a linux newline-terminated block of text.

        Returns
        -------
        str
            The output.
        """
        return '\n'.join(self.stdout_lines)

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def stderr(self) -> str:
        """
        The output of the child process's standard error stream as a linux newline-terminated block of text.

        Returns
        -------
        str
            The output.
        """
        return '\n'.join(self.stderr_lines)
