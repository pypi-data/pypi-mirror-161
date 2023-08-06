from re import template
from tabnanny import verbose
from django.db import models
from colorfield.fields import ColorField
from ckeditor import fields as ckeditor_fields
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader import fields as ckeditor_uploader_fields

# Create your models here.

MENU_OPTION_TYPE_CHOICES = (
    ('1', _('Link')),
    ('2', _('Submenu')),
    ('3', _('Separator')),
)


class UpperCaseCharField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField,
                         self).pre_save(model_instance, add)


class Image(models.Model):
    title = models.CharField(
        verbose_name=_('Title'),
        db_column='title',
        help_text=_('The image\'s title.'),
        max_length=200,
    )
    file = models.ImageField(
        verbose_name=_('File'),
        db_column='file',
        help_text=_('The image\'s file.'),
        upload_to='csm/images/',
    )
    description = ckeditor_fields.RichTextField(
        verbose_name=_('Description'),
        db_column='description',
        help_text=_('The image\'s description.'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.title}-{self.file}'

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        ordering = ['-pk']


class ArticleType(models.Model):
    name = UpperCaseCharField(
        verbose_name=_('Name'),
        db_column='name',
        help_text=_('The article type\'s name.'),
        max_length=200,
    )
    description = ckeditor_fields.RichTextField(
        verbose_name=_('Description'),
        db_column='description',
        help_text=_('The article type\'s description.'),
        blank=True,
        null=True,
    )
    template = models.CharField(
        verbose_name=_('Template'),
        db_column='template',
        help_text=_('The template on which the article\'s is rendered.'),
        max_length=200,
        default='basic.html',
    )
    is_active = models.BooleanField(
        verbose_name=_('Active'),
        db_column='is_active',
        help_text=_('Is the article type active?'),
        default=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Article type')
        verbose_name_plural = _('Article types')
        ordering = ['-pk']


class Article(models.Model):
    type = models.ForeignKey(
        ArticleType,
        verbose_name=_("Type"),
        db_column='type',
        help_text=_('Article\'s type.'),
        on_delete=models.DO_NOTHING,
    )
    title = models.CharField(
        verbose_name=_('Title'),
        db_column='title',
        help_text=_('Article\'s title.'),
        max_length=200,
    )
    body = ckeditor_uploader_fields.RichTextUploadingField(
        verbose_name=_('Body'),
        db_column='body',
        help_text=_('Article\'s content.'),
        blank=True,
        null=True,
    )
    background_image = models.ForeignKey(
        Image,
        verbose_name=_('Background Image'),
        db_column='background_image',
        help_text=_('Background image of the article\'s.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    images = models.ManyToManyField(
        Image,
        through='ArticleImage',
        verbose_name=_('Images'),
        db_column='images',
        related_name='images',
        help_text=_('Images included in the article\'s.'),
        blank=True,
    )
    grid_columns = models.IntegerField(
        verbose_name=_('Grid Columns'),
        db_column='grid_columns',
        help_text=
        _('Number of columns that the article occupies based on the Bootstrap 5 grid system.'
          ),
        default=12,
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
            (6, '6'),
            (7, '7'),
            (8, '8'),
            (9, '9'),
            (10, '10'),
            (11, '11'),
            (12, '12'),
        ),
    )
    article_height = models.CharField(
        verbose_name=_('Article Height'),
        db_column='article_height',
        help_text=_('Article\'s height.'),
        max_length=200,
        blank=True,
        null=True,
    )
    is_commentable = models.BooleanField(
        verbose_name=_('Commentable'),
        db_column='is_commentable',
        help_text=_('Is the article commentable?'),
        default=True,
    )
    is_active = models.BooleanField(
        verbose_name=_('Active'),
        db_column='is_active',
        help_text=_('Is the article active?'),
        default=True,
    )
    show_title = models.BooleanField(
        verbose_name=_('Show Title'),
        db_column='show_title',
        help_text=_('Show the article\'s title?'),
        default=True,
    )
    read_more = models.BooleanField(
        verbose_name=_('Read More'),
        db_column='read_more',
        help_text=_('Show the article\'s read more button?'),
        default=False,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        db_column='slug',
        help_text=_('URI identifier for this article'),
        max_length=200,
        unique=True,
    )
    date_created = models.DateTimeField(
        verbose_name=_('Date Created'),
        db_column='date_created',
        help_text=_('Date this article was created.'),
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        verbose_name=_('Date Updated'),
        db_column='date_updated',
        help_text=_('Date this article was updated.'),
        auto_now=True,
    )

    def __str__(self):
        return self.title

    def images_list(self):
        return [
            ai.image for ai in ArticleImage.objects.filter(
                article=self).order_by('order')
        ]

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-date_created']


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        verbose_name=_('Article'),
        db_column='article',
        help_text=_('Image is included in this article.'),
        on_delete=models.DO_NOTHING,
    )
    image = models.ForeignKey(
        Image,
        verbose_name=_('Image'),
        db_column='image',
        help_text=_('Image is included in this article.'),
        on_delete=models.DO_NOTHING,
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        db_column='order',
        help_text=_('Order of the image in the article.'),
        default=0,
    )

    def __str__(self):
        return f'{self.article}-{self.image}'

    class Meta:
        verbose_name = _('Article Image')
        verbose_name_plural = _('Article Images')
        ordering = ['order']


class Page(models.Model):
    title = models.CharField(
        verbose_name=_('Title'),
        db_column='title',
        help_text=_('Page\'s title.'),
        max_length=200,
    )
    name = models.CharField(
        verbose_name=_('Name'),
        db_column='name',
        help_text=_('Page\'s name.'),
        max_length=200,
        unique=True,
    )
    template = models.CharField(
        verbose_name=_('Template'),
        db_column='template',
        help_text=_('Page\'s template.'),
        max_length=200,
        blank=True,
        null=True,
    )
    articles = models.ManyToManyField(
        Article,
        through='PageArticle',
        verbose_name=_('Articles'),
        db_column='articles',
        related_name='articles',
        help_text=_('Articles included in this page.'),
        blank=True,
    )
    background_color = ColorField(
        verbose_name=_('Background Color'),
        db_column='background_color',
        help_text=_('Background color of the page.'),
        blank=True,
        null=True,
    )
    background_image = models.ForeignKey(
        Image,
        verbose_name=_('Background Image'),
        db_column='background_image',
        help_text=_('Background image of the page.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField(
        verbose_name=_('Active'),
        db_column='is_active',
        help_text=_('Is the page active?'),
        default=True,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        db_column='slug',
        help_text=_('URI identifier for this page'),
        max_length=200,
        unique=True,
    )
    date_created = models.DateTimeField(
        verbose_name=_('Date Created'),
        db_column='date_created',
        help_text=_('Date this page was created.'),
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        verbose_name=_('Date Updated'),
        db_column='date_updated',
        help_text=_('Date this page was updated.'),
        auto_now=True,
    )

    def __str__(self):
        return f'{self.name}-{self.title}'

    def articles_list(self):
        return [
            pa.article
            for pa in PageArticle.objects.filter(page=self).order_by('order')
        ]

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['-date_created']


class PageArticle(models.Model):
    page = models.ForeignKey(
        Page,
        verbose_name=_('Page'),
        db_column='page',
        help_text=_('Article is included in this page.'),
        on_delete=models.DO_NOTHING,
    )
    article = models.ForeignKey(
        Article,
        verbose_name=_('Article'),
        db_column='article',
        help_text=_('Article is included in this page.'),
        on_delete=models.DO_NOTHING,
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        db_column='order',
        help_text=_('Order of the article in the page.'),
        default=0,
    )

    def __str__(self):
        return f'{self.page}-{self.article}'

    class Meta:
        verbose_name = _('Page Article')
        verbose_name_plural = _('Page Articles')
        ordering = ['order']


class MenuOption(models.Model):
    type = models.CharField(
        verbose_name=_('Type'),
        db_column='type',
        help_text=_('Type of the menu option.'),
        choices=MENU_OPTION_TYPE_CHOICES,
        max_length=20,
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        db_column='order',
        help_text=_('Order of the menu option.'),
        default=0,
    )
    parent = models.ForeignKey(
        'self',
        verbose_name=_('Parent'),
        db_column='parent',
        help_text=_('Parent of the menu option.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    icon = models.CharField(
        verbose_name=_('Icon'),
        db_column='icon',
        help_text=_('Icon of the menu option.'),
        max_length=200,
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name=_('Name'),
        db_column='name',
        help_text=_('Menu option\'s name.'),
        max_length=200,
    )
    page = models.ForeignKey(
        Page,
        verbose_name=_('Page'),
        db_column='page',
        help_text=_('Page of the menu option.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        db_column='slug',
        help_text=_('URI identifier for this menu option'),
        max_length=200,
        unique=True,
    )
    is_active = models.BooleanField(
        verbose_name=_('Active'),
        db_column='is_active',
        help_text=_('Is the menu option active?'),
        default=True,
    )
    date_created = models.DateTimeField(
        verbose_name=_('Date Created'),
        db_column='date_created',
        help_text=_('Date this menu option was created.'),
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        verbose_name=_('Date Updated'),
        db_column='date_updated',
        help_text=_('Date this menu option was updated.'),
        auto_now=True,
    )

    def __str__(self):
        return f'{self.parent}-{self.name}' 

    def list_children(self):
        return MenuOption.objects.filter(parent=self).order_by('order')

    class Meta:
        verbose_name = _('Menu Option')
        verbose_name_plural = _('Menu Options')
        ordering = ['order']