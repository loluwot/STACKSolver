import math
from simpleeval import simple_eval
import fractions as frac
import re



def clean(s):
	return s.replace('−', '-').replace('⋅', '*').strip()





class Vector:
	def __init__(self, coords):
		self.coords = [frac.Fraction(x) for x in coords]

	def __add__(self, other):
		return Vector([x1+x2 for x1, x2 in zip(self.coords, other.coords)])

	def __neg__(self):
		return Vector([-x for x in self.coords])

	def __sub__(self, other):
		return self + -other

	def __str__(self):
		return (('[' + '{},'*len(self.coords))[:-1] + ']').format(*self.coords)

	@staticmethod
	def parse(s):
		s = ' ' + s + ' '
		# print(s)
		s = s.split('[')[1].split(']')[0]
		nums = s.split(',')
		nums = [frac.Fraction(clean(n)) for n in nums]
		return Vector(nums)

	def mag(self):
		return math.sqrt(sum([x**2 for x in self.coords]))

	def dot(self, vec2):
		return sum([x*y for x, y in zip(self.coords, vec2.coords)])

	def ang(self, vec2):
		return math.acos(self.dot(vec2)/(self.mag()*vec2.mag()))

	def cross(self, vec2):
		if len(vec2.coords) != 3:
			return -1
		return Vector([self.coords[1]*vec2.coords[2]-self.coords[2]*vec2.coords[1], -(self.coords[0]*vec2.coords[2] - self.coords[2]*vec2.coords[0]), self.coords[0]*vec2.coords[1]-self.coords[1]*vec2.coords[0]])

	def perp(self):
		if len(self.coords) == 2:
			return Vector([self.coords[1], -self.coords[0]])

		elif len(self.coords) == 3:
			return self.cross(self + Vector([0, 0, 1]))

		return -1


class Vectorized:
	def __init__(self, pos, dir):
		self.pos = pos
		self.dir = dir
		self.converter = Converter(pos=pos, dir=dir)

	def __str__(self):
		return '{}+t*{}'.format(self.pos, self.dir)

	@staticmethod
	def parse(s):
		s = clean(s)
		vecs = s.split('+')
		pos = Vector.parse(vecs[0])
		dir = Vector.parse(vecs[1][2:])
		return Vectorized(pos, dir)

	@staticmethod
	def vec_from_2(vec1, vec2):
		pos = vec1
		dir = vec2 - vec1
		return Vectorized(pos, dir)

	def intercepts(self):
		return self.converter.to_slopey().intercepts()


class Parameterized:
	def __init__(self, eqs):
		self.eqs = eqs
		self.converter = Converter(eqs=eqs)

	def __str__(self):
		st = ['{}+t*{}'.format(p, d) for p,d in self.eqs]
		return (('[' + '{},'*len(st))[:-1] + ']').format(*st)

	@staticmethod
	def parse(s):
		s = ' ' + s + ' '
		# print(s)
		s = s.split('[')[1].split(']')[0]
		arr = s.split(',')
		arr = [clean(x) for x in arr]
		pos = Vector([simple_eval(x.replace('t', '0')) for x in arr])
		dir = Vector([simple_eval(x.replace('t', '1')) for x in arr]) - pos

		eqs = [[p, d] for p, d in zip(pos.coords, dir.coords)]

		return Parameterized(eqs)

	def intercepts(self):
		return self.converter.to_slopey().intercepts()


class Cartesian:

	def __init__(self, l):
		self.coeff = [frac.Fraction(x) for x in l]
		self.converter = Converter(coeff=self.coeff)

	def __str__(self):
		return '{}*x + {}*y + {}'.format(*self.coeff)

	@staticmethod
	def parse(s):
		if ('=' in s):
			s = s.split('=')[0]
		s = clean(s)
		c = simple_eval(s.replace('x', '0').replace('y', '0'))
		a = simple_eval(s.replace('y', '0').replace('x', '1')) - c
		b = simple_eval(s.replace('x', '0').replace('y', '1')) - c

		return Cartesian([a, b, c])

	def intercepts(self):
		return self.converter.to_slopey().intercepts()


class SlopeY:

	def __init__(self, m, b):
		self.m = frac.Fraction(m)
		self.b = frac.Fraction(b)
		self.converter = Converter(m=m, b=b)

	@staticmethod
	def parse(s):
		s = clean(s)
		if ('y=' in s):
			s = s.split('=')[1]
		b = simple_eval(s.replace('x', '0'))
		m = simple_eval(s.replace('x', '1'))-b

		return SlopeY(m, b)

	def intercepts(self):
		return -self.b/self.m, self.b

	def __str__(self):
		return 'y = {}*x + {}'.format(self.m, self.b)

class Converter:

	def __init__(self, pos=None, dir=None, coeff=None, m=None, b=None, eqs=None):
		attr = ['pos', 'dir', 'coeff', 'm', 'b', 'eqs'] # add new attributes at the end to ensure backwards compat
		#       1      2      4        8    16   32
		arr = locals()
		given = int(''.join([str(int(arr[s] is not None)) for s in attr][::-1]), 2) # binary representation of given attributes
		print(given)
		if given == 32:
			self.pos, self.dir = Vector([x[0] for x in eqs]), Vector([x[1] for x in eqs])

		elif given == 3:
			self.pos, self.dir = pos, dir

		elif given == 4:
			self.pos, self.dir = Vector([-coeff[2]/coeff[0], 0]), Vector([-coeff[1]/coeff[0], 1])

		elif given == 24:
			self.pos, self.dir = Vector([0, b]), Vector([m.denominator, m.numerator])

		# conversion here
		self.m = self.dir.coords[1] / self.dir.coords[0]
		tx = (-self.pos.coords[0]) / (self.dir.coords[0])
		self.b = tx * self.dir.coords[0] + self.pos.coords[1]
		self.eqs = [[p, d] for p, d in zip(self.pos.coords, self.dir.coords)]
		normal = self.dir.perp()
		c = -(normal.dot(self.pos))
		self.coeff = normal.coords + [c]

	#to classes

	def to_cartesian(self):
		return Cartesian(self.coeff)

	def to_vectorized(self):
		return Vectorized(self.pos, self.dir)

	def to_slopey(self):
		return SlopeY(self.m, self.b)

	def to_param(self):
		return Parameterized(self.eqs)

