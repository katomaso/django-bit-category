from __future__ import division

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible


class HierarchicalModel(models.Model):
    '''
    Model which keeps tree-like structure using bitwise primary key.

    :param:`ID_BIT_WIDTH` int how many bits does the ID have (32 or 64)
    :param:`LEVEL_BIT_WIDTH` int how many bits should level have, does not need
        to be divisor of `ID_BIT_WIDTH`. The level can take 2^LEVEL_BIT_WIDTH items.
    :param:`level` int default 1
    '''
    ID_BIT_WIDTH = 32
    LEVEL_BIT_WIDTH = 5

    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey('self', related_name="children", null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=1)
    ordering = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.level:
            self.level = self.parent.level + 1 if self.parent else 1
        if not self.id:
            self.id = self.get_free_id()
        super(HierarchicalModel, self).save(*args, **kwargs)

    @property
    def gte(self):
        '''Lower inclusive bound for descendants IDS'''
        return self.id

    @property
    def lt(self):
        '''Upper exclusive bound for descendant IDS'''
        return self.id + self.min

    @property
    def ancestors(self):
        '''Returns ``QuerySet`` of ancestors (including itself)'''
        ids = map(lambda l: self._mask_for(l) & self.id, range(self.level, 0, -1))
        return self.__class__.objects.filter(id__in=ids)

    @property
    def descendants(self):
        '''Return ``QuerySet`` of all descendants (including itself)'''
        return self.__class__.objects.filter(id__gte=self.id, id__lt=self.id+self.min)

    @property
    def root(self):
        '''Returns root node from DB'''
        return self.__class__.objects.get(pk=self.id & self._mask_for(1))

    @property
    def min(self):
        '''Minimal value for given (sub) level'''
        return 1 << self._get_right_offset()

    @property
    def max(self):
        '''Maximal value for given (sub) level'''
        return (2 ** self.__class__.LEVEL_BIT_WIDTH - 1) << self._get_right_offset()

    def get_free_id(self):
        '''Returns next free ID in database evaluating spaces made by deleted items'''
        step = self.min
        if not self.parent:
            pks = sorted(self.__class__.objects.filter(parent__isnull=True).values_list("id", flat=True))
            minimum = step
        else:
            minimum = (self.parent.id & self._mask_for(self.parent.level)) + step
            pks = sorted(self.parent.children.values_list("id", flat=True))
        if not pks:
            return minimum
        for i, pk in enumerate(pks):
            if pk != i*step + minimum:
                return i*step + minimum
        return pks[-1] + step

    def _get_left_offset(self, level=None):
        '''Returns number of offset bits in current/given level from left'''
        return (level or self.level) * self.__class__.LEVEL_BIT_WIDTH

    def _get_right_offset(self, level=None):
        '''Returns number of offset bits in current/given level from right'''
        return self.__class__.ID_BIT_WIDTH - self._get_left_offset(level)

    def _mask_for(self, level):
        '''Returns mask with 1 where are the significant bits (1 from left)'''
        return (2 ** self._get_left_offset(level) - 1) << (self._get_right_offset(level))


@python_2_unicode_compatible
class Category(HierarchicalModel):

    name = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, blank=True, db_index=False)
    path = models.CharField(max_length=255, blank=True, db_index=True, unique=True,
                            help_text="Generated automatically, don't edit")

    class Meta:
        abstract = False

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # update path every time when changes
        new_path = self.slug
        if self.parent:
            new_path = "/".join((self.parent.path.strip("/"), self.slug))
        if self.path != new_path:
            self.path = new_path
        super(Category, self).save(*args, **kwargs)
