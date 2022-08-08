"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_file = input_stream
        self.lines = input_stream.read().splitlines()
        self.raw_txt = ""
        self.tokens = []
        self.curr_token = ()
        self.tokens_read = 0
        self.keyword_dict = dict.fromkeys(['class', 'constructor' , 'keyword', 'function', 'keyword', 'method' , 'keyword',
                                           'field', 'static', 'var', 'int', 'char',
                                           'boolean', 'void', 'true', 'false', 'null',
                                           'this', 'let', 'do', 'if', 'else',
                                           'while', 'return'], 'keyword')
        self.symbol_dict = dict.fromkeys(
            ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~' , '^' , '#'], 'symbol')
        self.removeComments()
        self.define_token()

    def define_token(self):
        '''
        defines a token.
        generate a list of tuples, (token,token type)
        '''
        keys_pattern = ''
        for key in self.keyword_dict.keys():
            keys_pattern += f'{key}(?!\w)|'
        keys_pattern = keys_pattern[:-7]
        symbol_pattern = ''
        for symbol in self.symbol_dict:
            symbol_pattern += f"|\\{symbol}"
        symbol_pattern = "[" + symbol_pattern[1:] + "]"
        numbers_pattern = r'\d+'
        string_pattern = '"[^"]*"'
        identifier_pattern = r"[\w]+"
        all_patterns = re.compile(
           keys_pattern + '|' + string_pattern + "|"+ symbol_pattern  + '|' + numbers_pattern + '|' + identifier_pattern)
        tokens = all_patterns.findall(self.raw_txt)
        for token in tokens:
            if re.match(keys_pattern , token) is not None:
                new_token = self.replace_tokens(token)
                self.tokens.append((new_token , "KEYWORD"))
            elif re.match(symbol_pattern , token) is not None:
                new_token = self.replace_tokens(token)
                self.tokens.append((new_token , "SYMBOL"))
            elif re.match(numbers_pattern, token) is not None:
                new_token = self.replace_tokens(token)
                self.tokens.append((new_token, "INT_CONST"))
            elif re.match(string_pattern, token) is not None:
                new_token = self.replace_tokens(token)
                self.tokens.append((new_token, "STRING_CONST"))
            elif re.match(identifier_pattern, token) is not None:
                new_token = self.replace_tokens(token)
                self.tokens.append((new_token, "IDENTIFIER"))

    def replace_tokens(self , token):
        '''
        replaces the token with maching text
        '''
        if len(token) > 1:
            if (token[0] == "\"") and (token[-1] == "\""):
                token = token[1:-1]
        if token == "<":
            token = "&lt;"
        if token == ">":
            token = "&gt;"
        if token == "&":
            token = "&amp;"
        if token == "\"":
            token = "&quot;"
        return token

    def removeComments(self):
        """ Removes comments from the file string """
        string = -1
        comment = False
        for line in self.lines:
            curr_idx = 0
            prev_idx = 0
            curr_line = line.strip()
            processed_line = ""
            while curr_idx != len(curr_line):
                if curr_idx + 2 <= len(curr_line):  # to avoid bad acsses
                    if curr_line[
                       curr_idx:curr_idx + 2] == "//" and string == -1:  # comment not in string - line ends for us here
                        break
                if comment:  # if comment - we seek to end it
                    if curr_idx + 2 > len(curr_line):  # go beyond the range of line no way it ends here
                        break
                    if curr_line[curr_idx:curr_idx + 2] == "*/":  # comment ended at this idx
                        comment = False
                        prev_idx = curr_idx + 2
                        curr_idx = curr_idx + 2
                        continue
                    else:  # continue searching
                        curr_idx += 1
                        continue
                if curr_line[curr_idx] == "\"":  # check if we start \ finish string mode
                    string *= -1
                    processed_line += curr_line[curr_idx]
                    curr_idx += 1
                    continue
                if curr_idx + 2 <= len(curr_line):  # to avoid bad acsses
                    if curr_line[curr_idx:curr_idx + 2] == "/*":
                        if string == 1:  # if we are in string mode comment should be included, comment mode not activated
                            processed_line += curr_line[curr_idx]
                            curr_idx += 1
                            continue
                        else:
                            comment = True  # activate comment mode
                            # processed_line += curr_line[prev_idx:curr_idx]  # add everything up till this point
                            curr_idx += 1
                            continue
                processed_line += curr_line[curr_idx]  # boring case nothing happend just add it
                curr_idx += 1
            processed_line = processed_line.strip()  # clean are line from extra spaces
            self.raw_txt += processed_line + " "

    def get_next_token(self) -> tuple:
        '''
        returns (next token,next token type)
        '''
        if self.has_more_tokens():
            return self.tokens[self.tokens_read]


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return len(self.tokens) != self.tokens_read

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.curr_token = self.tokens[self.tokens_read]
            self.tokens_read +=1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.tokens_read != 0 :
            return self.curr_token[1]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """


        if self.tokens_read != 0 and self.curr_token[1] == "KEYWORD":
            return self.curr_token[0].upper()


    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        if self.tokens_read != 0 and self.curr_token[1] == "SYMBOL":
            return self.curr_token[0]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        if self.tokens_read != 0 and self.curr_token[1] == "IDENTIFIER":
            return self.curr_token[0]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        if self.tokens_read != 0 and self.curr_token[1] == "INT_CONST":
            return int(self.curr_token[0])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        if self.tokens_read != 0 and self.curr_token[1] == "STRING_CONST":
            return self.curr_token[0]

    def get_token(self):
        '''
        return current token[0]
        '''
        if self.tokens_read > 0 and self.has_more_tokens():
            return self.curr_token[0]