#!/usr/bin/env python
from include import *

class Node:
	pass

class Leaf(Node):
	def __init__(self, keyword):
		self.keyword = keyword
	def Eval(self):
		result = SearchKeyword(self.keyword)
		#print 'Leaf "%s" Eval(): ' % self.keyword, result
		return result
	def String(self):
		return self.keyword
	
class Not(Node):
	def __init__(self, child):
		self.child = child
	def Eval(self):
		result = [x for x in lib.modules if x not in self.child.Eval()]
		#print 'Not Eval(): ', result
		return result
	def String(self):
		return 'Not(%s)' % self.child.String()

class And(Node):
	def __init__(self, child1, child2):
		self.child1 = child1
		self.child2 = child2
	def Eval(self):
		result = [x for x in self.child1.Eval() if x in self.child2.Eval()]
		#print 'And Eval(): ', result
		return result
	def String(self):
		return 'And(%s, %s)' % (self.child1.String(), self.child2.String())
		

class Or(Node):
	def __init__(self, child1, child2):
		self.child1 = child1
		self.child2 = child2
	def Eval(self):
		result = []
		for x in self.child1.Eval() + self.child2.Eval():
			if x not in result:
				result.append(x)
		#print 'Or Eval(): ', result
		return result
	def String(self):
		return 'Or(%s, %s)' % (self.child1.String(), self.child2.String())

def Search(expression):
	priority = ['', '|', '&', '!', '('] # '' won't be there (filtered in Split())
	depth = 0
	nodes = []
	operators = [] # determined by priority (mod 4 gives index in priority list)
	expression = filter(None, [x.strip() for x in re.split('([!|& \(\)<>=])', expression)])
	for x in expression:
		# first normalize operators (&&, &, and) ...
		if x.lower() in ['&&', 'and']:
			x = '&'
		if x.lower() in ['||', 'or']:
			x = '|'
		if x.lower() in ['not']:
			x = '!'
		
		#now build a tree
		if x == ')': 
			depth -= 1
			if depth < 0:
				log.err('Your query is broken (brackets in wrong order).')
				return []
		elif x in priority: # operand
			# use parameters with lower priority
			while len(operators) > 0 and (4 * depth + priority.index(x)) < operators[-1]:
				if operators[-1] % 4 == 1: # OR
					if len(nodes)<2:
						log.err('Your query is broken (missing OR operands).')
						return []
					nodes.append(Or(nodes.pop(), nodes.pop()))
					operators.pop()
				elif operators[-1] % 4 == 2: # AND
					if len(nodes)<2:
						log.err('Your query is broken (missing AND operands).')
						return []
					nodes.append(And(nodes.pop(), nodes.pop()))
					operators.pop()
				elif operators[-1] % 4 == 3: # NOT
					if len(nodes)<1:
						log.err('Your query is broken (missing NOT operand).')
						return []
					nodes.append(Not(nodes.pop()))
					operators.pop()
				else: # (
					log.err('Your query is broken (undefined behaviour).')
			# push operator priority
			if priority.index(x) % 4 == 0:
					depth += 1
			else:
				operators.append(4 * depth + priority.index(x))
		else: # operand
			nodes.append(Leaf(x))
	# everything processed, use remaining operators
	while len(operators) > 0:
		if operators[-1] % 4 == 1: # OR
			if len(nodes)<2:
				log.err('Your query is broken (missing OR operands).')
				return []
			nodes.append(Or(nodes.pop(), nodes.pop()))
			operators.pop()
		elif operators[-1] % 4 == 2: # AND
			if len(nodes)<2:
				log.err('Your query is broken (missing AND operands).')
				return []
			nodes.append(And(nodes.pop(), nodes.pop()))
			operators.pop()
		elif operators[-1] % 4 == 3: # NOT
			if len(nodes)<1:
				log.err('Your query is broken (missing NOT operand).')
				return []
			nodes.append(Not(nodes.pop()))
			operators.pop()
	if depth != 0:
		log.err('Your query is broken (brackets are not paired).')
		return []
	if len(nodes) != 1:
		log.err('Your query is broken (too many operands).')
		return []
	#print nodes[0].String()
	return nodes[0].Eval()


def SearchKeyword(keyword, moduleonly=False):
	if keyword[0] in ['>', '<', '='] and len(keyword[1:]) == 4 and keyword[1:].isdigit():
		# that is year query
		year = int(keyword[1:])
		by_year = []
		for m in lib.modules:
			myear = int(lib.modules[m].date[:4]) if lib.modules[m].date[:4].isdigit() else 0
			if (keyword[0] == '<' and myear <= year) or (keyword[0]=='>' and myear>=year) or (keyword[0]=='=' and myear==year):
				by_year.append(m)
		return by_year

	else: # normal query
		modules = lib.modules
		
		# in module (or abbreviation)
		by_tag = []
		by_parameter = []
		by_author = []
		by_kb = []
		by_dependency = []
		by_version = []
		by_module = SearchAbbr(keyword, modules.keys()) + [x for x in modules if keyword in x]

		if not moduleonly:
			# in tags
			by_tag = [x for x in modules if keyword in modules[x].tags]
			
			# in parameters
			by_parameter = [x for x in modules if keyword in modules[x].parameters]
		
			# in authors
			by_author = [x for x in modules for authors in modules[x].authors if keyword in authors.name or keyword in authors.email or keyword in authors.web]
		
			# in kb
			by_kb = [x for x in modules if keyword.upper() in modules[x].kb_access]

			# in dependencies (or abbreviations)
			by_dependency = [x for x in modules if len(SearchAbbr(keyword, modules[x].dependencies.keys())) > 0]

			# in version
			by_version = [x for x in modules if keyword == modules[x].version]
		
		# union everything and return
		total = []
		for x in by_module + by_tag + by_parameter + by_author + by_kb + by_dependency + by_version:
			if x not in total:
				total.append(x)
		return total

def SearchAbbr(keyword, data):
	ref_parts = filter(None, keyword.split('.'))
	parts = {}
	# select all modules with more or equal parts than the searched expression
	for i in data:
		p = filter(None, i.split('.'))
		if len(ref_parts) <= len(p): 
			parts[i]=p
	
	# find matching modules for each part
	toremove = []
	for p in parts: # for each splitted module name
		for i in range(0, len(ref_parts)): # for the number of parts in query
			if parts[p][i][:len(ref_parts[i])] != ref_parts[i]: # discrepancy on the ith part
				toremove.append(p)
				break
	for p in toremove:
		del parts[p]
	return parts.keys()

