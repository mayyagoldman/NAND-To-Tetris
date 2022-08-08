"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


def clean_file(input_file: typing.TextIO):
    processed_input = []
    input_lines = input_file.read().splitlines()
    for line in input_lines:
        n_line = line.strip()
        if n_line.startswith("//") or n_line == "":
            continue
        else:
            for i in range(len(n_line) - 1):
                if n_line[i:i + 2] == "//":
                    n_line = n_line[0:i]
                    break

            processed_input.append(n_line)

    return processed_input


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    commands = {"C_ARITHMETIC", "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION", "C_RETURN", "C_CALL"}
    commands_dict = {"push": "C_PUSH", "pop": "C_POP", "label": "C_LABEL", "goto": "C_GOTO",
                     "if-goto": "C_IF", "function": "C_FUNCTION", "return": "C_RETURN", "call": "C_CALL",
                     "add": "C_ARITHMETIC", "sub": "C_ARITHMETIC", "neg": "C_ARITHMETIC", "eq": "C_ARITHMETIC",
                     "gt": "C_ARITHMETIC", "lt": "C_ARITHMETIC", "and": "C_ARITHMETIC",
                     "or": "C_ARITHMETIC", "not": "C_ARITHMETIC" , "shiftleft" : "C_ARITHMETIC"  , "shiftright" : "C_ARITHMETIC"}

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """

        self.processed_input = clean_file(input_file)
        self.num_commands = len(self.processed_input)
        self.commands_read = 0
        self.curr_command = ""
        self.curr_type = ""

    def reset_parser(self):
        self.commands_read = 0
        self.curr_command = ""
        self.curr_type = ""

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.num_commands != self.commands_read

    def determine_command_type(self) -> str:
        command = self.curr_command.split()[0]
        return self.commands_dict[command]

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.curr_command = self.processed_input[self.commands_read]
            self.curr_type = self.determine_command_type()
            self.commands_read += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        return self.curr_type

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.curr_type == "C_RETURN":
            return ""
        if self.curr_type == "C_ARITHMETIC":
            return self.curr_command.split()[0]
        return self.curr_command.split()[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """

        if self.curr_type == "C_PUSH" or self.curr_type == "C_POP" or self.curr_type == "C_FUNCTION" \
                or self.curr_type == "C_CALL":
            return int(self.curr_command.split()[2])



