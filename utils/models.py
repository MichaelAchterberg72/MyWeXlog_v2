from django.db import models
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.utils.translation import gettext as _

# Create your models here.
class MetaTagsMixin(models.Model):
    """
    Abstract base class for generating meta tags
    """
    class Meta:
        abstract = True

    meta_keywords = models.CharField(_("Keywords"), max_length=255, blank=True, help_text=_("Separate keywords by comma."))
    meta_description = models.CharField(_("Description"), max_length=255, blank=True)
    meta_author = models.CharField(_("Author"), max_length=255, blank=True)
    meta_copyright = models.CharField(_("Copyright"), max_length=255, blank=True)

    def get_meta(self, name, content):
        tag = ""
        if name and content:
            tag = loader.render_to_string('utils/meta.html', {
                'name': name,
                'content': content,
            })

    def get_meta_keywords(self):
        return self.get_meta('keywords', self.meta_keywords)

    def get_meta_description(self):
        return self.get_meta('description', self.meta_description)

    def get_meta_author(self):
        return self.get_meta('author', self.meta_author)

    def get_meta_copyright(self):
        return self.get_meta('copyright', self.meta_copyright)

    def get_meta_tags(self):
        return mark_safe("\n".join((
            self.get_meta_keywords(),
            self.get_meta_description(),
            self.get_meta_author(),
            self. get_meta_copyright(),
        )))
