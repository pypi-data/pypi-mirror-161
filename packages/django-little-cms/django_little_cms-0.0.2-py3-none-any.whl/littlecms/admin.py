from django.contrib import admin
from littlecms.models import ArticleImage, Image, Article, ArticleType, Page, MenuOption, PageArticle

# Register your models here.


class PageArticleInline(admin.TabularInline):
    model = PageArticle
    extra = 0


class PageAdmin(admin.ModelAdmin):
    inlines = (PageArticleInline, )


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 0


class ArticleAdmin(admin.ModelAdmin):
    inlines = (ArticleImageInline, )


class MenuOptionInline(admin.TabularInline):
    model = MenuOption
    extra = 0


class MenuOptionAdmin(admin.ModelAdmin):
    inlines = (MenuOptionInline, )


admin.site.register(Image)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleType)
admin.site.register(Page, PageAdmin)
admin.site.register(MenuOption, MenuOptionAdmin)
