from django.conf.urls.defaults import *

urlpatterns = patterns('jetpack.views',
	url(r'^create/$', 'create', name='create'),
	# Jetpacks
    url(r'^jp_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/$',
		'jetpack_version_edit', name='jp_jetpack_version_edit'),
	url(r'^jp_(?P<slug>.*)/version_create/$', 
		'jetpack_version_create', name='jp_jetpack_version_create'),
	url(r'^jp_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/update/$', 
		'jetpack_version_update', name='jp_jetpack_version_update'),
	url(r'^jp_(?P<slug>.*)/update/$', 
		'jetpack_update', name='jp_jetpack_update'),
	url(r'^jp_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/save_as_base/$', 
		'jetpack_version_save_as_base', name='jp_jetpack_version_save_as_base'),
	url(r'^jp/create',
		'jetpack_create', name='jp_jetpack_create'),
    url(r'^jp_(?P<slug>.*)/$',
		'jetpack_edit', name='jp_jetpack_edit'),
	# Capabilities
    url(r'^cap_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/$',
		'capability_version_edit', name='jp_capability_version_edit'),
	url(r'^cap_(?P<slug>.*)/version_create/$', 
		'capability_version_create', name='jp_capability_version_create'),
	url(r'^cap_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/update/$', 
		'capability_version_update', name='jp_capability_version_update'),
	url(r'^cap_(?P<slug>.*)/update/$', 
		'capability_update', name='jp_capability_update'),
	url(r'^cap_(?P<slug>.*)/v_(?P<version>.*)\.(?P<counter>\d+)/save_as_base/$', 
		'capability_version_save_as_base', name='jp_capability_version_save_as_base'),
	url(r'^cap/create',
		'capability_create', name='jp_capability_create'),
    url(r'^cap_(?P<slug>.*)/$',
		'capability_edit', name='jp_capability_edit'),
)

