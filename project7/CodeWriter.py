"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    arithmetic_dict = {
        "add": "+", "sub": "-", "neg": "-",
        "eq": "=",
        "gt": "C_ARITHMETIC", "lt": "C_ARITHMETIC", "and": "C_ARITHMETIC",
        "or": "C_ARITHMETIC", "not": "C_ARITHMETIC"}

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.file = output_stream
        self.file_name = ""
        self.iteration = 0
        self.segment_dict = {"local": "LCL", "this": "THIS",
                             "that": "THAT", "pointer": "3", "temp": "5",
                             "argument": "ARG"}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename

    def add_or_sub(self, command: str) -> None:
        art_command = self.arithmetic_dict[command]
        self.file.write(
            f"@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "D=M\n" +  #D=y\
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            f"D=M{art_command}D\n" + #D = X - or + Y\
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def neg(self) -> None:
        self.file.write(
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "M=-M\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def binary(self, command: str) -> None:
        binary_dict = {"or": "|", "not": "!", "and": "&"}
        cur_cmd = binary_dict[command]
        iteration = self.iteration
        if cur_cmd == "!":
            self.file.write( "@ SP\n" + \
            "M = M - 1\n " + \
            "A = M\n" + \
            "M = !M\n" + \
            " @ SP\n" + \
            "M = M + 1\n")
        else:
            self.file.write(
                f"@SP\n" + \
                "M=M-1\n" + \
                "A=M\n" + \
                "D=M\n" #d=y + \
                "@SP\n" + \
                "M=M-1\n" + \
                "A=M\n" + \
                f"D=M{cur_cmd}D\n" + \
                "M=D\n" + \
                "@SP\n" + \
                "M=M+1\n")

    def shift(self, command: str) -> None:
        binary_dict = {"shiftright": ">>", "shiftleft": "<<"}
        cur_cmd = binary_dict[command]
        self.file.write(
            f"@SP\n" + \
            "M=M-1\n" + \
            f"@SP\n" + \
            "A=M\n" + \
            f"M=M{cur_cmd}\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def compare(self, command: str):
        branch_dict = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
        cur_cmd = branch_dict[command]
        iteration = self.iteration
        self.file.write("@SP\n" + \
                          "M=M-1\n" + \
                          f"@MAIN_BLOCK{iteration}\n" + \
                          "0;JMP\n" + \

                          # true - the condition is true
                          f"(TRUE{iteration})\n" + \
                          "@1\n" + \
                          "D=-A\n" + \
                          "@SP\n" + \
                          # "M=M-1\n" + \
                          "A=M\n" + \
                          "M=D\n" + \
                          f"@FINISH{iteration}\n" + \
                          "0;JMP\n" + \
 \
                          # false - the condition is false
                          f"(FALSE{iteration})\n" + \
                          "@0\n" + \
                          "D=A\n" + \
                          "@SP\n" + \
                          # "M=M-1\n" + \
                          "A=M\n" + \
                          "M=D\n" + \
                          f"@FINISH{iteration}\n" + \
                        "0;JMP\n" + \
 \
                        f"(MAIN_BLOCK{iteration})\n" + \
                          # check if (x>0)
                          "@SP\n" + \
                        "M = M-1\n" + \
 \
                        "A=M\n" + \
                          "D=M\n" + #d=x \
                          f"@X_POS{iteration}\n" + \
                          "D;JGT\n" + \
                          f"@X_NEG{iteration}\n" + \
                          "0;JMP\n" + \
 \
                          # x>0 -> check if y>0:
                          f"(X_POS{iteration})\n" + \
                          "@SP\n" + \
                        "M=M+1\n" + \
                        "A=M\n" + \
                          "D=M\n" + #d=y \
                          f"@SAME_SIGN{iteration}\n" + \
                          "D;JGT\n" + \
                          f"@DIFF_SIGN{iteration}\n" + \
                          "0;JMP\n" + \
 \
                          # x<0 -> check if y>0:
                          f"(X_NEG{iteration})\n" + \
                        "M=M+1\n" + \
                        "@SP\n" + \
                          "A=M  \n" + \
                          "D=M\n" + \
                          f"@DIFF_SIGN{iteration}\n" + \
                          "D;JGT\n" + \
                          f"@SAME_SIGN{iteration}\n" + \
                          "0;JMP\n" + \
 \
                          # if (x>0 and y>0 or x<0 and y<0)
                          f"(SAME_SIGN{iteration})\n" + \
                          "@SP\n" + \
                        "M=M-1\n" + \
                        "A=M\n" + \
                          "D=M\n" + #d=x \
                          "@SP\n" + \
                          "M=M+1\n" + \
                          "A=M\n" + \
                          "D=D-M\n" + #d=x-y\
                        "@SP\n" + \
                        "M=M-1\n" + \
                        f"@TRUE{iteration}\n" + \
                          f"D;{cur_cmd}\n" + \
                          f"@FALSE{iteration}\n" + \
                          "0;JMP\n" + \

                          # if (x>0 and y<0) or (x<0 and y>0)
                          f"(DIFF_SIGN{iteration})\n" + \
                          "@SP\n" + \
                        "M = M-1\n" + \
                          "A=M\n" + \
                          "D=M\n" + \
                          f"@TRUE{iteration}\n" + \
                          f"D;{cur_cmd}\n" + \
                          f"@FALSE{iteration}\n" + \
                          "0;JMP\n" + \
 \
                          f"(FINISH{iteration})\n"
                          "@SP\n" + \
                          "M=M+1\n")
        self.iteration += 1

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.
        Args:
            command (str): an arithmetic command.
        """
        if command == "add" or command == "sub":
            self.add_or_sub(command)
        elif command == "neg":
            self.neg()
        elif command == "gt" or command == "lt" or command == "eq":
            self.compare(command)
        elif command == "shiftleft" or command == "shiftright":
            self.shift(command)

        else:
            self.binary(command)

    ###push funcs

    def push_constant(self, index: int) -> None:
        self.file.write(
            # "@SP\n" + \
            f"@{index}\n" + \
            # "M=A\n" + \
            "D=A\n" + \
            "@SP\n" + \
            "A=M\n" + \
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n"
        )

    def push_heap(self, index: int, segment: str) -> None:
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=M\n" + \
            f"@{index}\n" + \
            # "M=A\n" + \
            "A=D+A\n" + #todo \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n" + #todo
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def push_p(self, index: int, segment: str) -> None:
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=A\n" + \
            f"@{index}\n" + \
            # "A = M\n" + #TODO: CHECK \
            "A=D+A\n" + \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n" + #todo \
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def push_static(self, index: int) -> None:
        file_name = self.file_name
        self.file.write(
            f"@{file_name}.{index}\n" + \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n"+ #todo
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    ###pop funcs

    def pop_heap(self, index: int, segment: str) -> None:
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=M\n" + \
            f"@{index}\n" + \
            "D=D+A\n" + \
            "@R13\n" + \
            "M=D\n" + \
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "D=M\n" + \
            "@R13\n" + \
            "A=M\n" + \
            "M=D\n")

    def pop_p(self, index: int, segment: str) -> None:
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=A\n" + \
            f"@{index}\n" + \
            # "M=A\n" + \
            "D=D+A\n" #todo + \
            "@R13\n"
            "M=D\n"
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "D=M\n" + \
            "@R13\n" + \
            "A=M\n" + \
            "M=D\n")

    def pop_static(self, index: int) -> None:
        file_name = self.file_name
        self.file.write(
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "D=M\n" + \
            f"@{file_name}.{index}\n" + \
            "M=D\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            if segment == "constant":
                self.push_constant(index)

            elif segment in {"argument", "local", "this",
                             "that"}:
                self.push_heap(index, segment)

            elif segment in {"pointer", "temp"}:
                self.push_p(index, segment)

            elif segment == "static":
                self.push_static(index)


        else:  # command == "C_POP"
            if segment in {"argument", "local", "this",
                                 "that"}:
                self.pop_heap(index, segment)

            elif segment in {"pointer", "temp"}:
                self.pop_p(index, segment)

            elif segment == "static":
                self.pop_static(index)

    def close(self) -> None:
        """Closes the output file."""
        self.file.close()