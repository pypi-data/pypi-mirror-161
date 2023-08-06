from hx_toolkit.models import Article, Category


def get_articles_by_category(category_slug):
    articles = Article.objects.filter(category__slug=category_slug)
    print len(articles)


def get_article_by_slug(article_slug):
    article = Article.objects.get(slug=article_slug)

    return article


def create_article_data():
    articles_by_category = {}
    categories = Category.objects.all()

    for category in categories:
        category_articles = Article.objects.filter(category=category)
        article_data = []
        for article in category_articles:
            article_data.append(article.article_title_data())
        if article_data:
            articles_by_category[category.slug] = article_data

    articles_by_time = {}

    phases = Article.PHASE_CHOICES
    quarters = Article.QUARTER_CHOICES

    for phase in phases:
        article_by_quarter = {}
        for quarter in quarters:
            quarter_articles = Article.objects.filter(phase=phase[0],
                                                      quarter=quarter[0])
            article_by_week = {}
            for article in quarter_articles:
                article_by_week[article.week] = article.article_title_data()
            if len(article_by_week):
                article_by_quarter.setdefault(quarter[0], {})
                article_by_quarter[quarter[0]] = article_by_week
        if len(article_by_quarter):
            articles_by_time.setdefault(phase[0], {})
            articles_by_time[phase[0]] = article_by_quarter

    return {'category': articles_by_category,
            'time': articles_by_time
            }
