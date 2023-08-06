from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render
from littlecms.models import Article, MenuOption
from django.utils.translation import gettext_lazy as _


# Create your views here.
class BaseCmsView(View):

    def get(self, request, menu_option_slug=None):

        if not menu_option_slug:
            menu_option = MenuOption.objects.filter(order=0)
        else:
            menu_option = MenuOption.objects.filter(slug=menu_option_slug)
        if menu_option:
            menu_option = menu_option.first()
            template = 'littlecms/base.html'
            if menu_option.page:
                template = menu_option.page.template if menu_option.page.template else template
            context = {'menu_option': menu_option}
            return render(request, template, context)
        else:
            messages.error(request, _('No se encontró la opción solicitada.'+request.path))
            return redirect('/')


class ArticleDetailView(View):

    def get(self, request, menu_option_slug, article_slug):

        menu_option = MenuOption.objects.filter(slug=menu_option_slug)
        article = Article.objects.filter(slug=article_slug)
        if menu_option and article:
            menu_option = menu_option.first()
            article = article.first()
            context = {'menu_option': menu_option, 'article': article}
            return render(request, 'littlecms/article_detail.html', context)
        else:
            messages.error(request, _('No se encontró la opción solicitada'))
            return render(request, 'littlecms/article_detail.html')
