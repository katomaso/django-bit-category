Django (bit) Category
=====================

Fast Category model with tree-like structure using bitwise ID field. The benefits
are obvious

 * simplicity
 * foreign key can filter all descendants in one simple query
   ``SomeModel.objects.filter(category_id__gte=category.gte, category_id__lt=category.lt)``

The hierarchical bitwise feature is in separated abstract model, so feel free to use it everywhere.

Future:
 * Adding widget which handles the tree structure via many selects created via AJAX