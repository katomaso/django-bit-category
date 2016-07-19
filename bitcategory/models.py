from __future__ import division

from django.db import models
from django.template.defaultfilters import slugify


class HierarchicalModel(models.Model):
    """
    Model which keeps tree-like structure using bitwise primary key.

    The root category reserves first `LEVEL_BIT_WIDTH` (MSB) bits for it's `id`.

    :param:`ID_BIT_WIDTH` int how many bits the ID has (32 or 64)
    :param:`LEVEL_BIT_WIDTH` int how many bits should one level have. It does not need
        to be a divisor of `ID_BIT_WIDTH`. The level can take 2^LEVEL_BIT_WIDTH items.
    :param:`level` int default 1
    """
    ID_BIT_WIDTH = 32
    LEVEL_BIT_WIDTH = 5

    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey('self', related_name="children", null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=1)
    ordering = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Update level and assign next free id."""
        self.level = self.parent.level + 1 if self.parent else 1
        if not self.id:
            self.id = self.get_free_id()
            kwargs.update(force_insert=True)
        super(HierarchicalModel, self).save(*args, **kwargs)

    def __contains__(self, other):
        """Test whether a category is a subcategory of the other.

        Usage: subcategory in parent_category == True
               parent_category in subcategory == False (antisymmetricity)
               category in category == True (reflexivity)

        !Right associative! "key" in dict -> dict.__contain__("key")
        """
        mask = self._mask_for(self.level)
        return (other.id >= self.id) and ((self.id & mask) == (other.id & mask))

    @property
    def gte(self):
        """Lower inclusive bound for descendants IDs."""
        return self.id

    @property
    def lt(self):
        """Upper exclusive bound for descendant IDs."""
        return self.id + self.min

    @property
    def ancestors(self):
        """Select all ancestors including itself in a queryset."""
        ids = map(lambda level: self._mask_for(level) & self.id, range(self.level, 0, -1))
        return self.__class__.objects.filter(id__in=ids)

    @property
    def descendants(self):
        """Select all descendants including itself in a queryset."""
        return self.__class__.objects.filter(id__gte=self.gte, id__lt=self.lt)

    @property
    def neighbours(self):
        """Select all neighbours including itself in a queryset."""
        return self.__class__.objects.filter(parent=self.parent)

    @property
    def first_child(self):
        """Select first child."""
        try:
            return self.__class__.objects.filter(parent=self)[0]
        except IndexError:
            return None

    @property
    def root(self):
        """Return root node from DB."""
        return self.__class__.objects.get(pk=self.id & self._mask_for(1))

    @property
    def min(self):
        """Minimal value for given (sub) level."""
        return 1 << self._get_right_offset()

    @property
    def max(self):
        """Maximal value for given (sub) level."""
        return (2 ** self.__class__.LEVEL_BIT_WIDTH - 1) << self._get_right_offset()

    def __gt__(self, other):
        """State if the other is a child of self.

        ROOT1 > CHILD1 == True
        ROOT2 > CHILD1 == False
        This function is intended mainly for usage within templates.
        """
        if not isinstance(other, self.__class__):
            raise ValueError("Compare only HierarchicalModels ancestors")
        if self.id is None or other.id is None:
            raise ValueError("Cannot compare unsaved HierarchicalModel")
        return (self.id == (other.id & self._mask_for(self.level)))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def get_free_id(self):
        """Returns next free ID in database evaluating spaces made by deleted items"""
        step = self.min
        if not self.parent:
            pks = sorted(self.__class__.objects.filter(parent__isnull=True).values_list("id", flat=True))
            minimum = step
        else:
            minimum = self.parent.id + step
            pks = sorted(self.parent.children.values_list("id", flat=True))
        if not pks:
            return minimum
        for i, pk in enumerate(pks):
            if pk != i*step + minimum:
                return i*step + minimum
        return pks[-1] + step

    def _get_left_offset(self, level=None):
        """Return number of offset bits in current/given level from left."""
        return (level or self.level) * self.__class__.LEVEL_BIT_WIDTH

    def _get_right_offset(self, level=None):
        """Return number of offset bits in current/given level from right."""
        return self.__class__.ID_BIT_WIDTH - self._get_left_offset(level)

    def _mask_for(self, level):
        """Return mask with 1 where are the significant bits (1 from left)."""
        return (2 ** self._get_left_offset(level) - 1) << (self._get_right_offset(level))


class CategoryBase(HierarchicalModel):
    """Category model prepared for you."""
    name = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, blank=True, db_index=False)
    path = models.CharField(max_length=255, blank=True, db_index=True, unique=True,
                            help_text="Generated automatically, don't edit")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # update path every time
        new_path = self.slug
        if self.parent:
            new_path = "/".join((self.parent.path.strip("/"), self.slug))
        if self.path != new_path:
            self.path = new_path
        super(CategoryBase, self).save(*args, **kwargs)


class Category(CategoryBase):
    """
    This class is mostly for testing purposes. If you don't want this class to
    be created in your database just don't put bitcategory into INSTALLED_APPS.
    """
    class Meta:
        abstract = False
        app_label = "bitcategory"
