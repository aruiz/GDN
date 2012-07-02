# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
from giscanner.girparser import GIRParser
import api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
from django.shortcuts import render_to_response
from storage import GIR_PATH, store_parser
from django.template import Context

def index(request):
	namespaces = []
	for db_ns in models.Namespace.objects.all():
		ns = {'name':    db_ns.name,
			  'version': db_ns.version,
			  'classes': False,
			  }
		namespaces.append (ns)

		classes = models.Class.objects.filter (namespace = db_ns)
		for db_class in classes:
			klass = {'name': db_class.gtype_name}

			if not ns['classes']:
				ns['classes'] = []
			ns['classes'].append (klass)

	ctx = Context({'namespaces': namespaces})
	return render_to_response ('overview.html', ctx)

