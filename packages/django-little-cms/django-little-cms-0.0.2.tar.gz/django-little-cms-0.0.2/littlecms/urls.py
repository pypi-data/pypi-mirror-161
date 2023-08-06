from django.urls import path
from littlecms import views as littlecms_views

urlpatterns = [
    path('', littlecms_views.BaseCmsView.as_view(), name='base_cms'),
    path('site/<str:menu_option_slug>',
         littlecms_views.BaseCmsView.as_view(),
         name='base_cms'),
    path('site/<str:menu_option_slug>/<str:article_slug>',
         littlecms_views.ArticleDetailView.as_view(),
         name='article_detail'),
]
