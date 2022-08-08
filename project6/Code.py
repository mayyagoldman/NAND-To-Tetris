"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        dest_dict = {"null": "000", "M": "001", "D": "010", "DM": "011", "MD": "011",
                     "A": "100", "AM": "101", "MA": "101",
                     "AD": "110", "DA": "110", "ADM": "111"}
        if mnemonic in dest_dict:
            return dest_dict[mnemonic]
        else:
            return dest_dict["null"]

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        comp_dict = {"0": "0101010", "1": "0111111", "-1": "0111010",
                     "D": "0001100",
                     "A": "0110000", "M": "1110000", "!D": "0001101",
                     "!A": "0110001"
            , "!M": "1110001", "-D": "0001111", "-A": "0110011",
                     "-M": "1110011", "D+1": "0011111", "A+1": "0110111",
                     "M+1": "1110111", "D-1": "0001110", "A-1": "0110010",
                     "M-1": "1110010", "D|A": "0010101", "D|M": "1010101",
                     "D&A": "0000000", "D&M": "1000000", "A-D": "0000111",
                     "M-D": "1000111"
            , "D-A": "0010011", "D-M": "1010011", "D+A": "0000010",
                     "D+M": "1000010", "D<<": "0110000", "A<<": "0100000", "M<<": "1100000", "D>>": "0010000"
            , "A>>": "0000000", "M>>": "1000000"}

        if mnemonic in comp_dict:
            return comp_dict[mnemonic]
        else:
            return comp_dict["0"]

    @staticmethod
    def jump(mnemonic: str) -> str:
        jump_dict = {"null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
                     "JLT": "100", "JNE": "101", "JLE": "110",
                     "JMP": "111"}

        if mnemonic in jump_dict:
            return jump_dict[mnemonic]
        else:
            return jump_dict["null"]

    @staticmethod
    def a_instructions(num: int) -> str:
        bin_num = bin(num).replace("0b", "")
        if len(bin_num) < 16:
            zreo_times = 16 - len(bin_num)
            bin_num = "0" * zreo_times + bin_num
        if len(bin_num) > 16:
            bin_num = bin_num[:16]
        bin_num = "0" + bin_num[1:]
        return bin_num
