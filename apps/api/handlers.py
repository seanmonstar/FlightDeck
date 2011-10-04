import commonware.log

from piston.handler import BaseHandler

from django.contrib.auth.models import User
from jetpack.models import Package, PackageRevision, Module, Attachment

log = commonware.log.getLogger('f.api')

class QueryParamsHandler(BaseHandler):
    """
    This allows parameters from a query string to filter the returning
    queryset from GET (read) requests. For example:

        GET /api/packages/?author=1
        => Package.objects.filter(author=1)
    """
    def queryset(self, request):
        log.debug('queryset derper')
        qs = super(QueryParamsHandler, self).queryset(request)
        if request.GET:
            params = dict((k, v) for k, v in request.GET.items() if k in self.fields)
            qs = qs.filter(**params)
        return qs


class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = User
    fields = ('username',)


class PackageHandler(QueryParamsHandler):
    allowed_methods = ('GET',)
    model = Package
    fields = ('id_number', 'full_name', 'name', 'description', 'type',
              'author', 'created_at', 'last_update', 'active', 'deleted',
              'latest')


class ModuleHandler(QueryParamsHandler):
    allowed_methods = ('GET', 'POST')
    model = Module
    fields =  ('id', 'filename', 'author', 'code',)


class AttachmentHandler(QueryParamsHandler):
    allowed_methods = ('GET', 'POST')
    model = Attachment
    fields = ('id', 'filename', 'ext', 'author', 'url')

    @classmethod
    def url(cls, attachment):
        return attachment.get_display_url()
