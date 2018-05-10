from django.shortcuts import render
from feed.models import News, Category, Source, Tag, Image, Comment, Like
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


def render_result(func):
    def renderer(*args, **kwargs):
        result = func(*args, **kwargs)
        if len(result) == 3:
            request, template_name, values = result
        else:
            request, template_name = result
            values = None
        return render(request, template_name, values)

    return renderer


def add_categories(func):
    def adder(*args, **kwargs):
        result = func(*args, **kwargs)

        if len(result) == 3:
            request, template_name, values = result
            values["categories"] = [{"name": category.name, "pk": category.pk,\
                                    "is_active": ("active_category" in values) and (category.pk == values["active_category"])} \
                                    for category in Category.objects.all()]
        else:
            request, template_name = result
            values = {"categories": list(Category.objects.all())}

        return request, template_name, values

    return adder


def add_sources(func):
    def adder(*args, **kwargs):
        request, template_name, values = func(*args, **kwargs)

        if "active_category" in values:
            category = Category.objects.get(pk=values["active_category"])
            sources = list(category.sources.all())
            values["sources"] = sources
        else:
            sources = list(Source.objects.all())
            values["sources"] = sources
        return request, template_name, values

    return adder


def register(request):
    if request.method == 'POST':
        if 'username' not in request.POST:
            return HttpResponse(status=400)

        if 'password' not in request.POST:
            return HttpResponse(status=400)

        if 'email' not in request.POST:
            return HttpResponse(status=400)
    username = request.POST["username"]
    password = request.POST["password"]
    email = request.POST["email"]
    user = User.objects.create_user(username, email, password)
    user.save()
    return HttpResponse(status=200)


def auth(request):
    if request.method == 'POST':
        if 'username' not in request.POST:
            return HttpResponse(status=400)

        if 'password' not in request.POST:
            return HttpResponse(status=400)
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)

@render_result
@add_categories
def view_article(request, pk):
    return request, "feed/article_page.html", {"article": News.objects.get(pk=pk)}


@render_result
@add_sources
@add_categories
def view_category(request, pk=0):
    values_dict = {}
    if pk == 0:
        news = News.objects.all()
    else:
        category = Category.objects.get(pk=pk)
        news = category.news_in_category.all()
        values_dict["active_category"] = pk

    articles = []
    for article in news:
        article_dict = {}
        article_dict["title"] = article.title
        article_dict["image"] = article.article_images.first().url
        article_dict["pk"] = article.pk
        articles.append(article_dict)

    values_dict["articles"] = articles
    return request, "feed/main_page.html", values_dict


@render_result
@add_sources
@add_categories
def view_tag(request, pk):
    values_dict = {}
    tag = Tag.objects.get(pk=pk)
    news = tag.news_with_tag.all()

    articles = []
    for article in news:
        article_dict = {}
        article_dict["title"] = article.title
        article_dict["image"] = article.article_images.first().url
        article_dict["pk"] = article.pk
        articles.append(article_dict)

    values_dict["articles"] = articles
    return request, "feed/main_page.html", values_dict


@login_required
def add_comment(request):
    if request.method == 'POST':
        if 'comment' not in request.POST:
            return HttpResponse(status=400)

        if 'article' not in request.POST:
            return HttpResponse(status=400)

        user = request.user
        author = user
        comment = request.POST['comment']
        article_pk = int(request.POST['article'])

        comment_obj = Comment()
        comment_obj.author = author
        comment_obj.comment = comment
        comment_obj.article = News.objects.get(pk=article_pk)
        comment_obj.save()

    return HttpResponse(user.first_name + user.last_name ,status=200)

@login_required
def like(request):
    if request.method == 'POST':
        if 'article' not in request.POST:
            return HttpResponse(status=400)

        article_pk = int(request.POST['article'])
        user = request.user
        article = News.objects.get(pk=article_pk)
        query = user.user_likes.filter(article=article)
        if query.count() == 0:
            like_obj = Like()
            like_obj.article = article
            like_obj.owner = user
            like_obj.save()
            return HttpResponse('true', status=200)
        else:
            query.get().delete()
            return HttpResponse('false', status=200)




def get_news(request):
    import requests
    from bs4 import BeautifulSoup

    source = Source.objects.get(pk=1)

    url = source.articles_page
    print(url)
    site_url = source.url
    print(site_url)
    main_page = requests.get(url)

    soup = BeautifulSoup(main_page.text.encode('utf-8'), 'html.parser')
    titles = soup.find_all('h3')
    for title in titles:
        link = title.find_all("a")
        if link:
            article = News()
            article.source = source
            article.category = source.category
            article.slug = title.a.get("href").split("/")[-1]
            article.title = title.get_text()
            article_page = site_url + title.a.get("href")
            article_page = requests.get(article_page)
            page_soup = BeautifulSoup(article_page.text.encode('utf-8'), 'html.parser')

            page_content = page_soup.find_all("div", {"class": "type-page clearfix"})[0]
            article.text = str(page_content)
            article.text = article.text[33:-7]
            article.save()
            image_url = title.parent.parent.a.img.get("src").split("?")[0]
            start = image_url.rfind("https")
            image_url = image_url[start:]
            image = Image()
            image.url = image_url
            image.news = article
            image.save()
            tags = page_soup.find_all("div", {"class" : "article__tags"})[1]
            tags = tags.find_all("a")
            for tag in tags:
                name = tag.get_text()
                db_tags = Tag.objects.filter(name=name)
                if db_tags.count() == 1:
                    article.tags.add(db_tags.first())
                else:
                    db_tag = Tag()
                    db_tag.name = tag.get_text()
                    db_tag.save()
                    article.tags.add(db_tag)
            article.save()
