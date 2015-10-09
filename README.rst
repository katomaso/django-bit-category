:author: Tomas Peterka
:licence: GPL

django-bit-category
=====================

Abstract (and one concrete) ``Model`` with tree-like structure using bitwise ID field.
This implementation is **very simple** and **super fast**!
Given a category, you can query for related models (products) to the category
and all it's subcategories by
`SomeModel.objects.filter(category_id__gte=category.gte, category_id__lt=category.lt)`

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

If you just want to use just one of the abstract models then you don't need to do anything special.
Import the abstract model ``from bitcategory.models import BaseCategory`` and inherit from it in your
concrete Model. Then make a foreign key in your another model which is going to use categories::

    # :file: models.py
    from django.db import models
    from bitcategory.models import BaseCategory

    class MyCategory(BaseCategory):
        # BaseCategory already provides fileds name, slug and path
        class Meta:
            abstract = False

    class MyProduct(models.Model):
        # some other fields like price, quantity ....
        category = models.ForeignKey('myproject.MyCategory', verbose_name=_("Category"))

That is all to your ``Model`` definition. Now, provided you have a concrete instance of MyCategory in
variable ``category``, you can query products within the category and all its subcategories by::

    MyProduct.objects.filter(category_id__gte=category.gte, category_id__lt=category.lt)

or to get products only for the category by::

    MyProduct.objects.filter(category=category)

However, if you want to have the awesome dynamic select boxes in your forms with ``category`` in it,
you need to do more

  * add the ``bitcategory`` into your INSTALLED_APPS
  * add ``bitcategory.urls`` into your urls and specify your custom hierarchical
    model. If you didn't create your custom hierarchical model, then use our pre-built concrete model
    ``bitcategory.models.Category``. We do that in order to be able to respond to AJAX requests which are sent
    by the ``bitcategory.fields.HierarchicalField``. The most simple way looks like::

      # :file: urls.py
      from django.conf.urls import patterns, include, url
      from myapp.models import YourHierarchicalModel

      urlpatterns = patterns('',
            url('', include('bitcategory.urls'), {"model": YourHierarchicalModel}),
      )

Now you are ready to show your form with categories in it. First, add
``bitcategory.fields.HierarchicalField`` in the form. When rendering the form into a page, don't
forget to include ``{{form.media}}`` into your template for javascripts.
