from django.db import models

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modificado el")

    class Meta:
        abstract = True
