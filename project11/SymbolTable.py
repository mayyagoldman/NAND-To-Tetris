"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.ClassDict = {}  # ClassDict[name] = [type,kind,count]
        self.ClassCount = {'field': 0, 'static': 0, 'argument': 0,
                           'local': 0,
                           'variable': 0}
        self.SubDict = {}
        self.SubCount = {'field': 0, 'static': 0, 'argument': 0,
                         'local': 0, 'variable': 0}
        self.ScopeDict = self.ClassDict  # current Scop dict
        self.ScopeCount = self.ClassCount  # current Scop kind counter

    def return_num_class_var(self):
        return self.ClassCount['static'] + self.ClassCount['field']

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's
        symbol table).
        """
        self.SubCount = {'field': 0, 'static': 0, 'argument': 0, 'local': 0,
                         'variable': 0}
        self.SubDict = {}
        self.ScopeDict = self.SubDict
        self.ScopeCount = self.SubCount

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns
        it a running index. "STATIC" and "FIELD" identifiers have a class scope,
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
            subrotin is :type(int/bool/char/ class name), kind(var/arg)
        """
        if kind in {'static', 'field'}:
            count = self.ClassCount[kind]
            self.ClassDict[name] = [type, kind, count]
            self.ClassCount[kind] += 1
        elif kind in {'argument', 'variable', 'local'}:
            count = self.SubCount[kind]
            self.SubDict[name] = [type, kind, count]
            self.SubCount[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in
            the current scope.
        """
        return self.ScopeCount[kind.lower()]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.ScopeDict.get(name, False):
            return self.ScopeDict[name][1]
        elif self.ClassDict.get(name, False):
            return self.ClassDict[name][1]
        else:
            return 'None'

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.ScopeDict.get(name, False):
            return self.ScopeDict[name][0]
        elif self.ClassDict.get(name, False):
            return self.ClassDict[name][0]
        else:
            return 'None'

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier, or -1
            if the identifier is unknown in the current scope.
        """
        if self.ScopeDict.get(name, False):
            return self.ScopeDict[name][2]
        elif self.ClassDict.get(name, False):
            return self.ClassDict[name][2]
        else:
            return -1
