"""
Definition of urls for Web_SpeechToText_Service_v1.
"""

from django.conf.urls import include, url
from SpeechToText import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index')
]

#メディアの設定
#https://qiita.com/narupo/items/e3dbdd5d030952d10661
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)