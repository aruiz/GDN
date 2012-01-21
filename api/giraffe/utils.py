# -*- coding: utf-8 -*-

from xml.sax.saxutils import escape, quoteattr

def camelcase2upper (name):
	"""
	Converts CamelCase to CAMEL_CASE
	"""
	result = ""
	for i in range(len(name) - 1) :
		if name[i].islower() and name[i+1].isupper():
			result += name[i].upper() + "_"
		else:
			result += name[i].upper()
	result += name[-1].upper()
	return result

def camelcase2lower (name):
	"""
	Converts CamelCase to camel_case
	"""
	return camelcase2upper(name).lower()

class HTMLWriter:
	"""
	Example:
	    >>> w = HTMLWriter (sys.stdout)
	    >>> w.a("Click here", href="http://example.com", klass="myclass")
	    <a href="http://example.com">Click here</a>
	    
	"""

	class Curry:
		"""Pasted from verbatim from http://www.python.org/dev/peps/pep-0309/#id23"""
		def __init__(*args, **kw):
		    self = args[0]
		    self.fn, self.args, self.kw = (args[1], args[2:], kw)

		def __call__(self, *args, **kw):
		    if kw and self.kw:
		        d = self.kw.copy()
		        d.update(kw)
		    else:
		        d = kw or self.kw
		    return self.fn(*(self.args + args), **d)
	
	def __init__ (self, stream):
		self._stream = stream
		
		self._ops = {}
		for tag in ("h1", "h2", "h3", "h4", "h5", "p", "div", "span", "a", "img"):
			self._ops[tag] = HTMLWriter.Curry (self.write_tag, tag)
			self._ops["start_"+tag] = HTMLWriter.Curry (self.start_tag, tag)
			self._ops["end_"+tag] = HTMLWriter.Curry (self.end_tag, tag)
		
		self._newline_start_tags = set(("p", "div"))
		self._newline_end_tags = set(("h1", "h2", "h3", "h4", "h5", "p", "div"))
	
	def __getattr__ (self, name):
		try:
			return self._ops[name]
		except KeyError:
			raise AttributeError, name
	
	def br (self):
		self._stream.write ("<br/>\n")
	
	def hr (self):
		self._stream.write ("<hr/>\n")
	
	def start_tag (self, tag, **attribs):
		if attribs.has_key("klass"):
			attribs["class"]=attribs["klass"]
			del attribs["klass"]
		attribs_string = " ".join (map(lambda v: '%s=%s' % (v[0], quoteattr(v[1])), attribs.items()))
		if attribs:
			self._stream.write ("<%s %s>" % (tag, attribs_string))
		else:
			self._stream.write ("<%s>" % tag)
		
		if tag in self._newline_start_tags:
			self._stream.write ("\n");
	
	def end_tag (self, tag):
		self._stream.write ("</%s>" % tag)
		
		if tag in self._newline_end_tags:
			self._stream.write ("\n");
	
	def write_tag (self, tag, contents="", **attribs):
		self.start_tag (tag, **attribs)
		self._stream.write (escape(contents))
		self.end_tag(tag)
	
	def write (self, contents):
		self.write_raw (escape(contents))
	
	def raw (self, data):
		self._stream.write (data)

