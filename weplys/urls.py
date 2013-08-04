from django.conf.urls import patterns, include, url
from views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'weplys.views.home', name='home'),
    # url(r'^weplys/', include('weplys.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^import/$', import_songs),
    url(r'^add_songs/$', add_songs),
    url(r'^delete_song/$', delete_song),
    url(r'^add_playlist/$', add_playlist),
    url(r'^load_playlist/$', load_playlist),
    url(r'^delete_playlist/$', delete_playlist),
    url(r'^add_song_to_playlist/$', add_song_to_playlist),
    url(r'^delete_song_from_playlist/$', delete_song_from_playlist),
    url(r'^get_lyrics/$', get_lyrics),
    url(r'^main/$', main_page),

)
