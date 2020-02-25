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
	if ('⋅' in string or '−' in string and '^' not in string):
		new_str = string.replace('⋅', '*').replace('−', '-')
		pattern_exp = re.compile('([)x])(\d)')
		new_str = pattern_exp.sub(r'\1**\2', new_str)
		return parse_expr(new_str)
	else:
		new_str = string.replace('^', '**')
		transformations = (standard_transformations + (implicit_multiplication_application, ))
		return parse_expr(new_str, transformations=transformations)
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
	"""Calculates leading term given a sequence
		Usage: !seqtoleading [n1] [n2] ...
		n1, n2 ... should express the sequence of y values"""
	ints = list(map(int, ints))
	diff, deg = constdiff(ints)
	lc = diff//math.factorial(deg)
	await ctx.send('```{}*x^{}```'.format(lc, deg))
@bot.command()
async def reflection(ctx, arg, line):
	a = int(line[2:])
	expr = process_exp(arg)

	if line[0] == 'x':
		await ctx.send('```'+reverse_exp(str(expr.subs(x, -x+2*a).expand())) + '```')
	else:
		await ctx.send('```' + reverse_exp(str((-1*expr + 2*a).expand())) + '```')
# @bot.command()
# async def composition(ctx, expr1, expr2):


bot.run("no u")
