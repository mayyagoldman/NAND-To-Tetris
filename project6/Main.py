"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def first_pass(parser: Parser, table: SymbolTable):
    n = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.curr_type != 3:
            n += 1
        else:
            table.add_entry(parser.symbol(), n)


def second_pass(parser: Parser, table: SymbolTable):
    parser.reset_parser()
    n = 16
    while parser.has_more_commands():
        if n >= table.get_address("SCREEN"): break
        parser.advance()
        symbol = str(parser.symbol())
        if symbol == "None":
            continue

        if not table.contains(symbol):
            if symbol.isdigit():
                table.add_entry(symbol, int(symbol))
            else:
                table.add_entry(symbol, n)
                n += 1


def third_pass(parser: Parser, table: SymbolTable, output_file: typing.TextIO):
    parser.reset_parser()
    while parser.has_more_commands():
        parser.advance()
        if parser.curr_type == 1:
            line = Code.a_instructions(table.get_address(parser.symbol()))
            output_file.write(line + "\n")
        elif parser.curr_type == 2:
            line = "111" + Code.comp(parser.comp()) + Code.dest(parser.dest()) + Code.jump(parser.jump())
            output_file.write(line + "\n")
        elif parser.curr_type == 4:
            line = "101" + Code.comp(parser.comp()) + Code.dest(parser.dest()) + Code.jump(parser.jump())
            output_file.write(line + "\n")


def assemble_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

       Args:
           input_file (typing.TextIO): the file to assemble.
           output_file (typing.TextIO): writes all output to this file.
       """
    table = SymbolTable()
    parser = Parser(input_file)
    input_file.close()

    # *Initialization*
    first_pass(parser, table)
    # *Second Pass*
    second_pass(parser, table)
    # After the command is translated, write the translation to the output file.
    third_pass(parser, table, output_file)
    output_file.close()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
