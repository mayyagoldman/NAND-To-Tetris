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
    #  arithmetic_dict classifies a string to the proper command.
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
        self.iteration = 0  # counts the commands being translated.
        self.segment_dict = {"local": "LCL", "this": "THIS",
                             "that": "THAT", "pointer": "3", "temp": "5",
                             "argument": "ARG"}
        self.cur_func = ""

    def writeInit(self):
        """
        Writes the assembly code that effects the
        VM initialization (also called bootstrap
        code). This code should be placed in the
        ROM beginning in address 0x0000.
        """
        code = "@256\n" + "D=A\n" + "@SP\n" + "M=D\n"
        self.file.write(code)
        self.cur_func = "Sys.init"
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label: str):
        """
        Writes the assembly code that is the
        translation of the given label command.
        """
        cur_label = "(" + self.cur_func + "." + label + ")"
        code = "//write label\n" + f"{cur_label}\n"
        self.file.write(code)

    def WriteIf(self, label: str):
        """
        Writes the assembly code that is the
        translation of the given if-goto command.
        """
        cur_label = self.cur_func + "." + label
        code = "//write if\n" + "@SP\n" + "M=M-1\n" + "A=M\n"
        code += "D=M\n" + f"@{cur_label}\n" + "D;JNE\n"
        self.file.write(code)

    def writeGoto(self, label: str):
        """
        Writes the assembly code that is the
        translation of the given goto command.
        """
        cur_label = "@" + self.cur_func + "." + label
        self.file.write(
            "//GO_TO\n" + f"{cur_label}\n" + "0;JMP\n")

    def push_return_address_to_stck(self, item: str):
        code = f"@{item}\n" + "D=A\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" \
               + "M=M+1\n"
        return code

    def push_to_stck(self, item: str):
        code = f"@{item}\n" + "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" \
               + "M=M+1\n"
        return code

    def writeCall(self, functionName: str, numArgs: int):
        self.cur_func = functionName
        return_address = f"{self.cur_func}.return{self.iteration}"
        code = f"//write call {functionName}\n"
        # push return address
        code += self.push_return_address_to_stck(return_address)
        # push LCL,ARG,THIS,THAT
        code += self.push_to_stck("LCL")
        code += self.push_to_stck("ARG")
        code += self.push_to_stck("THIS")
        code += self.push_to_stck("THAT")
        # ARG=SP-n-5
        remove = numArgs + 5
        code += "//ARG=SP-n-5\n" + "@SP\n" + "D=M\n" + f"@{remove}\n" + \
                "D=D-A\n" + "@ARG\n" + "M=D\n"
        # LCL=SP
        code += "@SP\n" + "D=M\n" + "@LCL\n" + "M=D\n"
        # goto f
        code += f"@{functionName}\n" + "0;JMP\n"
        code += f"({return_address})\n"
        self.file.write(code)
        self.iteration += 1

    def writeFunction(self, functionName: str, numLocals: int):
        code = "//write_func\n"
        code = f"({functionName})\n"
        for i in range(numLocals):
            code += "@0\n" + "D=A\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + \
                    "M=M+1\n"
        self.file.write(code)

    def writeReturn_helper(self, str_name: str):
        code = "@FRAME\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + f"@{str_name}\n" \
               + "M=D\n"
        return code

    def writeReturn(self):
        # FRAME = LCL
        code = "//write return\n"
        code += "@LCL\n" + "D=M\n" + "@FRAME\n" + "M=D\n"
        # RET=*(FRAM-5)
        code += "@5\n" + "D=A\n" + "@FRAME\n" + "D=M-D\n" + "A=D\n" \
                + "D=M\n" + "@RET\n" + "M=D\n"
        # *arg = pop()
        code += "@SP\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + "@ARG\n" + "A=M\n" \
                + "M=D\n"
        # sp = ARG+1
        code += "@ARG\n" + "D=M\n" + "D=D+1\n" + "@SP\n" + "M=D\n"
        # code += "@ARG\n" + "A=M\n" + "D=A+1\n" + "@SP\n" + "M=D\n" yuval
        code += self.writeReturn_helper("THAT")
        code += self.writeReturn_helper("THIS")
        code += self.writeReturn_helper("ARG")
        code += self.writeReturn_helper("LCL")
        # goto RET
        code += "@RET\n" + "A=M\n" + "0;JMP\n"
        self.file.write(code)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename

    #  this func handle the cases if command == "add" or command == "sub".
    def add_or_sub(self, command: str) -> None:
        art_command = self.arithmetic_dict[command]
        self.file.write(
            f"@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "D=M\n" + \
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            f"D=M{art_command}D\n" + \
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    #  this func handle the cases if command == "neg".
    def neg(self) -> None:
        self.file.write(
            "@SP\n" + \
            "M=M-1\n" + \
            "A=M\n" + \
            "M=-M\n" + \
            "@SP\n" + \
            "M=M+1\n")

    #  this func handle the cases if command is binary.
    def binary(self, command: str) -> None:
        binary_dict = {"or": "|", "not": "!", "and": "&"}
        cur_cmd = binary_dict[command]
        iteration = self.iteration
        if cur_cmd == "!":
            self.file.write("@SP\n" + \
                            "M=M-1\n" + \
                            "A=M\n" + \
                            "M=!M\n" + \
                            "@SP\n" + \
                            "M=M+1\n")
        else:
            self.file.write(
                f"@SP\n" + \
                "M=M-1\n" + \
                "A=M\n" + \
                "D=M\n"  # d=y + \
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
            "A=M\n" + \
            f"M=M{cur_cmd}1\n" + \
            "@SP\n" + \
            "M=M+1\n")

    #  this func handle the cases if command is "gt" / "lt" / "eq"
    #    def compare(self, command: str):
    #        branch_dict = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
    #        cur_cmd = branch_dict[command]
    #        iteration = self.iteration
    #        self.file.write("@SP\n" + \
    #                        "M=M-1\n" + \
    #                        f"@MAIN_BLOCK{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # true - the condition is true
    #                        f"(TRUE{iteration})\n" + \
    #                        "@1\n" + \
    #                        "D=-A\n" + \
    #                        "@SP\n" + \
    #                        "A=M\n" + \
    #                        "M=D\n" + \
    #                        f"@FINISH{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # false - the condition is false
    #                        f"(FALSE{iteration})\n" + \
    #                        "@0\n" + \
    #                        "D=A\n" + \
    #                        "@SP\n" + \
    #                        "A=M\n" + \
    #                        "M=D\n" + \
    #                        f"@FINISH{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        f"(MAIN_BLOCK{iteration})\n" + \
    #                        "@SP\n" + \
    #                        "M=M-1\n" + \
    #                        "A=M\n" + \
    #                        "D=M\n" + \
    #                        f"@X_POS{iteration}\n" + \
    #                        "D;JGT\n" + \
    #                        f"@X_NEG{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # x>0 -> check if y>0:
    #                        f"(X_POS{iteration})\n" + \
    #                        "@SP\n" + \
    #                        "M=M+1\n" + \
    #                        "A=M\n" + \
    #                        "D=M\n" + \
    #                        f"@SAME_SIGN{iteration}\n" + \
    #                        "D;JGT\n" + \
    #                        f"@DIFF_SIGN{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # x<0 -> check if y>0:
    #                        f"(X_NEG{iteration})\n" + \
    #                        "M=M+1\n" + \
    #                        "@SP\n" + \
    #                        "A=M\n" + \
    #                        "D=M\n" + \
    #                        f"@DIFF_SIGN{iteration}\n" + \
    #                        "D;JGT\n" + \
    #                        f"@SAME_SIGN{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # if (x>0 and y>0 or x<0 and y<0)
    #                        f"(SAME_SIGN{iteration})\n" + \
    #                        "@SP\n" + \
    #                        "M=M-1\n" + \
    #                        "A=M\n" + \
    #                        "D=M\n" + \
    #                        "@SP\n" + \
    #                        "M=M+1\n" + \
    #                        "A=M\n" + \
    #                        "D=D-M\n" + \
    #                        "@SP\n" + \
    #                        "M=M-1\n" + \
    #                        f"@TRUE{iteration}\n" + \
    #                        f"D;{cur_cmd}\n" + \
    #                        f"@FALSE{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        # if (x>0 and y<0) or (x<0 and y>0)
    #                        f"(DIFF_SIGN{iteration})\n" + \
    #                        "@SP\n" + \
    #                        "M=M-1\n" + \
    #                        "A=M\n" + \
    #                        "D=M\n" + \
    #                        f"@TRUE{iteration}\n" + \
    #                        f"D;{cur_cmd}\n" + \
    #                        f"@FALSE{iteration}\n" + \
    #                        "0;JMP\n" + \
    # \
    #                        f"(FINISH{iteration})\n"
    #                        "@SP\n" + \
    #                        "M=M+1\n")
    #        self.iteration += 1

    def check_different_sign(self):
        # check if x is positive or eq to 0
        code = "@X\n" + "D=M\n" + f"@X_IS_POSITIVE.{self.iteration}\n" + "D;JGE\n"
        # else x is negative
        code += f"@X_IS_NEGATIVE.{self.iteration}\n" + "0;JMP\n"
        # x is pos -> check if y is positive
        code += f"(X_IS_POSITIVE.{self.iteration})\n"
        code += "@Y" + "D=M" + f"@SAME_SIGN.{self.iteration}\n" + \
                "D;JGE\n"
        # x is pos -> else Y is negative
        code += f"@X_POS_Y_NEG.{self.iteration}\n" + "0;JMP\n"

        # x is neg -> check if y is negative
        code += f"(X_IS_NEGATIVE.{self.iteration})\n"
        code += "@Y\n" + "D=M\n" + f"@SAME_SIGN.{self.iteration}\n" + \
                "D;JLT\n"
        # x is neg -> else Y is positive
        code += f"@X_NEG_Y_POS.{self.iteration}\n" + "0;JMP\n"
        self.file.write(code)

    def check_if_eq(self):
        #x&y has the same sign
        code = f"(SAME_SIGN.{self.iteration})\n"
        # x,y is eq
        code += "@X\n" + "D=M\n" + "@Y\n" + "D=D-M\n" + f"@TRUE.{self.iteration}\n" + \
                "D;JEQ\n"
        # x,y is different
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        # x>=0 y<0
        code += f"(X_POS_Y_NEG.{self.iteration})\n"
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        # x<0 y>=0
        code += f"(X_NEG_Y_POS.{self.iteration})\n"
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        self.file.write(code)

    def true(self):
        # sp = -1
        code = f"(TRUE.{self.iteration})\n"
        code += "@SP\n" + "A=M\n" + "M=1\n" + "M=-M\n" + f"@END.{self.iteration}\n"
        code += "0;JMP\n"
        self.file.write(code)

    def false(self):
        # sp = 0
        code = f"(FALSE.{self.iteration})\n"
        code += "@0\n" + "D=A\n" + "@SP\n" + "A=M\n" + "M=D\n" + f"@END.{self.iteration}\n"
        code += "0;JMP\n"
        self.file.write(code)

    def chek_if_lt(self):
        # x&y has the same sign
        code = f"(SAME_SIGN.{self.iteration})\n"
        # x,y is eq
        code += "@X\n" + "D=M\n" + "@Y\n" + "D=D-M\n" + f"@TRUE.{self.iteration}\n" + \
                "D;JLT\n"
        # x,y is different
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        # x>=0 y<0
        code += f"(X_POS_Y_NEG.{self.iteration})\n"
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        # x<0 y>=0
        code += f"(X_NEG_Y_POS.{self.iteration})\n"
        code += f"@TRUE.{self.iteration}\n" + "0;JMP\n"
        self.file.write(code)

    def chek_if_gt(self):
        # x&y has the same sign
        code = f"(SAME_SIGN.{self.iteration})\n"
        code += "@X\n" + "D=M\n" + "@Y\n" + "D=D-M\n" + f"@TRUE.{self.iteration}\n" + \
                "D;JGT\n"
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        # x>=0 y<0
        code += f"(X_POS_Y_NEG.{self.iteration})\n"
        code += f"@TRUE.{self.iteration}\n" + "0;JMP\n"
        # x<0 y>=0
        code += f"(X_NEG_Y_POS.{self.iteration})\n"
        code += f"@FALSE.{self.iteration}\n" + "0;JMP\n"
        self.file.write(code)

    def compare(self, cmd: str):
        # y=sp-1
        code = "@SP\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + "@Y\n" + "M=D\n"
        # x=sp-2, now sp=sp-2!
        code += "@SP\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + "@X\n" + "M=D\n"
        self.file.write(code)
        # eq-true if x=y and false otherwise
        # if x,y has different sign -> false
        # if x,y has same sign -> if x-y==0 return true
        if cmd == "eq":
            self.check_if_eq()
            # dont forget to increase sp!
        # lt-true if x<y and false otherwise
        if cmd == "lt":
            self.chek_if_lt()
        # gt-true if x>y and false otherwise
        if cmd == "gt":
            self.chek_if_gt()
        self.true()
        self.false()
        code = f"(END.{self.iteration})\n" + "@SP\n" + "M=M+1\n"
        self.file.write(code)
        self.iteration += 1


    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.
        Args:
            command (str): an arithmetic command.
        """
        self.file.write("//" + command + "\n")
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
        """
        this func handle the cases if command is push and segment is
        constant.
        """
        self.file.write(
            # "@SP\n" + \
            f"//PUSH_CONSTANT\n"
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
        """
            this func handle the cases if command is push and segment is
            in {"argument", "local", "this", "that"}
        """
        pos = self.segment_dict[segment]
        self.file.write(
            f"//PUSH {pos}\n"
            f"@{pos}\n" + \
            "D=M\n" + \
            f"@{index}\n" + \
            # "M=A\n" + \
            "A=D+A\n" +  # todo \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n" +  # todo
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def push_p(self, index: int, segment: str) -> None:
        """
            this func handle the cases if command is push and segment is
            in {"pointer", "temp"}
        """
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=A\n" + \
            f"@{index}\n" + \
            # "A = M\n" + #TODO: CHECK \
            "A=D+A\n" + \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n" +  # todo \
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    def push_static(self, index: int) -> None:
        """
           this func handle the cases if command is push and segment is
           "static"
       """
        file_name = self.file_name
        self.file.write(
            f"@{file_name}.{index}\n" + \
            "D=M\n" + \
            "@SP\n" + \
            "A=M\n" +  # todo
            "M=D\n" + \
            "@SP\n" + \
            "M=M+1\n")

    ###pop funcs

    def pop_heap(self, index: int, segment: str) -> None:
        """
            this func handle the cases if command is pop and segment is
            in {"argument", "local", "this", "that"}
        """
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
        """
            this func handle the cases if command is pop and segment is
            in {"pointer", "temp"}
        """
        pos = self.segment_dict[segment]
        self.file.write(
            f"@{pos}\n" + \
            "D=A\n" + \
            f"@{index}\n" + \
            # "M=A\n" + \
            "D=D+A\n"  # todo + \
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
        """
           this func handle the cases if command is pop and segment is
           "static"
       """
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
