"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


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
        self.commenting_mode = False
        self.tokenizer = JackTokenizer(input_stream)
        self.output_file = output_stream
        self.table = SymbolTable()
        self.writer = VMWriter(output_stream)
        self.class_name = ''
        self.if_label_counter = -1
        self.while_label_counter = -1
        self.cur_token = ''

        self.op = {'+': 'add', '-': 'sub', '*': 'Math.multiply',
                   '/': 'Math.divide', '|': 'or', '=': 'eq', '&amp;': 'and',
                   '&lt;': 'lt', '&gt;': 'gt'}
        self.unary_op = {'-': 'neg', '~': 'not', '^': 'shiftleft',
                         '#': 'shiftright'}
        self.op_to_str = {'+': '+', '-': '-', '*': '*', '/': '/', '|': '|',
                          '=': '=', '&amp': "&amp;", '&lt': '&lt;', '<': '<',
                          '&gt': '&gt', '>': '>', ')': ')', '(': '(',
                          '{': '{',
                          '}': '}'}  # does it support the extra types?
        self.type_to_str = {"IDENTIFIER": 'identifier', 'SYMBOL': 'symbol',
                            'KEYWORD': 'keyword', 'INT_CONST': 'intConstant',
                            'STRING_CONST': 'stringConstant'}
        self.class_name = ''

    def advance(self):
        '''
        advances the token
        '''
        self.tokenizer.advance()
        self.cur_token = self.tokenizer.get_token()
        return self.tokenizer.get_token()

    def find_var(self, name: str) -> tuple:
        idx = self.table.index_of(name)
        kind = self.table.kind_of(name)
        return kind, idx

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if (self.commenting_mode):
            self.output_file.write('//compile_class\n')
        self.class_name = self.advance()
        self.advance()  # {
        self.advance()  # classVarDec / subDec
        while self.tokenizer.symbol() != "}":
            while self.isClassVarDec():
                self.compile_class_var_dec()
            while self.isSubroutineDec():
                self.compile_subroutine()
        # }
        self.writer.close()  # closes the file

    def isClassVarDec(self):
        '''
        checks if token is in {'static', 'field'}
        '''
        return self.tokenizer.get_token() in {'static', 'field'}

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        if (self.commenting_mode):
            self.output_file.write('//compile_class_var_dec\n')
        kind = self.tokenizer.get_token()  # static/field
        varType = self.advance()
        varName = self.advance()
        self.table.define(varName, varType, kind)
        self.advance()
        while self.tokenizer.symbol() == ",":
            extraVarName = self.advance()
            self.table.define(extraVarName, varType, kind)
            self.advance()
        self.advance()  # ;

    def isSubroutineDec(self):
        '''
         checks if token is in {'constructor', 'function', 'method'}
        '''
        return self.tokenizer.get_token() in {'constructor', 'function',
                                              'method'}

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        if (self.commenting_mode):
            self.output_file.write('//compile_subroutine\n')
        self.if_label_counter = -1
        self.while_label_counter = -1
        constructor_func_method = self.tokenizer.get_token()
        self.table.start_subroutine()  # starts a new subroutine.
        func_dict = {'constructor': self.compile_constructor,
                     'function': self.compile_func,
                     'method': self.compile_method}
        func_dict[constructor_func_method]()

    def compile_parameter_list_method(self):
        """ compiles the parameter list of a method"""
        name = 'this'
        type = self.class_name
        kind = 'argument'
        self.table.define(name, type, kind)  # add <this,className,0>
        type = self.tokenizer.get_token()
        if type == ')':
            self.advance()
            return
        token = self.advance()
        kind = 'argument'
        self.table.define(token, type, kind)
        token = self.advance()
        while token == ',':
            type = self.advance()
            token = self.advance()
            self.table.define(token, type, kind)
            token = self.advance()
        self.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration. like var int x, y, z, w;"""
        type = self.advance()
        varName = self.advance()
        token = self.advance()  # ; or , or )
        self.table.define(varName, type, 'local')
        while token == ",":
            extraVarName = self.advance()
            token = self.advance()
            self.table.define(extraVarName, type, 'local')

    def compile_func(self):
        """
        compiles a fanction
        """
        if (self.commenting_mode):
            self.output_file.write('//compile_sunc\n')
        self.advance()
        func_name = self.class_name + '.' + self.advance()
        self.advance()  # (
        self.advance()
        self.compile_parameter_list()
        self.advance()  # {
        token = self.tokenizer.get_token()
        while token == 'var':
            self.compile_var_dec()
            token = self.advance()
        var_num = self.table.var_count('local')
        self.writer.write_function(func_name, var_num)
        self.compile_statements()
        self.advance()  # }

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".    like (int x, int y, char l)"""
        if (self.commenting_mode):
            self.output_file.write('//compile_parameter_list')

        while self.tokenizer.symbol() != ")":
            type = self.tokenizer.get_token()
            varName = self.advance()
            kind = 'argument'
            self.table.define(varName, type, kind)
            token = self.advance()
            while token == ",":
                type = self.advance()
                extraVarName = self.advance()
                self.table.define(extraVarName, type, kind)
                token = self.advance()
        self.advance()

    def compile_method(self):
        """
        compiles a method
        """
        if (self.commenting_mode):
            self.output_file.write('//compile_method\n')
        self.advance()
        func_name = self.class_name + '.' + self.advance()
        self.advance()  # (
        self.advance()
        self.compile_parameter_list_method()

        self.advance()  # {
        token = self.tokenizer.get_token()
        while token == 'var':
            self.compile_var_dec()
            token = self.advance()
        var_num = self.table.var_count('local')
        self.writer.write_function(func_name, var_num)
        self.writer.write_push('argument', 0)
        self.writer.write_pop('pointer', 0)
        self.compile_statements()
        self.advance()  # }

    def compile_constructor(self):
        """ compiles a constructor subroutine"""
        if (self.commenting_mode):
            self.output_file.write('//compile_constructor\n')
        self.advance()  # type
        self.advance()  # sub_name
        self.advance()  # (
        token = self.advance()  # parameterList or )
        if token != ')':  # parameterList
            self.compile_parameter_list()
        filedVarSize = self.table.var_count('argument')
        func_name = self.class_name + '.new'
        count_class_var = self.table.return_num_class_var()
        self.advance()  # {
        token = self.tokenizer.get_token()
        while token == 'var':
            self.compile_var_dec()
            token = self.advance()
        var_num = self.table.var_count('local')
        self.writer.write_function(func_name, var_num)
        self.writer.write_push('constant', count_class_var)
        self.writer.write_call('Memory.alloc', 1)
        self.writer.write_pop('pointer', 0)
        self.compile_statements()
        self.advance()  # }


    def compile_statements(self) -> None:
        """Compiles a sequence of statements"""
        func_dict = {'do': self.compile_do, 'let': self.compile_let,
                     'while': self.compile_while,
                     'return': self.compile_return,
                     'if': self.compile_if}
        while self.tokenizer.get_token() != "}":
            if func_dict.get(self.tokenizer.get_token(), False):
                func_dict[self.tokenizer.get_token()]()
                token = self.tokenizer.get_token()
            else:
                self.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.if_label_counter += 1
        counter = self.if_label_counter  # saves locally label counter
        if (self.commenting_mode):
            self.output_file.write('//Compiles if\n')
        self.advance()  # (
        self.advance()  # (in)
        self.compile_expression()
        # )
        self.advance()  # {
        self.writer.write_if(f"IF_TRUE{counter}")
        self.writer.write_goto(f"IF_FALSE{counter}")
        self.advance()
        self.writer.write_label(f"IF_TRUE{counter}")
        self.compile_statements()  # true statments
        self.advance()
        if self.tokenizer.keyword() == "ELSE":
            self.writer.write_goto(f"IF_END{counter}")
            self.writer.write_label(f"IF_FALSE{counter}")
            self.advance()  # {
            self.advance()
            self.compile_statements()  # compile false statments # }
            self.advance()
            self.writer.write_label(f"IF_END{counter}")
        else:
            self.writer.write_label(f"IF_FALSE{counter}")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.while_label_counter += 1
        counter = self.while_label_counter  # saves locally label counter
        if (self.commenting_mode):
            self.output_file.write('//Compiles while\n')
        self.writer.write_label(f"WHILE_EXP{counter}")
        self.advance()  # (
        self.advance()  # (in)
        self.compile_expression()
        # )
        self.writer.write_arithmetic("not")
        self.writer.write_if(f"WHILE_END{counter}")
        self.advance()  # {
        self.advance()  # {in}
        self.compile_statements()
        # }
        self.writer.write_goto(f"WHILE_EXP{counter}")
        self.writer.write_label(f"WHILE_END{counter}")
        self.advance()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        if (self.commenting_mode):
            self.output_file.write('//Compiles do\n')
        self.advance()
        # self.compile_subroutine_call()  # ;
        self.compile_expression()
        self.writer.write_pop("temp", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        if (self.commenting_mode):
            self.output_file.write('//Compiles let\n')
        varName = self.advance()
        var_kind, var_idx = self.find_var(varName)
        token = self.advance()
        if token == "[":  # array acsses
            self.advance()  # get over [ symbol
            self.writer.write_push(var_kind, var_idx)
            self.compile_expression()  # ]
            self.advance()  # get over ] symbol
            self.writer.write_arithmetic('add')
            self.advance()  # get over = symbol
            self.compile_expression()  # RHS
            self.writer.write_pop('temp', 0)
            self.writer.write_pop('pointer', 1)
            self.writer.write_push('temp', 0)
            self.writer.write_pop('that', 0)
        else:  # simple case
            self.advance()  # get over = symbol
            self.compile_expression()  # RHS
            self.write_pop(var_kind, var_idx)
        self.advance()  # get over ;

    def write_pop(self, var_kind, var_idx) -> None:
        """ writes a pop command according to variable kind"""
        if var_kind in {'variable', 'local'}:
            self.writer.write_pop('local', var_idx)
        elif var_kind == 'argument':
            self.writer.write_pop('argument', var_idx)
        elif var_kind == 'field':
            self.writer.write_pop('this', var_idx)
        elif var_kind == 'static':
            self.writer.write_pop('static', var_idx)


    def write_push(self, var_kind, var_idx) -> None:
        """ writes a push command according to variable kind"""
        if var_kind in {'variable', 'local'}:
            self.writer.write_push('local', var_idx)
        elif var_kind == 'argument':
            self.writer.write_push('argument', var_idx)
        elif var_kind == 'field':
            self.writer.write_push('this', var_idx)
        elif var_kind == 'static':
            self.writer.write_push('static', var_idx)


    def compile_return(self) -> None:
        """ compiles a return statement"""
        if (self.commenting_mode):
            self.output_file.write('//Compiles return\n')
        self.advance()  # return
        if self.tokenizer.symbol() == ';':  # void method
            self.writer.write_push('constant', 0)
        else:
            self.compile_expression()
        self.writer.write_return()
        self.advance()  # skip ;

    def insert_letters(self, string: str) -> None:
        for i in string:
            val = ord(i)

            self.writer.write_push('constant', val)
            self.writer.write_call('String.appendChar', 2)

    def compile_keyword(self, keyword: str) -> None:
        # like - "BOOLEAN", "CHAR", "VOID", "STATIC", "FIELD", "TRUE",
        # "FALSE", "NULL", "THIS"
        if keyword == 'true':
            self.writer.write_push('constant', 0)
            self.writer.write_arithmetic('not')
        elif keyword in {'false', 'null'}:
            self.writer.write_push('constant', 0)
        elif keyword == 'this':
            self.writer.write_push('pointer', 0)

    def compile_expression(self) -> None:
        '''
        compiles a hole expression
        '''
        if (self.commenting_mode):
            self.output_file.write('//compile_expression\n')
        self.compile_term()
        op = self.tokenizer.get_token()
        while op in self.op.keys():
            op_to_vm = self.op[op]
            self.advance()
            self.compile_term()
            if op_to_vm == 'Math.multiply':
                self.writer.write_call('Math.multiply', 2)
            elif op_to_vm == 'Math.divide':
                self.writer.write_call('Math.divide', 2)
            else:
                self.writer.write_arithmetic(op_to_vm)
            op = self.tokenizer.get_token()

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        if (self.commenting_mode):
            self.output_file.write('//compile_expression_list\n')
        args_num = 0
        while self.tokenizer.get_token() != ")":
            args_num += 1
            self.compile_expression()
            while self.tokenizer.get_token() == ",":
                self.advance()
                self.compile_expression()
                args_num += 1
        return args_num

    def compile_square_brackets(self):
        """ compiles array accsess """
        varName = self.tokenizer.identifier()
        self.advance()  # [
        self.advance()  # [inside]
        self.compile_expression()
        var_index = self.table.index_of(varName)
        var_kind = self.table.kind_of(varName)
        self.write_push(var_kind, var_index)
        self.writer.write_arithmetic('add')
        self.writer.write_pop('pointer', 1)
        self.writer.write_push('that', 0)
        self.advance()  # ]

    def compile_identifier_term(self):
        '''
        identify and compiles a term
        '''
        next_token = self.tokenizer.get_next_token()[0]
        if next_token == "[":
            self.compile_square_brackets()
            # self.compile_expression()
        elif next_token == "(" or next_token == ".":
            self.compile_subroutine_call()
        else:
            varName = self.tokenizer.identifier()
            var_kind, var_idx = self.find_var(varName)
            self.write_push(var_kind, var_idx)
            self.advance()

    def compile_subroutine_call(self):
        """ compiles a subroutine call """
        subroutineName = self.tokenizer.get_token()
        next_token = self.tokenizer.get_next_token()
        args_num = 0
        if next_token[0] == "(":
            self.advance()  # (
            self.advance()  # (in)
            self.writer.write_push('pointer', 0)
            args_num = self.compile_expression_list() + 1
            subroutineName = self.class_name + '.' + subroutineName
            # )
        if next_token[0] == ".":
            # like other.getsize()
            class_or_var_name = self.tokenizer.get_token()
            var_kind, var_idx = self.find_var(class_or_var_name)
            if var_idx != -1:
                self.write_push(var_kind, var_idx)
                class_or_var_name = self.table.type_of(class_or_var_name)
            else:
                args_num -= 1
            self.advance()  # .
            subroutineName = class_or_var_name + '.' + self.advance()
            self.advance()  # (
            self.advance()  # (in)
            args_num += self.compile_expression_list()
            args_num += 1
        self.writer.write_call(subroutineName,
                               args_num)  # account for class type
        self.advance()

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
        if (self.commenting_mode):
            self.output_file.write('//compile_term\n')
        # next_token = self.tokenizer.get_next_token()
        token_type = self.tokenizer.token_type()
        token = self.tokenizer.get_token()
        if token_type == "INT_CONST":
            self.writer.write_push('constant', token)
            self.advance()
        elif token_type == "STRING_CONST":
            self.writer.write_push('constant', len(token))
            self.writer.write_call('String.new', 1)
            self.insert_letters(token)
            self.advance()
        elif token_type == "KEYWORD":
            self.compile_keyword(token)
            self.advance()
        elif token_type == "IDENTIFIER":
            self.compile_identifier_term()
        elif token == "(":  # we need to give priority
            self.advance()
            self.compile_expression()
            self.advance()
        elif token in {'-', '~', '<<', '>>'}:
            self.advance()
            self.compile_term()
            self.writer.write_arithmetic(self.unary_op[token])
        else:  # symbol
            self.advance()
            self.compile_term()

    def run(self):
        '''
        runs the program.
        '''
        self.tokenizer.advance()
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.get_token() == 'class':
                self.compile_class()
            self.advance()
        self.writer.close
