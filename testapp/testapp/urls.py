from django.conf.urls import patterns, include, url
from bitcategory.models import Category

# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'testapp.views.index', name="index"),
    url('', include('bitcategory.urls'), {"model": Category}),
    # url(r'^admin/', include(admin.site.urls)),
)
