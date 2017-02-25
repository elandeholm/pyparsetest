#
# Grammar derived from pyparsing/fourFn
#

from pyparsing import nums,alphas,alphanums,Regex
from pyparsing import Literal, Word, Group, Optional, ZeroOrMore, OneOrMore, Forward
from sys import stdin, argv

stack = [ ]

def push(f):
    def wrapped(*args):
        print('before push {}: stack is {}'.format(f.__name__, stack))       
        result = f(*args)
        stack.append(result)
        print('push {}({}): {}'.format(f.__name__, list(args), result))
        return result
    return wrapped

def pop(f):
    def wrapped(*args):
        print('before pop {}: stack is {}'.format(f.__name__, stack))       

        try:
            elem1 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        args = list(args)
        args.append(elem1)
        result = f(*args)

        print('pop {}({}) \n=> {}'.format(f.__name__, args, result))
        return result

    wrapped.__name__ = f.__name__

    return wrapped

def pop2(f):
    def wrapped(*args):
        print('before pop2 {}: stack is {}'.format(f.__name__, stack))       

        try:
            elem1 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        try:
            elem2 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        args = list(args)
        args.append(elem1)
        args.append(elem2)
        result = f(*args)

        print('pop2 {}({}) \n=> {}'.format(f.__name__, args, result))
        return result

    wrapped.__name__ = f.__name__

    return wrapped

def pop3(f):
    def wrapped(*args):
        print('before pop3 {}: stack is {}'.format(f.__name__, stack))

        try:
            elem1 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        try:
            elem2 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        try:
            elem3 = stack.pop()
        except IndexError as ie:
            raise IndexError(ie)

        args = list(args)
        args.append(elem1)
        args.append(elem2)
        args.append(elem3)
        result = f(*args)

        print('pop3 {}({}) \n=> {}'.format(f.__name__, args, result))
        return result

    wrapped.__name__ = f.__name__

    return wrapped

@push
def number_action(s, l, t):
    tl = t.asList()

    assert len(tl) == 1
    number = tl[0]

    return ['number', number ]

@push
def ident_action(s, l, t):
    tl = t.asList()

    assert len(tl) == 1
    ident = tl[0]

    return [ 'ident', ident ]

@push
@pop2
def funccall_action(s, l, t, ident, tupl):
    print('funccall_action, t is {}'.format(t))

    return [ 'funccall', ident, tupl ]

@push
@pop
def atom_action(s, l, t, atom):
    return [ 'atom', atom ]

@push
@pop3
def patom_action(s, l, t, op1, atom, op2):
    assert op1 == '('
    assert op2 == ')'

    return [ 'patom', atom ]

@push
@pop
def powexpr_action(s, l, t, number):
    print('*** powexpr_action(s={}, l={}, t={}, number={}): stack is {}'.format(s, l, t, number, stack))
    ti = iter(t)

    try:
        base = next(ti)
    except IndexError:
        return number

    raise ValueError(base)


    if base:
        return [ 'pow', base, number ]
    else:
        raise ValueError('kossa')

@push
@pop
def modexpr_action(s, l, t, number):
    print('*** modexpr_action(s={}, l={}, t={}, number={}): stack is {}'.format(s, l, t, number, stack))
    ti = iter(t)

    try:
        base = next(ti)
    except IndexError:
        return number

    return [ 'mod', base, number ]

@push
@pop
def product_action(s, l, t, number):
    print('*** product_action(s={}, l={}, t={}, base={}): stack is {}'.format(s, l, t, number, stack))
    assert False

@push
@pop
def sum_action(s, l, t, number):
    print('*** sum_action(s={}, l={}, t={}, base={}): stack is {}'.format(s, l, t, first, stack))
    assert False

@push
@pop
def expr_action(s, l, t, arg):
    return [ 'expr', arg ]

@push
@pop3
def tupl_action(s, l, t, op1, first, op2):
    assert op1 == '('
    assert op2 == ')'

    lst = [ first]

    while True:
        assert pop() == ','

        try:
            elem = stack.pop()
            lst.append(elem)
        except IndexError:
            berak

    return [ 'tuple', lst ]

class ExprParser:
    def __init__(self):
        plus, minus, mult, div, mod = map(Literal, '+-*/%')

        lpar = Literal('(')
        rpar = Literal(')')

        comma = Literal(',')

        powop = Literal( '^' )
        productop = mult | div
        modop  = Literal( '%' )
        sumop  = plus | minus

        tupl = Forward()

        number = Regex(r'[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?')
        number.setParseAction(number_action)

        ident = Word(alphas, alphanums+'_')
        ident.setParseAction(ident_action)

        funccall = ident + tupl
        funccall.setParseAction(funccall_action)

        atom = funccall | ident | number
        atom.setParseAction(atom_action)

        patom = lpar + atom + rpar
        patom.setParseAction(patom_action)

        powexpr = Forward()
        powexpr << Group( atom + ZeroOrMore( ( powop + powexpr ) ) )
        powexpr.setParseAction(powexpr_action)

        modexpr = Forward()
        modexpr << Group( powexpr + ZeroOrMore( ( modop + modexpr ) ) )
        modexpr.setParseAction(modexpr_action)

        product = Group( modexpr + ZeroOrMore( ( productop + modexpr ) ) )
        product.setParseAction(product_action)

        sumexpr = Group( product + Group( ZeroOrMore( sumop + product ) ) )
        sumexpr.setParseAction(sum_action)

        tupl << lpar + Optional(sumexpr + ZeroOrMore( comma + sumexpr ) ) + rpar
        tupl.setParseAction(tupl_action)

        expr = sumexpr | tupl
        expr.setParseAction(expr_action)

        self.bnf = expr

    def parse(self, s):
        return self.bnf.parseString(s, parseAll=True)

def inputprompt(prompt='> ', file=stdin):
    print(prompt, end='')
    line = next(file)
    return line.strip()

if __name__ == "__main__":
    e = ExprParser()

    try:
        s = ''.join(argv[1:])
    except IndexError:
        s = '42'

    try:
        result = e.parse(s)
    except:
        print(stack)
        raise
    print('* result: {}'.format(result))