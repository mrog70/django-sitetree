from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# This allows South to handle our custom 'CharFieldNullable' field 
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^sitetree\.models\.CharFieldNullable"])

class CharFieldNullable(models.CharField):
    """We use custom char field to put nulls in SiteTreeItem 'alias' field.
    That allows 'unique_together' directive in Meta to work properly, so
    we don't have two site tree items with the same alias in the same site tree. 
    
    """
    def get_prep_value(self, value):
        if value is not None:
            if value.strip() == '':
                return None
        return self.to_python(value)

class Tree(models.Model):
    alias = models.CharField(_('Alias'), max_length=80, help_text=_('Short name to address site tree from a template.'), unique=True, db_index=True)
       
    class Meta:
        verbose_name = _('Site Tree')
        verbose_name_plural = _('Site Trees')
        
    def __unicode__(self):
        return u'%s' % (self.alias)

class TreeItem(models.Model):
    title = models.CharField(_('Title'), max_length=100, help_text=_('Site tree item title. Can contain template variables E.g.: {{ mytitle }}.'))
    hint = models.CharField(_('Hint'), max_length=200, help_text=_('Some additional information about this item that is used as a hint.'), blank=True, default='')
    url = models.CharField(_('URL'), max_length=200, help_text=_('Exact URL or URL pattern (see "Additional settings") for this item.'), db_index=True)
    urlaspattern = models.BooleanField(_('URL as Pattern'), help_text=_('Whether the given URL should be treated as a pattern.<br/><b>Note:</b> Refer to Django "URL dispatcher" documentation (e.g. "Naming URL patterns" part).'), db_index=True, default=False)
    tree = models.ForeignKey(Tree, verbose_name=_('Site Tree'), help_text=_('Site tree this item belongs to.'), db_index=True)    
    hidden = models.BooleanField(_('Hidden'), help_text=_('Whether to show this item in navigation.'), db_index=True, default=False)    
    alias = CharFieldNullable(_('Alias'), max_length=80, help_text=_('Short name to address site tree item from a template.<br /><b>Reserved aliases:</b> "trunk", "this-children" and "this-siblings".'), db_index=True, blank=True, null=True)
    description = models.TextField(_('Description'), help_text=_('Additional comments on this item.'), blank=True, default='')
    inmenu = models.BooleanField(_('Show in menu'), help_text=_('Whether to show this item in a menu.'), db_index=True, default=True)
    inbreadcrumbs = models.BooleanField(_('Show in breadcrumb path'), help_text=_('Whether to show this item in a breadcrumb path.'), db_index=True, default=True)
    insitetree = models.BooleanField(_('Show in site tree'), help_text=_('Whether to show this item in a site tree.'), db_index=True, default=True)
    # These two are for 'adjacency list' model.
    # This is the current approach of tree representation for sitetree.
    parent = models.ForeignKey('self', verbose_name=_('Parent'), help_text=_('Parent site tree item.'), db_index=True, null=True, blank=True)
    sort_order = models.IntegerField(_('Sort order'), help_text=_('Item position among other site tree items under the same parent.'), db_index=True, default=0)
    
    def save(self, force_insert=False, force_update=False, **kwargs):
        """We override parent save method to set item's sort order to its' primary
        key value.
        
        """
        super(TreeItem, self).save(force_insert, force_update, **kwargs)
        if self.sort_order == 0:
            self.sort_order = self.id
            self.save()
    
    class Meta:
        verbose_name = _('Site Tree Item')
        verbose_name_plural = _('Site Tree Items')
        unique_together = ('tree', 'alias')
        
    def __unicode__(self):
        return u'%s' % (self.title)
    
      