from django.conf.urls.defaults import patterns, url, include

from piston.resource import Resource

from . import handlers


packages_resource = Resource(handlers.PackageHandler)
modules_resource = Resource(handlers.ModuleHandler)
attachments_resource = Resource(handlers.AttachmentHandler)

v0 = patterns('',
    url('^packages/$', packages_resource),
    url('^packages/(?P<id_number>\d+)$', packages_resource),

    url('^modules/$', modules_resource),
    url('^modules/(?P<id>\d+)$', modules_resource),

    url('^attachments/$', attachments_resource),
    url('^attachments/(?P<id>\d+)$', attachments_resource),
)




urlpatterns = patterns('',
    url(r'^0/', include(v0))
)
