:author: Tomas Peterka
:licence: GPL

django-bit-category
=====================

Abstract (and one concrete) ``Model`` with tree-like structure using bitwise ID field.
This implementation is **very simple** and **super fast**!

The key idea is to reserve a block of bits in model's ID for different levels of
hierarchy. In the basic setup we expect 32 bit ID (can be changed via ``ID_BIT_WIDTH``)
and we give 5 bits for each level (can be changed via ``LEVEL_BIT_WIDTH``).
The IDs looks like this::

    XXXXX000000000000000000000000000  # mask for the root category
    00001000000000000000000000000000  # first root
    00010000000000000000000000000000  # second root
    00011000000000000000000000000000  # third root

    00001000010000000000000000000000  # first child of the first root
    00001000100000000000000000000000  # second child of the first root

    ...and so on

Getting **all** descendants in all levels is in ``hierarchical_instance.descendants``,
but under the hood it is as simple as::

    SomeModel.objects.filter(category_id__gte=category.gte, category_id__lt=category.lt)


What is included in this app
----------------------------

  * abstract HierarchicalModel which takes care about the magic with IDs
  * abstract BaseCategory which contains the most usual category implementation
  * HierarchicalField which you can use for any custom model
  * HierarchicalWidget which dynamically (via AJAX) creates / deletes select boxes
  * urls.py and views.py which contains AJAX magic for form field working


How to make it work
-------------------

If you want to use just a abstract model, then you don't need to do anything special.
Just import a model ``from bitcategory.models import BaseCategory`` and here you are.

If you would like to have the awesome dynamic select boxes you need to do more
  * add the ``bitcategory`` into your INSTALLED_APPS
  * add ``bitcategory.urls`` into your urls and specify your custom hierarchical
    model. If you didn't make custom model, then you still have to specify   
    ``bitcategory.models.Category``. The most simple way looks like::
  
      # :file: urls.py
      from django.conf.urls import patterns, include, url
      from myapp.models import YourHierarchicalModel
      
      urlpatterns = patterns('',
            url('', include('bitcategory.urls'), {"model": YourHierarchicalModel}),
      )

And that's done. Just use ``bitcategory.fields.HierarchicalField`` and don't forget
to include ``{{form.media}}`` into your template for javascripts.

Future:
  * [DONE] Adding widget which handles the tree structure via many selects
    created via AJAX
  * Finish the implementation of namespaceses (even in the Field)
    for different models  
