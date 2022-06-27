import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils.common.tools import Evaluator
import awkward as ak
import numpy as np

# Number Evaluator
ev = Evaluator()
add_test = ev.evaluate('1+2')
assert add_test == 3
sub_test = ev.evaluate('1-2')
assert sub_test == -1
mult_test = ev.evaluate('1*2')
assert mult_test == 2
pow_test = ev.evaluate('2**2')
assert pow_test == 4
n_binops_test = ev.evaluate('((2+1)*3 - 4)**2')
assert n_binops_test == 25

eq_test = ev.evaluate('2==2')
assert eq_test is True
neq_test = ev.evaluate('1!=2')
assert neq_test is True
lt_test = ev.evaluate('1<2')
assert lt_test is True
leq_test = ev.evaluate('2<=2')
assert lt_test is True

two_ops_right = ev.evaluate("2==2 and 3==3")
assert two_ops_right is True
two_ops_wrong = ev.evaluate("2!=2 and 3==3")
assert two_ops_wrong is False
two_ops_wrong_bitwise_and = ev.evaluate("(2!=2) & (3==3)")
assert two_ops_wrong_bitwise_and is False
two_ops_right_bitwise_and = ev.evaluate("(2==2) & (3==3)")
assert two_ops_right_bitwise_and is True
two_ops_right_bitwise_or = ev.evaluate("(2==2) | (3==3)")
assert two_ops_right_bitwise_or is True
two_ops_wrong_bitwise_or = ev.evaluate("(2!=2) | (3==3)")
assert two_ops_wrong_bitwise_or is True

ev = Evaluator(a = 3)
var_gt_leq_right = ev.evaluate('1 < a <= 3')
assert var_gt_leq_right is True
ev = Evaluator(a = 4)
var_gt_leq_wrong = ev.evaluate('1 < a <= 3')
assert var_gt_leq_wrong is False


ev = Evaluator(x = True, y = False)
true_or_false_test = ev.evaluate('x or y')
true_and_false_test = ev.evaluate('x and y')
assert true_or_false_test is True
assert true_and_false_test is False

ev = Evaluator(x = True, y = True)
true_or_true_test = ev.evaluate('x or y')
true_and_true_test = ev.evaluate('x and y')
assert true_or_true_test is True
assert true_and_true_test is True

ev = Evaluator(x = False, y = False)
false_or_false_test = ev.evaluate('x or y')
false_and_false_test = ev.evaluate('x and y')
assert false_or_false_test is False
assert false_and_false_test is False

ev = Evaluator(x = False, y = True)
false_or_true_test = ev.evaluate('x or y')
false_and_true_test = ev.evaluate('x and y')
assert false_or_true_test is True
assert false_and_true_test is False


test_arr = ak.Array({'x': [0,1,2,3], 'y': [0,10,20,30]})

ev = Evaluator(x = test_arr.x)
ak_field_gt_test = ev.evaluate('x>2')
assert np.array_equal(np.array(ak_field_gt_test), np.array([False, False, False, True]))

ev = Evaluator(testarr = test_arr)
ak_arr_gt_test = ev.evaluate('testarr.x>2')
assert np.array_equal(np.array(ak_arr_gt_test), np.array([False, False, False, True]))
