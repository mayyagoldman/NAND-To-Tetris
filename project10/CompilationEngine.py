"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = JackTokenizer(input_stream)
        self.output_file = output_stream
        self.current_indentation = 0
        self.op = {'+', '-', '*', '/', '|', '=', '&amp', '&lt', '&gt'}
        self.op_to_str = {'+': '+', '-': '-', '*': '*', '/': '/', '|': '|',
                          '=': '=', '&amp': "&amp;", '&lt': '&lt;', '<': '<',
                          '&gt': '&gt;', '>': '>', ')': ')', '(': '(',
                          '{': '{', '}': '}'}
        self.type_to_str = {"IDENTIFIER": 'identifier', 'SYMBOL': 'symbol',
                            'KEYWORD': 'keyword', 'INT_CONST': 'intConstant',
                            'STRING_CONST': 'stringConstant'}

        self.ClassVarDec = {'static', 'field'}
        self.SubroutineDec = {'constructor', 'function', 'method'}

    def get_indentation(self, num):
        '''
        returns the current indentation
        '''
        current_indentation = self.current_indentation
        self.current_indentation += num
        return "    " * current_indentation

    def write_terminal(self, word, tag):
        '''
        like <symbol> ( </symbol>
        '''
        indentation = self.get_indentation(0)
        text = f"{indentation}<{tag}> {word} </{tag}>\n"
        self.output_file.write(text)

    def write_non_terminal_rules_start(self, word):
        '''
         like <whileStatment> ...... ( </symbol>
        '''
        indentation = self.get_indentation(1)
        text = f"{indentation}<{word}>\n"
        self.output_file.write(text)

    def write_non_terminal_rules_end(self, word):
        '''
         like ( </symbol>)
        '''
        self.current_indentation -= 1
        indentation = "    " * self.current_indentation
        text = f"{indentation}</{word}>\n"
        self.output_file.write(text)

    def write_type(self):
        '''
        writes the current token type
        '''
        if self.tokenizer.token_type() == 'KEYWORD':
            keyword = self.tokenizer.get_token()
            self.write_terminal(keyword, "keyword")
        else:
            className = self.tokenizer.identifier()
            self.write_terminal(className, "identifier")
        self.advance()

    def advance(self):
        '''
        advances the token
        '''
        self.tokenizer.advance()

    def isClassVarDec(self):
        '''
        checks if token is in {'static', 'field'}
        '''
        return self.tokenizer.get_token() in self.ClassVarDec

    def isSubroutineDec(self):
        '''
         checks if token is in {'constructor', 'function', 'method'}
        '''
        return self.tokenizer.get_token() in self.SubroutineDec

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write_non_terminal_rules_start("class")
        self.write_terminal("class", "keyword")
        self.advance()
        class_name = self.tokenizer.identifier()
        self.write_terminal(class_name, "identifier")
        self.advance()
        left_curly_prent = self.tokenizer.symbol()
        self.write_terminal(left_curly_prent, 'symbol')
        self.advance()
        while self.tokenizer.symbol() != "}":
            while self.isClassVarDec():
                self.compile_class_var_dec()
            while self.isSubroutineDec():
                self.compile_subroutine()
        right_curly_prent = self.tokenizer.symbol()
        self.write_terminal(right_curly_prent, 'symbol')
        self.write_non_terminal_rules_end("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write_non_terminal_rules_start("classVarDec")
        static_or_field = self.tokenizer.get_token()
        self.write_terminal(static_or_field, "keyword")
        self.advance()
        self.write_type()
        varName = self.tokenizer.identifier()
        self.write_terminal(varName, "identifier")
        self.advance()
        while self.tokenizer.symbol() == ",":
            self.write_terminal(",", "symbol")
            self.advance()
            extraVarName = self.tokenizer.identifier()
            self.write_terminal(extraVarName, "identifier")
            self.advance()
        self.write_terminal(";", "symbol")
        self.write_non_terminal_rules_end("classVarDec")
        self.advance()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.write_non_terminal_rules_start("subroutineDec")
        constructor_func_method = self.tokenizer.get_token()
        self.write_terminal(constructor_func_method, "keyword")
        self.advance()
        self.write_type()
        subroutineName = self.tokenizer.identifier()
        self.write_terminal(subroutineName, "identifier")
        self.advance()
        left_prent = self.tokenizer.symbol()
        self.write_terminal(left_prent, "symbol")
        self.advance()
        self.compile_parameter_list()
        right_prent = self.tokenizer.symbol()
        self.write_terminal(right_prent, "symbol")
        self.advance()
        self.compile_subroutine_body()
        self.write_non_terminal_rules_end("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.write_non_terminal_rules_start("parameterList")
        while self.tokenizer.symbol() != ")":
            self.write_type()
            varName = self.tokenizer.identifier()
            self.write_terminal(varName, "identifier")
            self.advance()
            while self.tokenizer.symbol() == ",":
                self.write_terminal(",", "symbol")
                self.advance()
                self.write_type()
                extraVarName = self.tokenizer.identifier()
                self.write_terminal(extraVarName, "identifier")
                self.advance()
        self.write_non_terminal_rules_end("parameterList")

    def compile_subroutine_body(self):
        '''
        Compiles a subroutine body.
        '''
        self.write_non_terminal_rules_start("subroutineBody")
        curly_left_prent = self.tokenizer.symbol()
        self.write_terminal(curly_left_prent, "symbol")
        self.advance()
        while self.tokenizer.get_token() == 'var':
            self.compile_var_dec()
        self.compile_statements()
        curly_right_prent = self.tokenizer.symbol()
        self.write_terminal(curly_right_prent, "symbol")
        self.write_non_terminal_rules_end("subroutineBody")
        self.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_non_terminal_rules_start("varDec")
        var = self.tokenizer.get_token()
        self.write_terminal(var, "keyword")
        self.advance()
        self.write_type()
        varName = self.tokenizer.identifier()
        self.write_terminal(varName, "identifier")
        self.advance()
        while self.tokenizer.symbol() == ",":
            self.write_terminal(",", "symbol")
            self.advance()
            extraVarName = self.tokenizer.identifier()
            self.write_terminal(extraVarName, "identifier")
            self.advance()
        self.write_terminal(";", "symbol")
        self.write_non_terminal_rules_end("varDec")
        self.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.write_non_terminal_rules_start("statements")
        while self.tokenizer.get_token() != "}":
            if self.tokenizer.get_token() == 'do':
                self.compile_do()
            elif self.tokenizer.get_token() == 'let':
                self.compile_let()
            elif self.tokenizer.get_token() == 'while':
                self.compile_while()
            elif self.tokenizer.get_token() == 'return':
                self.compile_return()
            elif self.tokenizer.get_token() == 'if':
                self.compile_if()
        self.write_non_terminal_rules_end("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_non_terminal_rules_start("doStatement")
        self.write_terminal("do", "keyword")
        self.advance()
        self.compile_subroutine_call()
        self.write_terminal(";", "symbol")  # ;
        self.advance()
        self.write_non_terminal_rules_end("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write_non_terminal_rules_start("letStatement")
        self.write_terminal("let", "keyword")
        self.advance()
        varName = self.tokenizer.identifier()
        self.write_terminal(varName, "identifier")
        self.advance()
        if self.tokenizer.symbol() == "[":
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # [
            self.advance()
            self.compile_expression()
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # ]
            self.advance()
        if self.tokenizer.symbol() == "[":
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # [
            self.advance()
            self.compile_expression()
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # ]
            self.advance()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # =
        self.advance()
        self.compile_expression()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # ;
        self.advance()
        self.write_non_terminal_rules_end("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write_non_terminal_rules_start("whileStatement")
        self.write_terminal("while", "keyword")
        self.advance()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # (
        self.advance()
        self.compile_expression()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # )
        self.advance()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # {
        self.advance()
        self.compile_statements()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # }
        self.advance()
        self.write_non_terminal_rules_end("whileStatement")

    def compile_return(self) -> None:
        self.write_non_terminal_rules_start("returnStatement")
        self.write_terminal("return", "keyword")
        self.advance()
        while self.tokenizer.symbol() != ';':
            self.compile_expression()  # ?
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # ;
        self.advance()
        self.write_non_terminal_rules_end("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.write_non_terminal_rules_start("ifStatement")
        self.write_terminal("if", "keyword")
        self.advance()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # (
        self.advance()
        self.compile_expression()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # )
        self.advance()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # {
        self.advance()
        self.compile_statements()
        self.write_terminal(self.tokenizer.symbol(), "symbol")  # }
        self.advance()
        while self.tokenizer.keyword() == "ELSE":
            self.write_terminal("else", "keyword")
            self.advance()
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # {
            self.advance()
            self.compile_statements()
            self.write_terminal(self.tokenizer.symbol(), "symbol")  # }
            self.advance()
        self.write_non_terminal_rules_end("ifStatement")

    def compile_expression(self) -> None:
        '''
        compiles a hole expression
        '''
        self.write_non_terminal_rules_start('expression')
        self.compile_term()
        while self.tokenizer.get_token() in self.op:
            op = self.tokenizer.get_token()
            self.write_terminal(self.op_to_str[op], "symbol")
            self.advance()
            self.compile_term()
        self.write_non_terminal_rules_end('expression')

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write_non_terminal_rules_start('term')
        if self.tokenizer.token_type() == "INT_CONST":
            self.write_terminal(str(self.tokenizer.get_token()),
                                "integerConstant")
            self.advance()
        elif self.tokenizer.token_type() == "STRING_CONST":
            self.write_terminal(self.tokenizer.get_token(), "stringConstant")
            self.advance()
        elif self.tokenizer.token_type() == "KEYWORD":
            self.write_terminal(self.tokenizer.get_token(), "keyword")
            self.advance()
        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.compile_identifier_term()
        elif self.tokenizer.get_token() == "(":
            self.write_terminal("(", "symbol")
            self.advance()
            self.compile_expression()
            self.write_terminal(")", "symbol")
            self.advance()
        else:
            self.write_terminal(self.tokenizer.get_token(), "symbol")
            self.advance()
            self.compile_term()
        self.write_non_terminal_rules_end('term')

    def compile_identifier_term(self):
        '''
        identify and compiles a term
        '''
        next_token = self.tokenizer.get_next_token()
        if next_token[0] == "[":
            varName = self.tokenizer.identifier()
            self.write_terminal(varName, "identifier")
            self.advance()
            self.write_terminal("[", "symbol")
            self.advance()
            self.compile_expression()
            self.write_terminal("]", "symbol")
            self.advance()
        elif next_token[0] == "(" or next_token[0] == ".":
            self.compile_subroutine_call()
        else:
            varName = self.tokenizer.identifier()
            self.write_terminal(varName, "identifier")
            self.advance()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_non_terminal_rules_start('expressionList')
        while self.tokenizer.get_token() != ")":
            self.compile_expression()
            while self.tokenizer.get_token() == ",":
                self.write_terminal(",", "symbol")
                self.advance()
                self.compile_expression()
        self.write_non_terminal_rules_end('expressionList')

    def compile_subroutine_call(self):
        next_token = self.tokenizer.get_next_token()
        if next_token[0] == "(":
            subroutineName = self.tokenizer.identifier()
            self.write_terminal(subroutineName, "identifier")
            self.advance()
            self.write_terminal("(", "symbol")
            self.advance()
            self.compile_expression_list()
            self.write_terminal(")", "symbol")
            self.advance()
        if next_token[0] == ".":
            class_or_var_name = self.tokenizer.identifier()
            self.write_terminal(class_or_var_name, "identifier")
            self.advance()
            self.write_terminal(".", "symbol")
            self.advance()
            subroutineName = self.tokenizer.identifier()
            self.write_terminal(subroutineName, "identifier")
            self.advance()
            self.write_terminal("(", "symbol")
            self.advance()
            self.compile_expression_list()
            self.write_terminal(")", "symbol")
            self.advance()

    def run(self):
        '''
        runs the program.
        '''
        self.tokenizer.advance()
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.get_token() == 'class':
                self.compile_class()
            self.advance()
