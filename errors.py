import sys
import SyntaxTree


class Error_handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = [
            'UnexpectedError',
            'StartPointError',
            'IndexError',
            'RedeclarationError',
            'ElementDeclarationError',
            'ConverseError',
            'UndeclaredVariableError',
            'ArrayDeclarationError',
            'NotArrayError',
            'UndeclaredFunctionError',
            'CallWorkError',
            'WrongParameterError',
            'RobotError',
            'NameError',
            'ArrayToVariableError'
        ]

    def call(self, err_type, node=None):
        self.type = err_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(err_type)]}: ')
        if self.type == 0:
            sys.stderr.write(f'Incorrect syntax at {self.node.children[0].lineno} line \n')
            return
        elif self.type == 1:
            sys.stderr.write(f'No WORK function in program\n')
        elif self.type == 2:
            sys.stderr.write(f'Index is wrong at line {self.node.lineno}\n')
        elif self.type == 3:
            sys.stderr.write(f'Redeclaration of a variable "{self.node.child[1].child[0].value}" at line {self.node.child[1].child[0].lineno}\n')
        elif self.type == 4:
            sys.stderr.write(f'Declared element of array at line {self.node.child[0].lineno}\n')
        elif self.type == 5:
            sys.stderr.write(f'Can\'t converse types at line {self.node.lineno}\n')
        elif self.type == 6:
            if node.type == 'variable' or node.type == 'arr variable':
                sys.stderr.write(f'Using undeclared variable "{self.node.value}" at line {self.node.lineno}\n')
            else:
                sys.stderr.write(f'Using undeclared variable "{self.node.child[0].value}" at line {self.node.child[0].lineno}\n')
        elif self.type == 7:
            if node.child[1].type == 'variable' or node.child[1].type == 'arr variable':
                sys.stderr.write(
                    f'Wrong declaration of array "{self.node.child[1].value}" at line {self.node.child[1].lineno}\n')
            else:
                sys.stderr.write(f'Wrong declaration of array "{self.node.child[1].child[0].value}" at line {self.node.child[1].child[0].lineno}\n')
        elif self.type == 8:
            sys.stderr.write(f'Trying to get index from not array variable "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 9:
            sys.stderr.write(f'Calling undeclared function "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 10:
            sys.stderr.write(f'Calling WORK function at line {self.node.lineno}\n')
        elif self.type == 11:
            sys.stderr.write(f'Wrong parameters in function "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 12:
            sys.stderr.write(f'Robot error at line {self.node.lineno}\n')
        elif self.type == 13:
            if node.type == 'variable' or node.type == 'arr variable':
                sys.stderr.write(
                    f'Name "{self.node.value}" at line {self.node.lineno} correlates with 2 or more\n')
            else:
                sys.stderr.write(f'Name "{self.node.child[0].value}" at line {self.node.child[0].lineno} correlates with 2 or more\n')
        elif self.type == 14:
            sys.stderr.write(f'Can\'t assign variable to array variable or vice versa at line {self.node.lineno}\n')


class UnexpectedError(Exception):
    pass


class StartPointError(Exception):
    pass


class IndexError(Exception):
    pass


class RedeclarationError(Exception):
    pass


class ElementDeclarationError(Exception):
    pass


class ConverseError(Exception):
    pass


class UndeclaredVariableError(Exception):
    pass


class ArrayDeclarationError(Exception):
    pass


class NotArrayError(Exception):
    pass


class UndeclaredFunctionError(Exception):
    pass


class CallWorkError(Exception):
    pass


class WrongParameterError(Exception):
    pass


class RobotError(Exception):
    pass


# class NameError(Exception):
#     pass


class ArrayToVariableError(Exception):
    pass


class Exit(Exception):
    pass
