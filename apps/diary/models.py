from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):
    tag = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        verbose_name=_('tag'),
        unique=True,
    )

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class DiaryEntry(models.Model):
    author = models.ForeignKey(
        'users.User',
        null=True,
        blank=False,
        related_name='diary_entries',
        verbose_name=_('Author'),
    )

    date = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date'),
    )

    text = models.TextField(
        null=True,
        blank=False,
        verbose_name=_('Text'),
    )

    tags = models.ManyToManyField(
        to=Tag,
        blank=True,
        related_name='diary_entries',
        verbose_name=_('Tags'),
    )

    class Meta:
        verbose_name = _('Diary entry')
        verbose_name_plural = _('Diary entries')
        ordering = ('-date',)

    @property
    def html(self):
        """Property to represent entry text as HTML."""
        return ''.join([
            f'<p>{line}</p>' if line else '<p>&nbsp;<p>'
            for line in self.text.split('\r\n')
        ])


class DiaryCategory(models.Model):
    author = models.ForeignKey(
        'users.User',
        null=True,
        blank=False,
        related_name='diary_category',
        verbose_name=_('Author'),
    )

    date = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date'),
    )

    Category = models.CharField(
        max_length=100,
        null=False,
        unique=True,
        verbose_name=_('Category'),
    )

    class Meta:
        verbose_name = _('Diary Category')
        verbose_name_plural = _('Diary Categories')
        ordering = ('-date',)


class DiaryImage(models.Model):
    author = models.ForeignKey(
        'users.User',
        null=True,
        blank=False,
        related_name='diary_image',
        verbose_name=_('Author'),
    )

    date = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date'),
    )

    image_path = models.TextField(
        null=False,
        blank=False,
        verbose_name=_('image_path'),
    )

    class Meta:
        verbose_name = _('Diary Image')
        verbose_name_plural = _('Diary Images')
        ordering = ('-date',)


class DiaryTasks(models.Model):
    author = models.ForeignKey(
        'users.User',
        null=True,
        blank=False,
        related_name='diary_task',
        verbose_name=_('Author'),
    )

    date = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date'),
    )

    task = models.TextField(
        null=False,
        blank=False,
        verbose_name=_('task'),
    )

    completion_percent = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('completion_percent')
    )

    category = models.ForeignKey(
        'diary.diarycategory',
        null=True,
        blank=False,
        related_name='diary_task',
        verbose_name=_('category'),
    )

    class Meta:
        verbose_name = _('Diary Task')
        verbose_name_plural = _('Diary Tasks')
        ordering = ('-date',)