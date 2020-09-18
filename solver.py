import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
import math
from simpleeval import simple_eval
import fractions as frac
from classes import *

bot = Bot(command_prefix="!")

class_match = [('\[[0-9,\/\+\-\−]{1,}\][\+\−\-]t\*\[[0-9,\/\+\-\−]{1,}\]', Vectorized),
               ('\[[0-9\/\-\−]{0,}[\+\-\−]?[0-9]{0,}[\*⋅]?t[\+\-\−]?[0-9\/\-\−]{0,},[0-9\/\-\−]{0,}[\+\-\−]?[0-9\/]{0,}[\*⋅]?t[\+\-\−]?[0-9\/\-\−]{0,}\]', Parameterized),
               ('y=[0-9\/\-\−]{0,}x?[\+\−\-]?[0-9\/\-\−]{0,}', SlopeY),
               ('[0-9\/\-\−]{1,}?\*?[xy][\+\-\−][0-9\/\-\−]{1,}?\*?[xy][\+\-\−]?[0-9\/\-\−]{0,}(=0)?', Cartesian)]


def generic_parse(s):
	s = clean(s)
	for m, c in class_match:
		if (re.match(m, s) is not None):
			return c.parse(s)
	return -1


def rad_to_deg(n):
	return n*360/2/math.pi


#Bot commands

@bot.command()
async def cross(ctx, arg1:Vector.parse, arg2:Vector.parse):
	"""Finds cross product of two vectors.
								Usage: !dot [v1] [v2]
								Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	res = arg1.cross(arg2)
	if (res == -1):
		await ctx.send('`These vectors are likely not of size 3. Cross product does not exist for vectors of size 2 and has not been implemented for vectors of above size 3.`')
	else:
		await ctx.send('`{}`'.format(arg1.cross(arg2)))

@bot.command()
async def vecfrom2(ctx, p1:Vector.parse, p2:Vector.parse):
	"""Finds vectorized line equation from 2 points.
						Usage: !vecfrom2 [p1] [p2]
						Points must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(Vectorized.vec_from_2(p1, p2)))

@bot.command()
async def dot(ctx, v1:Vector.parse, v2:Vector.parse):
	"""Finds dot product of two vectors.
							Usage: !dot [v1] [v2]
							Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(v1.dot(v2)))

@bot.command()
async def ang(ctx, v1:generic_parse, v2:generic_parse):
	"""Finds acute angle between two lines.
			Usage: !ang [line1] [line2]
			Lines can be in Vectorized, Parametric, Slope y-intercept, or Cartesian forms."""

	res = v1.converter.dir.ang(v2.converter.dir)
	if (res >= math.pi/2):
		res = math.pi-res
	await ctx.send('`Acute Degrees: {}`'.format(rad_to_deg(res)))
	await ctx.send('`Acute Radians: {}`'.format(res))


@bot.command()
async def angv(ctx, v1:Vector.parse, v2:Vector.parse):
	"""Finds angle between two n-dimensional vectors.
				Usage: !angv [vector1] [vector2]
				Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""

	res = v1.ang(v2)
	await ctx.send('`Degrees: {}`'.format(rad_to_deg(res)))
	await ctx.send('`Radians: {}`'.format(res))

@bot.command()
async def intercepts(ctx, s:generic_parse):
	"""Finds x and y intercepts of line.
				Usage: !intercepts [line1]
				Lines can be in Vectorized, Parametric, Slope y-intercept, or Cartesian forms."""
	xi, yi = s.intercepts()
	await ctx.send('`x-intercept: {}`'.format(xi))
	await ctx.send('`y-intercept: {}`'.format(yi))

@bot.command()
async def tocartesian(ctx, s:generic_parse):
	"""Converts line to Cartesian form.
					Usage: !tocartesian [line1]
					Lines can be in Vectorized, Parametric, or Slope y-intercept form."""
	await ctx.send('`{}`'.format(s.converter.to_cartesian()))

@bot.command()
async def toparam(ctx, s:generic_parse):
	"""Converts line to Parametric form.
						Usage: !toparam [line1]
						Lines can be in Vectorized, Cartesian, or Slope y-intercept form."""
	await ctx.send('`{}`'.format(s.converter.to_param()))

@bot.command()
async def tovec(ctx, s:generic_parse):
	"""Converts line to Vectorized form.
						Usage: !tovec [line1]
						Lines can be in Cartesian, Parametric, or Slope y-intercept form."""
	await ctx.send('`{}`'.format(s.converter.to_vectorized()))

@bot.command()
async def toslopey(ctx, s:generic_parse):
	"""Converts line to Slope y-intercept form.
						Usage: !toslopey [line1]
						Lines can be in Vectorized, Parametric, or Cartesian form."""
	await ctx.send('`{}`'.format(s.converter.to_slopey()))

@bot.command()
async def cartfrom2(ctx, p1:Vector.parse, p2:Vector.parse):
	"""Finds Cartesian line equation from 2 points.
							Usage: !cartfrom2 [p1] [p2]
							Points must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(Vectorized.vec_from_2(p1, p2).converter.to_cartesian()))


@bot.event
async def on_ready():
	print("ready")


@bot.event
async def on_message(message):
	await bot.process_commands(message)
	pass



bot.run('no token for you')
