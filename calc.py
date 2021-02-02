import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
import math
from simpleeval import simple_eval
import fractions as frac
from classes import *

bot = Bot(command_prefix="!")

class_match = [('\[[0-9,\/\+\-\−]{1,}\][\+\−\-][st]\*\[[0-9,\/\+\-\−]{1,}\]', Vectorized),
               ('\[([0-9\/\-\−]{0,}[\+\-\−]?[0-9]{0,}[\*⋅]?[a-z][\+\-\−]?[0-9\/\-\−]{0,},){1,}[0-9\/\-\−]{0,}[\+\-\−]?[0-9\/]{0,}[\*⋅]?[a-z][\+\-\−]?[0-9\/\-\−]{0,}\]', Parameterized),
               ('y=[0-9\/\-\−]{0,}x?[\+\−\-]?[0-9\/\-\−]{0,}', SlopeY),
               ('[0-9\/\-\−]{0,}?\*?[xy][\+\-\−][0-9\/\-\−]{0,}?\*?[xy][\+\-\−]?[0-9\/\-\−]{0,}(=0)?', Cartesian)]

moodle_help_id = 0

variable_storage = {}
results = {}

def generic_parse(s):
	s = clean(s)
	for m, c in class_match:
		if (re.match(m, s) is not None):
			return c.parse(s)
	return -1


def rad_to_deg(n):
	return n*360/2/math.pi

def gcd(a,b):
	print(a, b)
	if (b == 0):
		return a
	if (abs(a) < abs(b)):
		return gcd(b, a)
	return gcd(b, a%b)
	

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
async def mag(ctx, v1:Vector.parse):
	await ctx.send('`{}`'.format(v1.mag()))

@bot.command()
async def sqm(ctx, v1:Vector.parse):
	await ctx.send('`{}`'.format(v1.sqmag()))

@bot.command()
async def projv(ctx, v1:Vector.parse, v2:Vector.parse):
	await ctx.send('`{}`'.format(v1.projon(v2)))
	
@bot.command()
async def proj(ctx, v1:Vector.parse, v2:generic_parse):
	"""Finds projection of point onto a line.
								Usage: !proj [p1] [line1]
								Points must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]
								Lines can be in Vectorized, Parametric, Slope y-intercept, or Cartesian forms."""
	vecform = v2.converter.to_vectorized()
	p1 = v1-vecform.pos
	res = p1.projon(vecform.dir)+vecform.pos
	await ctx.send('`{}`'.format(res))
	
@bot.command()
async def dist(ctx, p1:Vector.parse, p2:Vector.parse):
	m = (p2-p1).sqmag()
	await ctx.send('`sqrt({})`'.format(m))
	
@bot.command()
async def mul(ctx, p1:Vector.parse, c:frac.Fraction):
	await ctx.send('`{}`'.format(p1*c))
	
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
	"""Finds all intercepts of n-dimensional line.
				Usage: !intercepts [line1]
				Lines can be in Vectorized, Parametric, Slope y-intercept, or Cartesian forms."""
	i1 = s.intercepts()
	for n, v in i1:
		await ctx.send('`{}-intercept: {}`'.format(n, v))

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

@bot.command()
async def sub(ctx, p1:Vector.parse, p2:Vector.parse):
	"""Subtracts two vectors.
									Usage: !sub [v1] [v2]
									Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(p1-p2))

@bot.command()
async def add(ctx, p1:Vector.parse, p2:Vector.parse):
	"""Adds two vectors.
									Usage: !add [v1] [v2]
									Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(p1+p2))

@bot.command()
async def midpoint(ctx, p1:Vector.parse, p2:Vector.parse):
	"""Finds midpoint of 2 points.
									Usage: !midpoint [p1] [p2]
									Points must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format((p1+p2)/2))

@bot.command()
async def perp(ctx, p1:Vector.parse):
	"""Finds perpendicular vector from a vector.
									Usage: !perp3 [v1]
									Vectors must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	await ctx.send('`{}`'.format(p1.perp()))

@bot.command()
async def perp3(ctx, p1:Vector.parse, p2:Vector.parse, p3:Vector.parse):
	"""Finds perpendicular vector from 3 points.
								Usage: !perp3 [p1] [p2] [p3]
								Points must be a comma separated list surrounded by square brackets, without spaces. E.g [1,2,3]"""
	l1 = p1-p2
	l2 = p2-p3
	res = l1.cross(l2)
	await ctx.send('`{}`'.format(res))

@bot.command()
async def tovectemp(ctx, p1:ParameterizedPlane.parse):
	res = p1.tovec()
	await ctx.send('`{}`'.format(res))


@bot.command()
async def simplify(ctx, p1:Vector.parse):
	tot_gcd = gcd(p1.coords[0], p1.coords[1])
	for i in p1.coords[2:]:
		tot_gcd = gcd(tot_gcd, i)
	res = p1/tot_gcd
	await ctx.send('`{}`'.format(res))
	
	
@bot.command()
async def intersection(ctx, l1:generic_parse, l2:generic_parse):
	res = l1.intersection(l2)
	await ctx.send('`{}`'.format(res))

@bot.command()
async def trianglecalc(ctx, s):
	A = Vector([int(s[0]), -int(s[1]), int(s[2])])
	B = Vector([-int(s[3]), int(s[4]), -int(s[5])])
	C = Vector([int(s[6]), -int(s[7]), int(s[8])])
	AB = B - A
	AC = C - A
	BC = C - B
	perim = [AB.sqmag(), AC.sqmag(), BC.sqmag()]
	perim_exact = AB.mag() + AC.mag() + BC.mag()
	angA = rad_to_deg(math.acos((BC.sqmag()-AB.sqmag()-AC.sqmag())/(-2*AB.mag()*AC.mag())))
	area = (AB.cross(AC).sqmag()) #remember to re div by 2!!!
	area_exact = (AB.cross(AC).mag())/2
	volume = abs((A.dot(B.cross(C)))/6)
	median_lineA = Vectorized.vec_from_2(A, (B+C)/2)
	median_lineA.integerize()
	median_lineB = Vectorized.vec_from_2(B, (A+C)/2)
	centroid = median_lineA.intersection(median_lineB)
	cartesian = CartesianPlane.from3(A,B,C)
	distorigin = 3*volume/area_exact
	distoriginexact = [3*volume*2, area]
	perp = AB.cross(AC)
	altitudeA = Vectorized(A, perp.cross(BC))
	altitudeA.integerize()
	altitudeB = Vectorized(B, perp.cross(AC))
	orthocenter = altitudeA.intersection(altitudeB)
	perpbiBC = Vectorized((B+C)/2, perp.cross(BC))
	perpbiBC.integerize()
	perpbiAC = Vectorized((A+C)/2, perp.cross(AC))
	circum = perpbiAC.intersection(perpbiBC)
	KH = orthocenter - circum
	KG = centroid - circum
	print(KH - KG*3)
	#assert (KH - KG*3).coords == [0]*len((KH - KG*3).coords)
	eulerline = Vectorized(circum, KH)
	eulerline.integerize()
	results_list = [A,B,C,AB] + perim + [perim_exact, angA, area, area_exact, volume, median_lineA, centroid, cartesian]
	results_list2 = [distorigin] + distoriginexact + [altitudeA, orthocenter, perpbiBC, circum, eulerline]
	await ctx.send('```A: {}\nB: {}\nC: {}\nAB: {}\nExact Perimeter: sqrt({}) + sqrt({}) + sqrt({})\nPerimeter: {}\nAngle at A: {}\nExact Area: sqrt({})/2\nArea: {}\nVolume: {}\nMedian line from A: {}\nCentroid: {}\nCartesian Equation: {}\n```'.format(*results_list))
	await ctx.send('```Distance from origin: {}\nExact Distance from origin: {}/sqrt({})\nAltitude from A: {}\nOrthocenter: {}\nPerpendicular bisector of BC: {}\nCircumcenter: {}\nEuler line: {}```'.format(*results_list2))
@bot.command()
async def sethelp(ctx):
	global moodle_help_id
	g = ctx.guild
	memp = g.get_member(ctx.author.id).guild_permissions.administrator
	
	if memp:
		channel = ctx.message.channel_mentions[0]
		moodle_help_id = channel
		print(type(moodle_help_id))
		await ctx.send('Channel set!')
	else:
		await ctx.send('You do not have proper permissions.')

@bot.command()
async def format(ctx, n:int):
	global moodle_help_id
	counter = 0
	people_list = ctx.message.mentions
	messages = []
	print(moodle_help_id)
	print(type(moodle_help_id))
	async for message in moodle_help_id.history(limit=200):
		if (counter >= n):
			break
		if message.author in people_list:
			counter += 1
			messages.append(message)
	print(messages)
	final_str = ''.join(['{}: {}\n'.format(m.author.name, m.content) for m in messages])
	await ctx.send('```{}```'.format(final_str))
#	pass


@bot.event
async def on_ready():
	print("ready")


@bot.event
async def on_message(message):
	await bot.process_commands(message)
	pass



bot.run('No token for you')
