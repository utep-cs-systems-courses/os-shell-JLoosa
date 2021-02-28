#!/usr/bin/python3.6

"""
    @author Jacob Loosa
    Date Modified: 20 February 2021
"""

import sys as system
import re as regex
import os

# Used for type hinting. Does not impact functionality
# I use this as I am a fan of typed languages. In a way, this is closer to C as C uses typing.
from typing import ByteString, Optional, List

_ENCODING = "utf-8"


def print_debug(message: str):
    print("[Debug]", message)


class MyReadLine:

    def __init__(self, file_descriptor: int):
        # File Descriptor Information
        self._file_descriptor: int = file_descriptor
        # Pre-String Information1
        self._last_input: Optional[bytes] = None
        # String Information
        self._line_buffer: List[str] = list()
        self._line_builder: Optional[str] = None
        self._last_output: Optional[str] = None
        self._current_line_number: int = 0

    def _read(self, num_bytes: int = 10000) -> ByteString:
        self._last_input = os.read(self._file_descriptor, num_bytes)
        return self._last_input

    def _read_line(self) -> Optional[str]:
        # Check if we have a line in the buffer before reading more. Lists in python act as a queue, so we can use pop
        if self._line_buffer:
            return self._line_buffer.pop()
        # The list was empty, so we will do a read and repopulate it
        self._read()  # Result is stored in self.last_input and returned, so assignment to a variable here is optional
        # Return nothing if end-of-file
        if len(self._last_input) == 0:
            return None

        for index in range(len(self._last_input)):
            current_char = chr(self._last_input[index])
            if current_char == '\n':
                self._line_buffer.append(self._line_builder)
                self._line_builder = None
            else:
                if self._line_builder is None:
                    self._line_builder = current_char
                else:
                    self._line_builder += current_char
        self._last_input = None

    def read_line(self) -> Optional[str]:
        self._last_output = self._read_line()
        if self._last_output:
            self._current_line_number += 1
        return self._last_output

    def repeat_line(self) -> Optional[str]:
        return self._last_output

    def get_current_line_number(self) -> int:
        return self._current_line_number


class MyShell0:

    # By default, file descriptors 0 and 1 are standard input and output, respectively
    def __init__(self, file_descriptor_in: int = 0, file_descriptor_out: int = 1):
        self._file_descriptor_in: int = file_descriptor_in
        self._file_descriptor_out: int = file_descriptor_out
        self._line_reader: MyReadLine = MyReadLine(self._file_descriptor_in)
        self._shell_running = True
        self.write_str("Shell Created.\n")

    def _write_bytes(self, bytes_output: bytes) -> None:
        if bytes_output is None:
            return
        os.write(self._file_descriptor_out, bytes_output)

    def write_str(self, str_output: str) -> None:
        if str_output is None:
            return
        self._write_bytes(str_output.encode(_ENCODING))

    def next_line(self, reject_blank_inputs: bool = False) -> Optional[str]:
        next_line: Optional[str] = self._line_reader.read_line()
        # Blocks until an input is provided by the user. Ignores empty lines
        while next_line is None and reject_blank_inputs:
            next_line = self._line_reader.read_line()
        return next_line

    def current_line(self) -> Optional[str]:
        return self._line_reader.repeat_line()

    def loop(self):
        _ps1 = os.environ["PS1"] if "PS1" in os.environ else "> "
        while self._shell_running:
            self.write_str(_ps1)
            _result = self.next_line(True)
            if _result == "exit":
                self._shell_running = False
                self.write_str("Shell exiting.")
                system.exit(0)

            _fork_rc = os.fork()

            if _fork_rc < 0:
                self.write_str("Fork failed with code %d\n" % _fork_rc)
            elif _fork_rc == 0:
                args = _result.split()
                for directory in regex.split(":", os.environ['PATH']):  # try each directory in the path
                    program = "%s/%s" % (directory, args[0])
                    try:
                        os.execve(program, args, os.environ)  # try to exec program
                    except FileNotFoundError:  # ...expected
                        pass  # ...fail quietly
                os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                system.exit(1)  # terminate with error
            else:
                self.write_str("Child process created with PID %d\n" % _fork_rc)
                os.wait()


if __name__ == '__main__':
    shell: MyShell0 = MyShell0()
    shell.loop()
