# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 noexpandtab:

import sys
import logging
from itertools import chain
from xml.etree import ElementTree 
from xml.etree.ElementTree import XML
from giraffe.utils import camelcase2lower

class ETreeNamespace:
	
		def __init__ (self, ns):
			self._ns = ns
		
		def __getattr__ (self, name):
			return "{%s}%s" % (self._ns, name)
		
		def __getitem__ (self, name):
			return "{%s}%s" % (self._ns, name)

GIR = ETreeNamespace ("http://www.gtk.org/introspection/core/1.0")
C = ETreeNamespace ("http://www.gtk.org/introspection/c/1.0")
GLIB = ETreeNamespace ("http://www.gtk.org/introspection/glib/1.0")

BUILTINS = [
	{ "name" : "gpointer", "c_type" : "gpointer", "pyname" : "gpointer" },
	{ "name" : "gboolean", "c_type" : "gboolean", "pyname" : "bool" },
	{ "name" : "gint",     "c_type" : "gint",     "pyname" : "int" },
	{ "name" : "gint8",    "c_type" : "gint8",    "pyname" : "int" },
	{ "name" : "gint16",   "c_type" : "gint16",   "pyname" : "int" },
	{ "name" : "gint32",   "c_type" : "gint32",   "pyname" : "int" },
	{ "name" : "gint64",   "c_type" : "gint64",   "pyname" : "int" },
	{ "name" : "guint",    "c_type" : "guint",    "pyname" : "int" },
	{ "name" : "guint8",   "c_type" : "guint8",   "pyname" : "int" },
	{ "name" : "guint16",  "c_type" : "guint16",  "pyname" : "int" },
	{ "name" : "guint32",  "c_type" : "guint32",  "pyname" : "int" },
	{ "name" : "guint64",  "c_type" : "guint64",  "pyname" : "int" },
	{ "name" : "glong",    "c_type" : "glong",    "pyname" : "int" },
	{ "name" : "gulong",   "c_type" : "gulong",   "pyname" : "int" },
	{ "name" : "GType",    "c_type" : "GType",    "pyname" : "GType" },
	{ "name" : "gfloat",   "c_type" : "gfloat",   "pyname" : "float" },
	{ "name" : "gdouble",  "c_type" : "gdouble",  "pyname" : "float" },
	{ "name" : "utf8",     "c_type" : "gchar*",    "pyname" : "string" },
	{ "name" : "filename", "c_type" : "gchar*",    "pyname" : "bytearray" },
	{ "name" : "none",     "c_type" : "void",     "pyname" : "void" },
	{ "name" : "va_list",  "c_type" : "va_list",  "pyname" : "va_list" },
]
BUILTINS_NAMES = dict ([(b["name"],b) for b in BUILTINS])

class Node :
	def __init__ (self, element, parent):
		self._attribs = element.attrib
		self._element = element

		if parent is None or isinstance (parent, Node):
			self._parent = parent
		else:
			raise TypeError, "Parent node must be a %s" % Node
	
	def __getattr__ (self, name):
		attrib_name = None
		if name.startswith ("glib_"):
			attrib_name = GLIB[name[5:]]
		elif name.startswith ("c_"):
			attrib_name = C[name[2:]]
		else:
			attrib_name = name
		
		try:
			val = self._attribs[attrib_name]
			return val
		except KeyError:
			raise AttributeError, "%s(%s) does not have an attribute '%s'" % (self.__class__, self.name, name)
	
	@property
	def name (self):
		try:
			return self._attribs["name"]
		except KeyError:
			return "unknown_" + self._element.tag
	
	@property
	def namespaced_name (self):
		if self.parent_node is None or isinstance(self.parent_node, Repository): return self.name
		return self.parent_node.namespaced_name + "." + self.name
	
	@property
	def parent_node (self):
		return self._parent
	
	@property
	def doc (self):
		return "\n".join (map(lambda elt : elt.text, self._element.findall (GIR.doc)))
	
	@property
	def namespace (self):
		ns = self.parent_node
		if ns is None : return None
		while not isinstance (ns, Namespace):
			ns = ns.parent_node
		return ns
	
	@property
	def introspectable (self):
		try:
			return self._attribs["introspectable"] != "0"
		except KeyError:
			return True
	
	def html_anchor (self, contents="", klass=""):
		return '<span class="anchor-%s " id="%s">%s</span>' % (self.__clas__.__name__, klass, self.anchor, contents)
	
	
	def html_link (self, contents=None, klass=""):
		return '<a class="link-%s %s" href="%s">%s</a>' % (self.__class__.__name__, klass, self.href, self.namespaced_name if contents is None else contents)
	
	@property
	def anchor (self):
		return self.namespaced_name
	
	@property
	def href (self):
		ns = self.namespace
		return "%s-%s.html#%s" % (ns.name, ns.version, self.anchor)
	
	def __str__ (self):
		if "name" in self._attribs:
			return "%s<%s>" % (str(self.__class__).rpartition(".")[2], str(self.name))
		else:
			return "%s<?>" % str(self.__class__).rpartition(".")[2]

class Callable (Node) :
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
		
		self._params = []
		params = element.findall (GIR.parameters+"/"+GIR.parameter)
		for p in params:
			p = Parameter (p, self)
			self._params.append (p)
		
		return_values = element.findall (GIR["return-value"])
		if len(return_values) != 1:
			raise ValueError, "%s does not have a return-value" % self
		self._return_value = ReturnValue (return_values[0], self)
	
	@property
	def parameters (self):
		return self._params
	
	@property
	def return_value (self):
		return self._return_value
	
	@property
	def c_identifier (self):
		if self._attribs.has_key (C.identifier):
			return self._attribs[C.identifier]
		else:
			return camelcase2lower(self.parent_node.c_type+"_"+self.name)
	
	def __str__ (self):
		return "%s<%s %s (%s)>" % (str(self.__class__).rpartition(".")[2], self.return_value, self.name, ", ".join (map (str, self.parameters)))

class Method (Callable) :
	def __init__ (self, element, parent, virtual=False, static=False):
		Callable.__init__ (self, element, parent)
		self._virtual = virtual
		self._static = static
	
	@property
	def virtual (self):
		return self._virtual
	
	@property
	def static (self):
		return self._static
	
	def __str__ (self):
		s = Callable.__str__ (self)
		return s if not self.virtual else s + " (virtual)"

class Signal (Callable) :
	def __init__ (self, element, parent):
		Callable.__init__ (self, element, parent)

class Type (Node):
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
	
	@property
	def is_array (self):
		return False
	
	@property
	def c_type (self):
		if C.type in self._attribs:
			return self._attribs[C.type]
		elif "c_type" in self._attribs:
			return self._attribs["c_type"]
		else:
			# Fall back to guesswork
			if self.name in BUILTINS_NAMES:
				return BUILTINS_NAMES[self.name]["c_type"]
			if not "." in self.name:
				return self.namespace.name + self.name
			return self.name.replace(".", "")
	
	@property
	def namespaced_name (self):
		if self.name in BUILTINS_NAMES:
			return self.name
		else:
			# Fall back to guesswork
			if "." in self.name:
				return self.name
			return self.namespace.name + "." + self.name
		

class VarArgs (Type):
	def __init__ (self, element, parent):
		Type.__init__ (self, element, parent)
	
	def __str__ (self):
		return "VarArgs<...>"
	
	@property
	def c_type (self):
		return "..."
	
	@property
	def namespaced_name (self):
		return "VarArgs"

class Array (Type):
	def __init__ (self, element, parent):
		Type.__init__ (self, element, parent)				
		
		# FIXME: We don't support nested arrays
		child_types = element.findall (GIR.type)
		if len(child_types) != 1:
			raise ValueError, "Array in %s does not have exactly one child type element" % self.parent_node
		
		self._child_type = Type (child_types[0], self)
		
		# Array elements does not have a 'name' attribute (which makes sense)
		# but for convenience of our API we add one anyway so we can guarantee
		# that Nodes always have a name
		self._attribs["name"] = "Array<%s>" % self._child_type.name
		
	@property
	def child_type (self):
		return self._child_type
	
	@property
	def is_array (self):
		return True
	
	@property
	def c_type (self):
		return self.child_type.c_type
	
	@property
	def namespaced_name (self):
		return "Array<%s>" % self.child_type.namespaced_name
	
	def __str__ (self):
		return "Array<%s>" % self._child_type.name

class Callback (Type, Callable):
	def __init__ (self, element, parent):
		Type.__init__ (self, element, parent)
		Callable.__init__ (self, element, parent)
	
class TypedNode (Node) :
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
		
		types = element.findall (GIR.type)
		if len(types) > 1:
			raise ValueError, "%s of %s more than one type element" % (self, self.parent_node)
		if len(types) == 0:
			arrays = element.findall (GIR.array)
			if len(arrays) == 0:
				varargs = element.findall (GIR.varargs)
				if len(varargs) == 0:
					callbacks = element.findall (GIR.callback)
					if len(callbacks) != 1:
						raise ValueError, "%s '%s' of %s '%s' does not have exactly one type-, array-, callback-, or varargs element" % (self.__class__, self.name, self.parent_node.__class__, self.parent_node.name)
					else:
						self._type  = Callback (callbacks[0], self)
				else:
					self._type = VarArgs (varargs[0], self)
			else:
				self._type = Array (arrays[0], self)
		else:
			self._type = Type (types[0], self)
		
		self._is_pointer = self.type.c_type.endswith("*")
		self._is_array = self.type.is_array
	
	def get_type (self):
		return self._type
	
	def set_type (self, typ):
		self._type = typ
	type = property (get_type, set_type)
	
	@property
	def name (self):
		return self._attribs["name"] if "name" in self._attribs else "?"
	
	@property
	def is_pointer (self):
		return self._is_pointer
	
	@property
	def is_array (self):
		return self._is_array
	
	def __str__ (self):
		return "%s@%s" % (self.type, self.name)

class Field (TypedNode) :
	def __init__ (self, element, parent):
		TypedNode.__init__ (self, element, parent)

class Parameter (TypedNode):
	def __init__ (self, element, parent):
		TypedNode.__init__ (self, element, parent)		
	
	@property
	def is_out (self):
		try:
			return self._attribs["direction"] == "out"
		except KeyError:
			return False	

class ReturnValue (Parameter) :
	def __init__ (self, element, parent):
		Parameter.__init__ (self, element, parent)
	
	@property
	def name (self):
		if "name" in self._attribs:
			return self._attribs["name"]
		else:
			return "return"

class Property (Field) :
	def __init__ (self, element, parent):
		Field.__init__ (self, element, parent)
	
	@property
	def writable (self):
		try:
			return bool (self._attribs["writable"])
		except KeyError:
			return False
	
	@property
	def construct_only (self):
		try:
			return bool (self._attribs["construct-only"])
		except KeyError:
			try:
				return bool (self._attribs["construct"])
			except KeyError:
				return False
			

class Value (Node):
	"""A litteral with a 'name' and a 'value' property"""
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
	
	def __str__ (self):
		return "Value<%s=%s>" % (self.name, self.value)
	
class Constructor (Method) :
	def __init__ (self, element, parent):
		Method.__init__ (self, element, parent)

class Enumeration (Type):
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
		
		self._members = []
		members = element.findall (GIR.member)
		for m in members:
			m = Value (m, self)
			self._members.append(m)
	
	@property
	def members (self):
		return self._members

class BitField (Enumeration):
	def __init__ (self, element, parent):
		Enumeration.__init__ (self, element, parent)
		
class Record (Type) :
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
		
		self._fields = {}
		fields = element.findall (GIR.field)
		for f in fields:
			f = Field (f, self)
			self._fields[f.name] = f
		
		self._callbacks = {}
		callbacks = element.findall (GIR.callback)
		for cb in callbacks:
			cb = Callback (cb, self)
			self._callbacks[cb.name] = cb
		
		self._methods = {}
		methods = element.findall (GIR.method)
		for m in methods:
			m = Method (m, self)
			self._methods[m.name] = m
		
		static_methods = element.findall (GIR.function)
		for m in static_methods:
			m = Method (m, self, static=True)
			self._methods[m.name] = m
	
	@property
	def fields (self):
		return list(self._fields.values())
	
	@property
	def callbacks (self):
		return list(self._callbacks.values())
	
	@property
	def methods (self):
		return list(self._methods.values())
	
	@property
	def disguised (self):
		try:
			return int(self._attribs["disguised"])
		except KeyError:
			return False
	
	@property
	def namespaced_name (self):
		return self.namespace.name + "." + self.name

class Class (Record) :
	def __init__ (self, element, parent):
		Record.__init__ (self, element, parent)
		
		self._props = {}
		props = element.findall (GIR.property)
		for p in props:
			p = Property (p, self)
			self._props[p.name] = p		
		
		self._ctors = {}
		ctors = element.findall (GIR.constructor)
		for ctor in ctors:
			ctor = Constructor (ctor, self)
			self._ctors[ctor.name] = ctor
		
		self._signals = {}
		signals = element.findall (GLIB.signal)
		for s in signals:
			s = Signal (s, self)
			self._signals[s.name] = s
		
		virtuals = element.findall (GIR["virtual-method"])
		for v in virtuals:
			v = Method (v, self, virtual=True)
			self._methods[v.name] = v
		
		# The interfaces will be added later once we can resolve them
		self._interfaces = set()
		self._subclasses = set()
		self._parent_class = None
	
	@property
	def constructors (self):
		return list(self._ctors.values())
	
	@property
	def properties (self):
		return list(self._props.values())
	
	@property
	def signals (self):
		return list(self._signals.values())
	
	@property
	def fields (self):
		return list(self._fields.values())

	@property
	def interfaces (self):
		return list(self._interfaces)
	
	@property
	def subclasses (self):
		return list(self._subclasses)
	
	@property
	def parent_class (self):
		return self._parent_class
	
	@property
	def is_abstract (self):
		try:
			return bool (self._attribs["abstract"])
		except KeyError:
			return False
	
	def implement_interface (self, interface):
		if not isinstance (interface, Interface):
			raise TypeError, "Expected giraffe.ast.Interface found %s" % interface.__class__
		self._interfaces.add (interface)
	
	def register_subclass (self, subclass):
		if not isinstance (subclass, Class):
			raise TypeError, "Expected giraffe.ast.Class found %s" % subclass.__class__
		self._subclasses.add (subclass)

class Interface (Class) :
	def __init__ (self, element, parent):
		Class.__init__ (self, element, parent)
		self._implementations = set()
	
	@property
	def implementations (self):
		return list(self._implementations)
	
	def register_implementation (self, klass):
		if not isinstance (klass, Class):
			raise TypeError, "Expected giraffe.ast.Class found %s" % klass.__class__
		self._implementations.add (klass)
	
	@property
	def is_abstract (self):
		return True

class Function (Callable) :
	def __init__ (self, element, parent):
		Callable.__init__ (self, element, parent)

class Namespace (Node):
	def __init__ (self, element, parent):
		Node.__init__ (self, element, parent)
		
		self._classes = {}
		classes = element.findall (GIR["class"])
		for cl in classes:
			try:
				cl = Class (cl, self)
				self._classes[cl.name] = cl
			except ValueError, e:
				logging.error ("Error parsing Class: %s" % e)
		
		self._ifaces = {}
		ifaces = element.findall (GIR.interface)
		for iface in ifaces:
			try:
				iface = Interface (iface, self)
				self._ifaces[iface.name] = iface
			except ValueError, e:
				logging.error ("Error parsing Interface: %s" % e)
		
		self._records = {}
		records = element.findall (GIR.record)
		for r in records:
			try:
				r = Record (r, self)
				self._records[r.name] = r
			except ValueError, e:
				logging.error ("Error parsing Record: %s" % e)
		
		self._enumerations = {}
		enumerations = element.findall (GIR.enumeration)
		for e in enumerations:
			try:
				e = Enumeration (e, self)
				self._enumerations[e.name] = e
			except ValueError, e:
				logging.error ("Error parsing Enumeration: %s" % e)
		
		bitfields = element.findall (GIR.bitfield)
		for b in bitfields:
			try:
				b = BitField(b, self)
				self._enumerations[b.name] = b
			except ValueError, e:
				logging.error ("Error parsing BitField: %s" % e)
		
		self._functions = {}
		functions = element.findall (GIR.function)
		for f in functions:
			try:
				f = Function (f, self)
				self._functions[f.name] = f
			except ValueError, e:
				logging.error ("Error parsing Function: %s" % e)
		
		self._callbacks = {}
		callbacks = element.findall (GIR.callback)
		for cb in callbacks:
			try:
				cb = Callback (cb, self)
				self._callbacks[cb.name] = cb
			except ValueError, e:
				logging.error ("Error parsing Callback: %s" % e)
	
	
	@property
	def classes (self):
		return list(self._classes.values())
	
	@property
	def interfaces (self):
		return list(self._ifaces.values())
	
	@property
	def records (self):
		return list(self._records.values())
	
	@property
	def enumerations (self):
		return list(self._enumerations.values())

	@property
	def functions (self):
		return list(self._functions.values())
	
	@property
	def callbacks (self):
		return list(self._callbacks.values())
	
	@property
	def repository (self):
		if self.parent_node is None:
			raise ValueError, "Namespace %s has no associated repository" % self.name
		repo = self.parent_node
		while repo.parent_node:
			repo = repo.parent_node
		return repo
	
	@property
	def members (self):
		"""A generator iterating through all members of this namespace"""
		for s in self.classes :
			yield s
			for m in s.methods : yield m
			for sig in s.signals : yield sig
			for p in s.properties : yield p
			for f in s.fields : yield f
			for cb in s.callbacks : yield cb
		for s in self.interfaces :
			yield s
			for m in s.methods : yield m
			for sig in s.signals : yield sig
			for p in s.properties : yield p
			for f in s.fields : yield f
			for cb in s.callbacks : yield cb
		for s in self.records :
			yield s
			for m in s.methods : yield m
			for f in s.fields : yield f
			for cb in s.callbacks : yield cb
		for s in self.enumerations :
			yield s
			for m in s.members : yield m
		for s in self.functions :
			yield s
		for s in self.callbacks :
			yield s
	
	@property
	def callables (self):
		for cl in self.classes:
			for m in cl.methods : yield m
			for s in cl.signals : yield s
			for cb in cl.callbacks : yield cb
		for iface in self.interfaces :
			for m in iface.methods : yield m
			for s in cl.signals : yield s
			for cb in cl.callbacks : yield cb
		for s in self.records :
			for m in s.methods : yield m
			for cb in s.callbacks : yield cb
		for f in self.functions:
			yield f
	
	@property
	def properties (self):
		for cl in self.classes:
			for p in cl.properties : yield p
	
	@property
	def fields (self):
		for cl in self.classes:
			for f in cl.fields : yield f
		for iface in self.interfaces:
			for f in iface.fields : yield f
		for r in self.records:
			for f in r.fields : yield f
	
	@property
	def symbol_prefix (self):
		try:
			return self._attribs[C["symbol-prefixes"]]
		except KeyError:
			try:
				return self._attribs[C.prefix].lower()
			except KeyError:
				return self.name.lower()
	
	@property
	def identifier_prefixes (self):
		try:
			return self._attribs[C["indentifier-prefixes"]]
		except KeyError:
			try:
				return self._attribs[C.prefix].title()
			except KeyError:
				return self.name.title()

class Repository (Node):
	def __init__ (self):
		self._namespaces = {}
		self._members = {}
		self._register_builtins ()
	
	def add_gir (self, xmlfile):
		"""
		Parse and add file-like object to the repository. The metadata is added
		in a crude unresolved state. To compile and resolve everything you
		need to call link() once you are done adding GIR metadata.
		"""
		xmlparser = ElementTree.XMLParser()
		xml = ElementTree.parse(xmlfile, parser=xmlparser)
		xml = xml.getroot()
		
		if not xml.tag == GIR.repository:
			raise TypeError, "Expected 'repository' tag. Found %s." % xml.tag
		
		Node.__init__ (self, xml, None)
				
		namespaces = xml.findall (GIR.namespace)
		for ns in namespaces:
			ns = Namespace (ns, self)
			if ns.name in self:
				raise ImportError, "GIR namespace %s already registered"
			self._namespaces[ns.name] = ns
			
			# Index everything in the namespace by all known identifiers
			# We use this index later to resolve all interface implementations
			# and class inheritance etc.
			# FIXME: This only indexes top level members,
			#        We also need class members etc
			for member in ns.members:
				self.register_member (member)
	
	def link (self):
		"""
		Resolve all references in GIR metadata added via add_gir()
		"""
		for ns in self._namespaces.values():
			# Resolve interface implementations and class inheritance
			for cl in ns.classes:
				for iface in cl._element.findall (GIR.implements):
					
					name = iface.attrib["name"]
					if not "." in name:
						name = "%s.%s" % (ns.name, name)
					
					if not name in self:
						raise ImportError, "Unresolved interface %s for class %s" % (name, cl.namespaced_name)
					
					iface_node = self[name]
					cl.implement_interface (iface_node)
					iface_node.register_implementation (cl)
				
				if "parent" in cl._attribs:
					# Make sure we have the namespace name of the iface
					parent_name = cl.parent
					if not "." in parent_name:
						parent_name = "%s.%s" % (ns.name, parent_name)
					
					if not parent_name in self:
						logging.warning("Unresolved parent class %s for class %s" % (parent_name, cl.namespaced_name))
					else:
						parent_class = self[parent_name]
						cl._parent_class = parent_class
						parent_class.register_subclass (cl)
			
			# Resolve correct return- and parameter types for all methods,
			# functions, and signals
			for c in ns.callables:
				try:
					c.return_value.type = self[c.return_value.type]
				except KeyError:
					logging.warning("Unresolved return type %s for callable %s" % (c.return_value.type, c))
				
				for i, p in enumerate (c.parameters):
					try:
						p.type = self[p.type]
					except KeyError:
						logging.warning("Unresolved parameter type %s for argument %s of %s" % (p.type, i, p))
			
			# Resolve correct type for all properties and fields
			for f in chain(ns.properties, ns.fields):
				try:
					f.type = self[f.type]
				except KeyError:
					logging.warning("Unresolved type %s for %s" % (f.type, f))
	
	@property
	def namespaces (self):
		return self._namespaces.values()
	
	def register_member (self, member):
		try:
			m_id = member.c_type
			self._members[m_id] = member
		except AttributeError:
			pass
			
		try:
			m_id = member.c_identifier
			self._members[m_id] = member
		except AttributeError:
			pass
				
		self._members[member.namespaced_name] = member
	
	def __getitem__ (self, name_or_type):
		if isinstance (name_or_type, VarArgs):
			return name_or_type
		if isinstance (name_or_type, Array):
			child_type = name_or_type
			while isinstance (child_type, Array):
				child_type = child_type.child_type
			if child_type in self:
				return name_or_type
			else:
				raise KeyError, name_or_type.namespaced_name
		elif isinstance (name_or_type, Type):
			return self._members[name_or_type.namespaced_name]
		elif isinstance (name_or_type, basestring):
			return self._members[name_or_type]
		else:
			raise TypeError, "Expected a name or a giraffe.ast.Type instance"
	
	def __contains__ (self, name_or_type):
		if isinstance (name_or_type, Type):
			child_type = name_or_type
			while isinstance (child_type, Array):
				child_type = child_type.child_type
			return child_type.namespaced_name in self._members
		elif isinstance (name_or_type, basestring):
			return name_or_type in self._members
		else:
			raise TypeError, "Expected a name or a giraffe.ast.Type instance"
	
	def _register_builtins (self):
		for t in BUILTINS:
			self.register_member (BaseType(t, self))
		
class BaseType (Type):
	def __init__ (self, attribs, repo):
		elt = FakeElement ("type", attribs)
		Type.__init__ (self, elt, None)
		self._repo = repo
	
	def html_link (self, contents="", klass=""):
		return '<span class="type-basetype %s">%s</span>' % (klass, contents if contents else self.name)
	
	@property
	def namespace (self):
		return BaseNamespace(self._repo)

class BaseNamespace:
	def __init__ (self, repo):
		self.repository = repo

class FakeElement:
	def __init__ (self, tag, attrib):
		self.tag = tag
		self.attrib = attrib

