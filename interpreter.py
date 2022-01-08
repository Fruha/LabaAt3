import sys
import os
import copy
from YACC import ParserClass
from SyntaxTree import node
from errors import *
from robot import *

LOG_WAY = True

class variable:
    def __init__(self, v_type, v_name, v_value=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        if v_value is None:
            self.value = 0
        else:
            if self.type == 'bool':
                self.value = v_value
            elif self.type == 'short' and isinstance(v_value, str):
                if v_value[0] == 's':
                    self.value = int(v_value[1:])
                else:  # -
                    v_value = v_value[0] + v_value[2:]
                    self.value = int(v_value)
            else:
                self.value = int(v_value)

    def __repr__(self):
        return f'{self.type} {self.name} = {self.value}'


class arr_variable:
    def __init__(self, v_type, v_name, v_dd, v_array=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        self.dd = v_dd
        if v_array is None:
            self.array = []
            nuls = 0
            for i in list(v_dd.values()):
                nuls += i
            for j in range(nuls):
                self.array.append(0)
        else:
            self.array = v_array
        
    def __repr__(self):
        dds = list(self.dd.values())
        return f'{self.type} {self.name}{dds} = {self.array}'

class TypeConverser:
    def __init__(self):
        pass

    def converse(self, var, vartype):
        if vartype == var.type:
            return var
        elif vartype == 'bool':
            return self.sint_to_bool(var)
        elif vartype == 'int':
            if var.type == 'short':
                return self.short_to_int(var)
            elif var.type == 'bool':
                return self.bool_to_int(var)
        elif vartype == 'short':
            if var.type == 'int':
                return self.int_to_short(var)
            elif var.type == 'bool':
                return self.bool_to_short(var)

    def sint_to_bool(self, var):
        if isinstance(var, variable):
            if var.value > 0:
                return variable('bool', '', 'true')
            elif var.value < 0:
                return variable('bool', '', 'false')
            else:
                return variable('bool', '', 'undefined')
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i][0] == 's':
                    if int(var.array[i][1:]) > 0:
                        arr[i] = 'true'
                    else:
                        arr[i] = 'undefined'
                elif var.array[i][0] == '-' and var.array[i][1] == 's':
                    if int(var.array[i][2:]) > 0:
                        arr[i] = 'false'
                    else:
                        arr[i] = 'undefined'
                else:
                    if int(var.array[i]) > 0:
                        arr[i] = 'true'
                    elif int(var.array[i]) < 0:
                        arr[i] = 'false'
                    else:
                        arr[i] = 'undefined'
            return arr_variable('bool', '', var.dd, arr)

    def int_to_short(self, var):
        if isinstance(var, variable):
            if var.value > 127 or var.value < -128:
                raise ConverseError
            return variable('short', '', var.value)
        else:
            for i in range(len(var.array)):
                if int(var.array[i]) > 127 or int(var.array[i]) < -128:
                    raise ConverseError
            return arr_variable('short', '', var.dd, var.array)

    def short_to_int(self, var):
        if isinstance(var, variable):
            if isinstance(var.value, int):
                return variable('int', '', var.value)
            else:
                return variable('int', '', var.value[1:])
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i][0] == 's':
                    arr[i] = var.array[i][1:]
                elif var.array[i][0] == '-' and var.array[i][1] == 's':
                    arr[i] = '-' + var.array[i][2:]
                else:
                    arr[i] = var.array[i]
            return arr_variable('int', '', var.dd, arr)

    def bool_to_int(self, var):
        if isinstance(var, variable):
            if var.value == 'true':
                return variable('int', '', 1)
            elif var.value == 'false':
                return variable('int', '', -1)
            else:
                return variable('int', '', 0)
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i] == 'true':
                    arr[i] = '1'
                elif var.array[i] == 'false':
                    arr[i] = '-1'
                else:
                    arr[i] = '0'
            return arr_variable('int', '', var.dd, arr)

    def bool_to_short(self, var):
        if isinstance(var, variable):
            if var.value == 'true':
                return variable('short', '', 1)
            elif var.value == 'false':
                return variable('short', '', -1)
            else:
                return variable('short', '', 0)
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i] == 'true':
                    arr[i] = '1'
                elif var.array[i] == 'false':
                    arr[i] = '-1'
                else:
                    arr[i] = '0'
            return arr_variable('short', '', var.dd, arr)


class interpreter:
    def __init__(self, program=None, robot=None):
        self.parser = ParserClass()
        self.converse = TypeConverser()
        self.error = Error_handler()
        self.dd = 0
        self.db_vars = [dict()]
        self.er_types = {
            'UnexpectedError': 0,
            'StartPointError': 1,
            'IndexError': 2,
            'RedeclarationError': 3,
            'ElementDeclarationError': 4,
            'ConverseError': 5,
            'UndeclaredVariableError': 6,
            'ArrayDeclarationError': 7,
            'NotArrayError': 8,
            'UndeclaredFunctionError': 9,
            'CallWorkError': 10,
            'WrongParameterError': 11,
            'RobotError': 12,
            'NameError': 13,
            'ArrayToVariableError': 14
        }
        self.tree = None
        self.funcs = None
        self.correct = None
        self.program = program
        self.robot = robot
        self.steps = 0
        self.exit = False

    def interpret(self):
        self.tree, self.funcs, self.correct = self.parser.parse(self.program)
        if self.correct:
            if 'work' not in self.funcs.keys():
                self.error.call(self.er_types['StartPointError'])
                return
            try:
                self.interp_node(self.funcs['work'].child['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'ERROR: RECURSION ERROR\n')
                sys.stderr.write("ERROR: FATAL ERROR\n")
                return False
            except Exit:
                return True
        else:
            sys.stderr.write(f'Incorrect input file\n')

    def interp_node(self, node):
        # print('id:', node.id, 'type:', node.type)
        if self.exit:
            raise Exit
        if node is None:
            return
        elif node.type == 'NL':
            pass
        elif node.type == 'EOS':
            pass
        elif node.type == 'error':
            self.error.call(self.er_types['UnexpectedError'], node)
        elif node.type == 'program':
            self.interp_node(node.child)
        elif node.type == 'group_stat':
            self.interp_node(node.child[1])
        elif node.type == 'statement list':
            self.interp_node(node.child[0])
            self.interp_node(node.child[1])
        elif node.type == 'declaration':
            decl_type = node.child[0]
            decl_child = node.child[1]
            try:
                if decl_child.type == 'var_list':
                    while decl_child.type == 'var_list':
                        self.declaration(decl_type, decl_child.child[0])
                        if decl_child.child[1].type != 'var_list':
                            self.declaration(decl_type, decl_child.child[1])
                        decl_child = decl_child.child[1]
                else:
                    self.declaration(decl_type, decl_child)
            except RedeclarationError:
                self.error.call(self.er_types['RedeclarationError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except ArrayDeclarationError:
                self.error.call(self.er_types['ArrayDeclarationError'], node)
            except ElementDeclarationError:
                self.error.call(self.er_types['ElementDeclarationError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
            except NameError:
                self.error.call(self.er_types['NameError'], node)

        elif node.type == 'assignment':
            try:
                self.assign_variable(node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
            except NotArrayError:
                self.error.call(self.er_types['NotArrayError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
            except NameError:
                self.error.call(self.er_types['NameError'], node)
            except ArrayToVariableError:
                self.error.call(self.er_types['ArrayToVariableError'], node)
        elif node.type == 'variable':
            try:
                return self._variable(node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
            except NameError:
                self.error.call(self.er_types['NameError'], node)
        elif node.type == 'arr variable':
            try:
                return self._arr_variable(node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
            except NotArrayError:
                self.error.call(self.er_types['NotArrayError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
            except NameError:
                self.error.call(self.er_types['NameError'], node)
        elif node.type == 'digit':
            if node.value[0] == 's':
                return variable('short', '', node.value)
            else:
                return variable('int', '', node.value)
        elif node.type == 'bool':
            return variable('bool', '', node.value)
        elif node.type == 'bracket':
            return node.value
        elif node.type == 'sizeof':
            try:
                return variable('int', '', self._sizeof(node))
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
        elif node.type == 'calculation':
            try:
                return self._calculation(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
        elif node.type == 'expression':
            return self.interp_node(node.child[1])

        elif node.type == 'if_then':
            try:
                self._if_th(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'if_th_el':
            try:
                self._if_th_el(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'do_while':
            try:
                self.func_while(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)

        elif node.type == 'function':
            pass
        elif node.type == 'param':
            try:
                return self.combine_param(node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
        elif node.type == 'call_func':
            try:
                return self.call_function(node)
            except RecursionError:
                raise RecursionError from None
            except UndeclaredFunctionError:
                self.error.call(self.er_types['UndeclaredFunctionError'], node)
            except CallWorkError:
                self.error.call(self.er_types['CallWorkError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)

        elif node.type == 'command':
            if self.robot is None:
                self.error.call(self.er_types['RobotError'], node)
                self.correct = False
                return 0
            if node.value == 'lms':
                return self.robot.lms()
            else:
                if self.robot.exit():
                    self.exit = True
                    return variable('bool', 'exit', 'true')
                self.steps += 1
                # self.robot.show()
                return self.robot.move(node.value)

        else:
            print('Not all nodes checked')

    def get_name(self, name):
        res = None
        length = len(name)
        for var in sorted(self.db_vars[self.dd].keys()):
            if var[:length] == name:
                if res is None:
                    res = var
                    if len(var) == len(name):
                        return res
                # else:
                #     raise NameError
        return res

    def _calculation(self, node):
        first_term = copy.deepcopy(self.interp_node(node.child[0]))
        second_term = copy.deepcopy(self.interp_node(node.child[1]))
        if isinstance(first_term, arr_variable) or isinstance(second_term, arr_variable):
            raise ConverseError
        if node.value == 'add':
            return self._add(first_term, second_term)
        if node.value == 'sub':
            return self._sub(first_term, second_term)
        if node.value == 'and':
            return self._and(first_term, second_term)
        if node.value == 'or':
            return self._or(first_term, second_term)
        if node.value == 'not or':
            return self._not_or(first_term, second_term)
        if node.value == 'not and':
            return self._not_and(first_term, second_term)
        elif node.value == 'first smaller' or node.value == 'second larger':
            return self._first_smaller(first_term, second_term)
        elif node.value == 'first larger' or node.value == 'second smaller':
            return self._first_larger(first_term, second_term)

    def _add(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return variable('int', 'res', first.value + second.value)

    def _sub(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return variable('int', 'res', first.value - second.value)

    def _first_smaller(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return variable('bool', 'res', 'false')
        elif first.value < second.value:
            return variable('bool', 'res', 'true')
        else:
            return variable('bool', 'res', 'undefined')

    def _first_larger(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return variable('bool', 'res', 'true')
        elif first.value < second.value:
            return variable('bool', 'res', 'false')
        else:
            return variable('bool', 'res', 'undefined')

    def _and(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' and second.value == 'true':
            return variable('bool', 'res', 'true')
        elif first.value == 'true' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'true' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'false' and second.value == 'true':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'true':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'undefined' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')

    def _or(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' or second.value == 'true':
            return variable('bool', 'res', 'true')
        elif first.value == 'false' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')

    def _not_or(self, first, second):
        var = self._or(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    def _not_and(self, first, second):
        var = self._and(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    def _variable(self, node):
        """get val by name"""
        var = self.get_name(node.value)
        if var is None:
            raise UndeclaredVariableError
        else:
            return self.db_vars[self.dd][var]

    def _arr_variable(self, node):
        """get val by index from arr"""
        name = self.get_name(node.value)
        if name is None:
            raise UndeclaredVariableError
        var = self.db_vars[self.dd][name]
        if isinstance(var, variable):
            raise NotArrayError
        i = self.get_el_index(node, var)
        type_var = var.type
        new_var = variable(type_var, name + str(i), self.db_vars[self.dd][name].array[i])
        return new_var

    def get_el_index(self, node, var):
        """[3][3], [1][2] -> 2*3 + 3"""
        ind = []
        ind = self.get_var_indexes(node, ind)
        # print('node:', node, 'ind:', ind)
        if isinstance(var, variable):
            raise NotArrayError
        if len(list(var.dd.values())) != len(ind):
            raise IndexError
        for i in range(len(ind)):
            if ind[i] > var.dd[i] - 1 or ind[i] < 0:
                raise IndexError
        if len(ind) == 1:
            return ind[0]
        ind.reverse()
        scp = list(var.dd.values())
        # print('scp:', scp)
        scp.reverse()
        res = ind[0]
        sc = 1
        i = 1
        while i < len(ind):
            sc *= scp[i]
            res += ind[i] * sc
            i += 1
        return res

    def get_var_indexes(self, node, ind):
        """ret using indexes"""
        if isinstance(node.child, list) and len(node.child) > 0:
            index = self.interp_node(node.child[0])
            if isinstance(index, arr_variable):
                raise IndexError
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
            ind = self.get_var_indexes(node.child[1], ind)
        elif node.type != 'index' and node.type != 'arr variable':
            index = self.interp_node(node)
            if isinstance(index, arr_variable):
                raise IndexError
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
        else:
            ind = self.get_var_indexes(node.child, ind)
        
        return ind

    def _sizeof(self, node):
        if node.child.type == 'type':
            tip = node.child.value
            return self.sizeof_type(tip)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, arr_variable):
                raise WrongParameterError
            return self.sizeof_type(var.type)

    def sizeof_type(self, type):
        if type == 'short' or type == 'short int':
            return 8
        elif type == 'int':
            return 16
        else:
            return 1

    def declaration(self, type, node):
        # print('self.dd:', self.dd)
        # print(self.db_vars)
        if node.type == 'var_list':
            for child in node.child:
                self.declaration(type, child)
        if type.type == 'arr':
            if node.type == 'variable':
                raise ArrayDeclarationError
            arr_dd = self._arr_dd(type, 1)  # counting vector of
            arr_type = self._arr_type(type)
            # print('type:', type, 'arr_type:', arr_type)
            # print(self.funcs)
            if node.type == 'arr variable':
                if node.value in self.db_vars[self.dd].keys() or node.value in self.funcs:
                    raise RedeclarationError
                index_dd = self._index_dd(node.child, 1)
                if index_dd != arr_dd:
                    raise ArrayDeclarationError
                arr_indexes = {}
                arr_indexes = self.get_indexes(node.child, arr_indexes, 0)
                # print('node:', node, 'arr_indexes:', arr_indexes)
                var = arr_variable(arr_type, node.value, arr_indexes)
                self.db_vars[self.dd][node.value] = var
            elif node.type == 'var_list':
                for ch in node.child:
                    self.declaration(type, ch)
            elif node.type == 'assignment':
                raise ArrayDeclarationError
            elif node.type == 'assignment array':
                var_ch = node.child[0]
                expr_ch = node.child[1]
                arr_name = var_ch.value
                if arr_name in self.db_vars[self.dd].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if var_ch.type == 'arr variable':
                    index_dd = self._index_dd(var_ch.child, 1)
                    if index_dd != arr_dd:
                        raise ArrayDeclarationError
                    arr_indexes = {}
                    arr_indexes = self.get_indexes(var_ch.child, arr_indexes, 0)
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_indexes)
                    amount_items = self.count_items(arr_indexes)
                    if amount_items != len(arr_values):
                        raise ArrayDeclarationError
                    if index_dd != len(arr_indexes.keys()):
                        raise ArrayDeclarationError
                    var = arr_variable(arr_type, arr_name, arr_indexes, arr_values)
                    if var is not None:
                        self.db_vars[self.dd][arr_name] = var
                elif var_ch.type == 'variable':
                    arr_indexes = {}
                    for i in range(arr_dd):
                        arr_indexes[i] = -1
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_indexes)
                    for i in arr_indexes.values():
                        if i == -1:
                            raise ArrayDeclarationError
                    var = arr_variable(arr_type, arr_name, arr_indexes, arr_values)
                    if var is not None:
                        self.db_vars[self.dd][arr_name] = var

        else:  # if type.type == 'type'
            if node.type == 'variable':
                if node.value in self.db_vars[self.dd].keys() or node.value in self.funcs:
                    raise RedeclarationError
                else:
                    self.db_vars[self.dd][node.value] = variable(type.value, node.value)
            elif node.type == 'arr variable':
                raise ElementDeclarationError
            elif node.type == 'assignment array':
                raise ArrayDeclarationError
            else:  # if node.type == 'assignment'
                var = node.child[0].value
                if var in self.db_vars[self.dd].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if node.child[0].type != 'arr variable':
                    expr = self.interp_node(node.child[1])
                    if expr is not None:
                        expr = self.converse.converse(expr, type.value)
                        self.db_vars[self.dd][var] = variable(type.value, var, expr.value)
                else:
                    raise ElementDeclarationError

    def _arr_dd(self, node, i):
        if node.child.type == 'type':
            return i
        else:
            return self._arr_dd(node.child, i + 1)

    def _index_dd(self, node, i):
        if isinstance(node.child, list):
            return self._index_dd(node.child[1], i + 1)
        else:
            return i

    def _arr_type(self, node):
        if node.type == 'type':
            return node.value
        else:
            return self._arr_type(node.child)

    def get_indexes(self, node, indexes, layer):
        if isinstance(node.child, list):
            var = self.interp_node(node.child[0])
            if isinstance(var, arr_variable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return self.get_indexes(node.child[1], indexes, layer + 1)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, arr_variable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return indexes

    def get_arr_values(self, node, type, indexes):
        arr = []
        if node.type == 'array_comma':
            raise ArrayDeclarationError
        else:
            self.get_arr_next(node.child, type, arr, indexes, 0, 0)
        return arr

    def get_arr_next(self, node, type, arr, indexes, lvl, amount):
        if node.type == 'array_comma':
            amount += 1
            self.get_arr_next(node.child[0], type, arr, indexes, lvl, amount)
            amount = self.get_arr_next(node.child[1], type, arr, indexes, lvl, amount)
            if indexes[lvl] is None:
                raise ArrayDeclarationError
            if indexes[lvl] == -1:
                indexes[lvl] = amount+1
            else:
                if indexes[lvl] != amount+1:
                    raise ArrayDeclarationError
        elif node.type == 'array_lvl':
            self.get_arr_next(node.child, type, arr, indexes, lvl+1, 0)
        else:
            st = len(arr)
            self.get_arr_const(node, type, arr)
            things = len(arr) - st
            if indexes[lvl] is None:
                raise ArrayDeclarationError
            if indexes[lvl] == -1:
                indexes[lvl] = things
            else:
                if indexes[lvl] != things:
                    raise ArrayDeclarationError
        return amount

    def get_arr_const(self, node, type, arr):
        if node.type == 'array item':
            arr.append(self.get_const(node.child[0], type))
            self.get_arr_const(node.child[1], type, arr)
        else:
            arr.append(self.get_const(node, type))

    def get_const(self, node, type):
        if node.type == 'bool':
            if type != 'bool':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'digit':
            if node.value[0] == 's' and type == 'int':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'sizeof':
            if type == 'bool':
                raise ArrayDeclarationError
            return self._sizeof(node)

    def count_items(self, ind):
        sum = 1
        for i in list(ind.values()):
            sum = sum * i
        return sum

    def assign_variable(self, node):
        var = node.child[0]
        if var.type == 'variable':
            name = self.get_name(var.value)
            if name is None:
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            variab = self.db_vars[self.dd][name]
            if expr is None:
                return
            if expr.type != variab.type:
                expr = self.converse.converse(expr, variab.type)
            if self.robot is None:
                if isinstance(variab, arr_variable) and isinstance(expr, arr_variable):
                    if variab.dd != expr.dd:
                        raise IndexError
                    self.db_vars[self.dd][name].array = expr.array
                elif isinstance(variab, variable) and isinstance(expr, variable):
                    self.db_vars[self.dd][name].value = expr.value
                else:
                    raise ArrayToVariableError
            else:
                if isinstance(variab, arr_variable):
                    self.db_vars[self.dd][name].array = expr.array
                else:
                    self.db_vars[self.dd][name].value = expr.value

        elif var.type == 'arr variable':
            name = self.get_name(var.value)
            if name is None:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            if expr is not None:
                var_class = self.db_vars[self.dd][name]
                if expr.type != var_class.type:
                    expr = self.converse.converse(expr, var_class.type)
                ind = self.get_el_index(var, var_class)
                self.db_vars[self.dd][var_class.name].array[ind] = str(expr.value)

    def _if_th(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body'])

    def _if_th_el(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body_1'])
        else:
            self.interp_node(node.child['body_2'])

    def func_while(self, node):
        try:
            while self.converse.converse(self.interp_node(node.child['condition']), 'bool').value == 'true':
                self.interp_node(node.child['body'])
        except ConverseError:
            self.error.call(self.er_types['ConverseError'], node)
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        except UndeclaredVariableError:
            self.error.call(self.er_types['UndeclaredVariableError'], node)
        except RedeclarationError:
            self.error.call(self.er_types['RedeclarationError'], node)
        except ElementDeclarationError:
            self.error.call(self.er_types['ElementDeclarationError'], node)
        except NotArrayError:
            self.error.call(self.er_types['NotArrayError'], node)

    def call_function(self, node):
        name = node.value
        if self.dd > 100:
            self.dd = -1
            raise RecursionError
        if name not in self.funcs.keys():
            raise UndeclaredFunctionError
        if name == 'work':
            raise CallWorkError
        param = node.child
        input_param = []
        change_value = []
        try:
            while param is not None:
                if param.type == 'func_param':
                    if param.value == 'none':
                        input_param = []
                        break
                    else:
                        input_param.append(self.interp_node(param.child[1]))
                        if param.child[1].type == 'arr variable':
                            change_value.append(len(input_param) - 1)
                        param = param.child[0]
                else:
                    input_param.append(self.interp_node(param))
                    if param.type == 'arr variable':
                        change_value.append(len(input_param) - 1)
                    break
            input_param.reverse()
            for i in range(len(change_value)):
                change_value[i] = -change_value[i] - 1
        except NotArrayError:
            self.error.call(self.er_types['NotArrayError'], node)
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        self.dd += 1
        self.db_vars.append(dict())
        func_param = []
        node_param = self.funcs[name].child['parameters']
        func_param = self.get_parameter(node_param)
        if len(func_param) != len(input_param):
            raise WrongParameterError
        for i in range(len(input_param)):
            self.set_param(input_param[i], func_param[i])
        for par in func_param:
            self.db_vars[self.dd][par.name] = par
        self.interp_node(self.funcs[name].child['body'])
        result = copy.deepcopy(self.interp_node(self.funcs[name].child['return']))
        self.db_vars.pop()
        self.dd -= 1
        for i in range(len(input_param)):
            name = input_param[i].name
            input_param[i] = self.converse.converse(func_param[i], input_param[i].type)
            input_param[i].name = name
        for p in change_value:
            par = input_param[p]
            arr_type = self.db_vars[self.dd][par.name[:-1]].type
            if par.type != arr_type:
                par = self.converse.converse(par, arr_type)
            self.db_vars[self.dd][par.name[:-1]].array[int(par.name[-1])] = str(par.value)
            input_param[p] = None
            func_param[p] = None
            for var in input_param:
                if var is not None:
                    self.db_vars[self.dd][var.name] = var
        return result

    def get_parameter(self, node):
        if node.type == 'param_none':
            return []
        param = []
        while isinstance(node.child, list):
            if node.type == 'param arr':
                param.append(self.interp_node(node.child[0]))
                param.append(self.interp_node(node.child[1]))
            elif node.type == 'param':
                param.append(self.combine_param(node))
            if len(node.child) == 0 or node.child[0].type == 'param':
                break
            node = node.child[0]
        # param.reverse()
        return param

    def combine_param(self, node):
        type_node = node.child[0]
        ch_node = node.child[1]
        if ch_node.type == 'arr variable':
            raise WrongParameterError
        if type_node.type == 'type':
            type = type_node.value
            return variable(type, ch_node.value)

        else:  # type_node.type == 'arr':
            arr_dd = self._arr_dd(type_node, 1)
            arr_type = self._arr_type(type_node)
            dd = {}
            for i in range(arr_dd):
                dd[i] = 0
            return arr_variable(arr_type, ch_node.value, dd)

    def set_param(self, input, func):
        if isinstance(input, arr_variable) and isinstance(func, arr_variable):
            t = self.converse.converse(input, func.type)
            func.array = t.array
            func.dd = t.dd
        elif isinstance(input, variable) and isinstance(func, variable):
            t = self.converse.converse(input, func.type)
            func.value = t.value
        else:
            raise WrongParameterError


def create_robot(file_name):
    with open(file_name) as file:
        text = file.read().split('\n')
    robot_info = text.pop(0).split(' ')
    map_size = text.pop(0).split(' ')
    x = int(robot_info[0])
    y = int(robot_info[1])
    map_ = [0] * int(map_size[0])

    for i in range(int(map_size[0])):
        map_[i] = [0]*int(map_size[1])
    for i in range(int(map_size[0])):
        for j in range(int(map_size[1])):
            map_[i][j] = Cell("empty")
    pos = 0
    while len(text) > 0:
        line = list(text.pop(0))
        line = [Cell(cells[i]) for i in line]
        map_[pos] = line
        pos += 1
    return Robot(x, y, map_)


if __name__ == '__main__':
    get_files_name = lambda folder_name:[f'{folder_name}/{file_name}' for file_name in os.listdir(folder_name)]
    prog_names = get_files_name('Programs')
    path_finders = get_files_name('Path finders')
    maps = get_files_name('Maps')
    while True:
        print('\n---------------------\n0)Programs \n1)Robot \n---------------------\n')
        n = int(input())
        if n == 0:
            print('choose program:')
            for i, program_name in enumerate(os.listdir('Programs')):
                print(f'{i}){program_name}')
            # print('1 - QuickSort \n2 - Factorial \n3 - Errors \n4 - Factorial recursion')
            num = int(input())
            if num < 0 or num >= len(prog_names):
                print('Error: Wrong number\n')
                continue
            with open(prog_names[num]) as f:
                i = interpreter(program=f.read().lower())
                res = i.interpret()
                if res:
                    # print(i.db_vars[0])
                    print('------>Database vars:<-------')
                    for db_vars in i.db_vars:
                        for k, v in db_vars.items():
                            print(v)
                else:
                    print('Error')
        elif n == 1:
            print('choose algorithm:')
            for i, path_finders_name in enumerate(os.listdir('Path finders')):
                print(f'{i}){path_finders_name}')
            m1 = int(input())
            if m1 < 0 or m1 >= len(path_finders):
                print('Error: Wrong number\n')
                continue
            print('\nchoose map:')
            for i, map_name in enumerate(os.listdir('Maps')):
                print(f'{i}){map_name}')
            m = int(input())
            if m < 0 or m >= len(maps):
                print('Error: Wrong number\n')
                continue
            robot = create_robot(maps[m])
            with open(path_finders[m1]) as f:
                # f = open(path_finders[m])
                i = interpreter(program=f.read().lower(), robot=robot)
                i.robot.show()
                res = i.interpret()
                if res:
                    print('------>Database vars:<-------')
                    for db_vars in i.db_vars:
                        for k, v in db_vars.items():
                            print(v)
                else:
                    print('Error')
                if i.exit:
                    print(f'The robot found exit in {i.steps} steps\n')
                else:
                    print('The robot did not find a way out\n')