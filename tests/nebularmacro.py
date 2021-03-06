from fractions import Fraction
from operator import add
from functools import reduce

from macropy.core.macros import *
from macropy.core.quotes import macros, q, u, name, ast, ast_list

macros = Macros()
S = None


@macros.expr
def sy(tree, **kw):
    new_tree = sympylizer.recurse(tree, False)
    return new_tree


@macros.decorator
def parallelize_asserts(tree, gen_sym, exact_src, **kw):
    """
    Transforms all asserts in a function of the form
        def test_me():
            assert solve(a1) == b1
            print "hi"
            assert solve(a2) == b2
    into
        def test_me():
            expected_1 = lambda: b1
            actual_1 = lambda: solve(a1)
            print "hi"
            expected_2 = lambda: b2
            actual_2 = lambda: solve(a2)
            return [('solve(a1)', 'b1', expected_1, actual_1), ('solve(a2)', 'b2', expected_2, actual_2)]
    """
    transformed_statements = [transform_assert(stmt, gen_sym, exact_src) if isinstance(stmt, Assert)
                              else ([stmt],) + (None,) * 5 for stmt in tree.body]
    new_body = reduce(add, [ts[0] for ts in transformed_statements])

    ret = list(q[u[in_str], u[sympylized], u[ex_str], name[ex_sym], name[ac_sym]]
               for _, in_str, sympylized, ex_str, ex_sym, ac_sym in transformed_statements
               if in_str is not None)
    tree.body = new_body + [Return(value=q[ast_list[ret]])]
    # print unparse(tree)
    return tree


def transform_assert(stmt, gen_sym, exact_src):
    """
    Transforms and assert statement of the form
        assert solve(a) == b
    into
        expected_1 = lambda: b
        actual_1 = lambda: solve(a)
    :return: ('solve(a)', 'b', expected_1, actual_1)
    """
    input_str = exact_src(stmt.test.left)  # solve(a)
    actual_sym = gen_sym("actual_")
    new_actual = sy(stmt.test.left)

    expected_str = exact_src(stmt.test.comparators[0])  # b
    expected_sym = gen_sym("expected_")
    new_expected = sy(stmt.test.comparators[0])

    with q as code:
        name[expected_sym] = lambda: ast[new_expected]
        name[actual_sym] = lambda: ast[new_actual]
    copy_location(code[0], stmt.test.comparators[0])
    copy_location(code[1], stmt.test.left)

    return code, input_str, unparse(new_actual), expected_str, expected_sym, actual_sym


MAPPING = {Eq: 'Eq', NotEq: 'Ne'}  # , Lt: 'Lt', LtE: 'Le', Gt: 'Gt', GtE: 'Ge'}


@Walker
def sympylizer(tree, ctx, set_ctx, **kw):
    if isinstance(tree, Num) and not ctx:
        set_ctx(True)  # prevent infinite descent
        return num2S(tree.n)
    elif isinstance(tree, Compare):
        if isinstance(tree.ops[0], (Eq, NotEq)) and len(tree.comparators) == 1:
            sympy_op = MAPPING[type(tree.ops[0])]
            return q[name[sympy_op](ast[tree.left], ast[tree.comparators[0]])]


def num2S(n):
    frac = Fraction(n).limit_denominator()
    if frac.denominator != 1:
        return q[S(u[int(frac.numerator)]) / u[int(frac.denominator)]]
    else:
        return q[S(u[int(frac.numerator)])]
