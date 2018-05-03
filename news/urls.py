"""news URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from feed.views import view_category, view_article, get_news, view_tag, add_comment, like, register, auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<int:pk>/', view_category, name="view_category"),
    path('', view_category, name="view_all"),
    path('article/<int:pk>/', view_article, name="view_article"),
    path('load_news/', get_news, name="get_news"),
    path('tag/<int:pk>/', view_tag, name="view_tag"),
    path('comment/add', add_comment, name="add_comment"),
    path('like/like', like, name="like"),
    path('login/register', register, name="register"),
    path('login/auth', auth, name="login"),
    path('oauth/', include('social_django.urls', namespace='social'))
]
