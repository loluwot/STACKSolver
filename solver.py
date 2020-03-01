import sympy as sp
import math
from sympy.abc import x, y
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations, implicit_multiplication_application)
import re
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get
bot = Bot(command_prefix="!")
def process_exp(string):
	string = string.replace('\\', '').replace('⋅', '*').replace('−', '-').replace('^', '**')
	pattern_exp = re.compile('([)x])(\d)')
	string = pattern_exp.sub(r'\1**\2', string)

	transformations = (standard_transformations + (implicit_multiplication_application, ))
	return parse_expr(string, transformations=transformations)
def reverse_exp(string):
	new_str = string.replace('**', '^')
	return new_str

def constdiff(arr):
	temp = []
	deg = 0
	while len(arr) > 0:
		temp = [arr[i+1]-arr[i] for i in range(len(arr)-1)]
		all_zero = True
		for val in temp:
			all_zero = all_zero and val==0
		if all_zero:
			return arr[0], deg
		print(temp)
		deg += 1
		arr = list(temp)
	return (arr[0], deg)

def gen_n_poly(n):
	arr = [i for i in range(n+1)]
	coeff = sp.symbols(' '.join(arr))
	x = sp.symbols('x')
	expr = 0
	for i in range(n+1):
		expr += coeff[i]*x**i
	print(expr)
	return expr

@bot.event
async def on_ready():
	print("ready")

@bot.command()
async def expand(ctx, *, arg):
	"""Expands a polynomial expressed in factored form.
		Usage: !expand [expr]
		expr should be directly copied from moodle, should look like −2⋅x⋅(x+1)⋅(x+2)2"""
	await ctx.send('```'+reverse_exp(str(sp.expand(process_exp(arg)))) + '```')

@bot.command()
async def factor(ctx, *, arg):
	"""Factors a polynomial expressed in standard form.
		Usage: !factor [expr]
		expr should be directly copied from moodle, should look like −2⋅x4−10⋅x3−16⋅x2−8⋅x"""
	await ctx.send('```' + reverse_exp(str(sp.factor(process_exp(arg)))) + '```')

@bot.command()
async def ndiff (ctx, n1, diff1, n2, diff2):
	"""Calculates constant difference of f(x)g(x) given differences of f(x) and g(x)
		Usage: !ndiff [n1] [diff1] [n2] [diff2]
		n1 is order of difference of f(x)
		diff1 is constant difference of f(x)
		n2 is order of difference of g(x)
		diff2 is constant difference of g(x)"""
	n1 = int(n1)
	n2 = int(n2)
	diff1 = int(diff1)
	diff2 = int(diff2)
	ans = str(math.factorial(n1+n2)*diff1*diff2//(math.factorial(n1)*math.factorial(n2)))
	await ctx.send('```' + ans + '```')

@bot.command()
async def describe(ctx, *, arg):
	"""Describes a polynomial expressed in standard form.
		Usage: !describe [expr]
		expr should be directly copied from moodle, should look like −2⋅x4−10⋅x3−16⋅x2−8⋅x
		Will return all required characteristics, like leading term and degree"""
	expr = process_exp(arg)
	pol = sp.Poly(expr)
	await ctx.send('```Degree: ' + str(pol.degree()) + '```')
	await ctx.send('```Leading Coefficient: ' + str(pol.LC()) + '```')
	await ctx.send('```Leading Term: ' + reverse_exp(str(sp.LT(expr))) + '```')
	await ctx.send('```Constant Term / y-intercept: ' + str(expr.subs(x, 0)) + '```')

@bot.command()
async def seqtoleading(ctx, *ints):
	"""Calculates leading term given a sequence of y values
		Usage: !seqtoleading [n1] [n2] ...
		n1, n2 ... should express the sequence of y values"""
	ints = list(map(int, ints))
	diff, deg = constdiff(ints)
	lc = diff//math.factorial(deg)
	await ctx.send('```{}*x^{}```'.format(lc, deg))
@bot.command()
async def reflection(ctx, expr, line):
	"""Reflects a function across a line.
		Usage: !reflection [expr] [line]
		expr is the expression you would like to reflect
		line is the line you want to reflect across (e.g. x=1)"""
	a = int(line[2:])
	expr = process_exp(expr)

	if line[0] == 'x':
		await ctx.send('```'+reverse_exp(str(expr.subs(x, -x+2*a).expand())) + '```')
	else:
		await ctx.send('```' + reverse_exp(str((-1*expr + 2*a).expand())) + '```')
@bot.command()
async def composition(ctx, f, g):
	expr1 = process_exp(f)
	expr2 = process_exp(g)
	await ctx.send('```' + reverse_exp(str(expr1.subs(x, expr2).expand()))+ '```')

@bot.command()
async def reversecomp (ctx, h, f):
	expr1 = process_exp(h)
	expr2 = process_exp(f)
	y = sp.symbols('y')
	expr3 = expr2.subs(x, y)-expr1
	print(sp.solve(expr3, y))
	await ctx.send('```' + ', '.join(list(map(str, sp.solve(expr3, y)))) + '```')

@bot.command()
async def polydivide(ctx, *args):
	"""Calculates the quotient and remainder of f(x)/g(x).
		Usage: !polydivide [f] [g] [optional: d]
		f is the dividend
		g is the divisor
		d is the domain of the coefficients (integer or rational). Defaults to integer."""
	d = 'ZZ'
	if (len(args) > 2 and args[2].lower() == 'rational'):
		d = 'QQ'
	f = process_exp(args[0])
	g = process_exp(args[1])
	q, r = sp.div(f.as_poly(), g.as_poly(), domain=d)
	await ctx.send('```Quotient: ' + reverse_exp(str(q.as_expr())) + '```')
	await ctx.send('```Remainder: ' + reverse_exp(str(r.as_expr())) + '```')

# @bot.command()
# async def polysolve(ctx, f, g, type1, type2, solve1, solve2):
# 	"""Calculates possible missing expressions for divisor, quotient, remainder, or dividend. Can solve for 2 or less missing.
# 		Usage: !polysolve [f] [g] [type1] [type2] [solve1] [solve2]
# 		f is the first given expression
# 		g is the second given expression
# 		type1 is the type of the expression f is (divisor, quotient, remainder, dividend)
# 		type2 is the type of expression g is (divisor, quotient, remainder, dividend)
# 		solve1 is one of the expressions to solve for (divisor, quotient, remainder, dividend)
# 		solve2 is the other expression to solve for (divisor, quotient, remainder, dividend)
# 		"""
# 	arr = [type1, type2]
# 	arr.sort()
# 	if (arr == ['divisor', 'quotient']):
#

bot.run("no u")
