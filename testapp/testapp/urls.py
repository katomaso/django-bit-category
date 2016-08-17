from django.conf.urls import include, url
from bitcategory.models import Category

# admin.autodiscover()


def _patterns(*args):
    try:
        from django.conf.urls import patterns
        return patterns('', *args)
    except ImportError:
        return args

urlpatterns = _patterns(
    url(r'^$', 'testapp.views.index', name="index"),
    url('', include('bitcategory.urls'), {"model": Category}),
    # url(r'^admin/', include(admin.site.urls)),
)
