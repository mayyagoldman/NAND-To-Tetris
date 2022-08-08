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
        n_line = line.replace(" ", "")
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
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    commands = {1: "A_COMMAND", 2: "C_COMMAND", 3: "L_COMMAND", 4: "S_C_COMMAND"}

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.processed_input = clean_file(input_file)
        self.num_commands = len(self.processed_input)
        self.commands_read = 0
        self.curr_command = ""
        self.curr_type = -1

    def reset_parser(self):
        self.commands_read = 0
        self.curr_command = ""
        self.curr_type = -1

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?


        Returns:
            bool: True if there are more commands, False otherwise.
        """

        return self.num_commands != self.commands_read

    def determine_command_type(self):
        if self.curr_command[0] == "@":
            return 1
        if self.curr_command[0] == "(" and self.curr_command[-1] == ")":
            return 3
        if ">>" in self.curr_command or "<<" in self.curr_command:
            return 4
        else:
            return 2

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.curr_command = self.processed_input[self.commands_read]
            self.curr_type = self.determine_command_type()
            self.commands_read += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """

        return self.commands[self.curr_type]

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.curr_type == 1:
            return self.curr_command[1:]

        if self.curr_type == 3:
            return self.curr_command[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """

        if self.curr_type == 2 or self.curr_type == 4:
            for i in range(len(self.curr_command)):
                if self.curr_command[i] == "=":
                    return self.curr_command[:i]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """

        if self.curr_type == 2 or self.curr_type == 4:
            starting_idx = 0
            finish_idx = len(self.curr_command)
            for i in range(len(self.curr_command) - 1):
                if self.curr_command[i] == "=":
                    starting_idx = i + 1
                elif self.curr_command[i] == ";":
                    finish_idx = i
            return self.curr_command[starting_idx: finish_idx]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.curr_type == 2 or self.curr_type == 4:
            for i in range(len(self.curr_command)):
                if self.curr_command[i] == ";":
                    return self.curr_command[i + 1:]
