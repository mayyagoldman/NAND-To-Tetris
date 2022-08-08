"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing

from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO, code_writer: CodeWriter) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)
    code_writer.set_file_name(input_filename)
    while parser.has_more_commands():
        parser.advance()
        if parser.curr_type == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.curr_command)
        elif parser.curr_type == "C_PUSH" or parser.curr_type == "C_POP":
            code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
        elif parser.curr_type == "C_GOTO":
            code_writer.writeGoto(parser.arg1())
        elif parser.curr_type == "C_LABEL":
            code_writer.writeLabel(parser.arg1())
        elif parser.curr_type == "C_IF":
            code_writer.WriteIf(parser.arg1())
        elif parser.curr_type == "C_FUNCTION":
            code_writer.writeFunction(parser.arg1(), parser.arg2())
        elif parser.curr_type == "C_RETURN":
            code_writer.writeReturn()
        elif parser.curr_type == "C_CALL":
            code_writer.writeCall(parser.arg1(), parser.arg2())
        else:
            break



if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        code_writer = CodeWriter(output_file)
        code_writer.writeInit()
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, code_writer)
        code_writer.close()

