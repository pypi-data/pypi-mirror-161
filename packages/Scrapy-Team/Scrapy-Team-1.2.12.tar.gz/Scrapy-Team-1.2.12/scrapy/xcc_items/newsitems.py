# -*- coding: utf-8 -*-

"""
原厂资讯
FactoryNewsItem
FactoryNewsMapItem
FactoryNewsCategoryItem
原厂简讯
FactoryNewSletterItem
突发事件资讯
NewsItemtufa
地方掠影资讯
NewsItemglimpse
"""

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


# 重要字段用'<----'标识,如果与需求不符合要找需求人对一下

# 原厂资讯
class FactoryNewsItem(scrapy.Item):
    table = 'news_detail'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(FactoryNewsItem, self).__init__()

    source = scrapy.Field()  # *来源 <-----
    category = scrapy.Field()  # *分类<-----
    source_url = scrapy.Field()  # *来源链接<-----
    title = scrapy.Field()  # *标题<-----
    content = scrapy.Field()  # *内容<-----
    article_from = scrapy.Field()  # *文章来源<-----
    author = scrapy.Field()  # 作者
    tips = scrapy.Field()  # 标签
    publish_time = scrapy.Field()  # *新闻时间<-----
    create_time = scrapy.Field()  # *创建时间<-----
    creator = scrapy.Field()  # *创建人<-----
    update_time = scrapy.Field()  # 更新时间
    updator = scrapy.Field()  # 更新人
    spider_name = scrapy.Field()  # 爬虫名
    spider_time = scrapy.Field()  # 爬虫时间
    del_flag = scrapy.Field()  # 删除标记
    note = scrapy.Field()  # 备注
    img_url = scrapy.Field()  # *图片链接(文章图片链接"|"做分割) <-----
    img_num = scrapy.Field()  # 用做图片数量(弃用不用写)
    new3 = scrapy.Field()  # 资讯是否公开(弃用不用写)
    abstract = scrapy.Field()  # 摘要
    read_number = scrapy.Field()  # 浏览次数(文章没有则随机2000以内) <-----
    is_open = scrapy.Field()  # 资讯是否公开(网信资讯设置为0) <----- 需要确认是否是网信资讯
    title_en = scrapy.Field()  # 英文标题
    content_en = scrapy.Field()  # 英文内容
    tips_en = scrapy.Field()  # 英文标签
    is_en = scrapy.Field()  # 是否外文（0：否；1：是）(接口设置参数,不用写)
    appdetail_id = scrapy.Field()  # uuid对应品牌id(品牌资讯需要,普通资讯不用写) <----- hash.sha1模式与原厂关联


class FactoryNewsMapItem(scrapy.Item):
    table = 'app_detail_brand'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(FactoryNewsMapItem, self).__init__()

    appdetail_id = scrapy.Field()  # <-----
    brand_id = scrapy.Field()  # <-----


class FactoryNewsCategoryItem(scrapy.Item):
    table = 'news_category'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(FactoryNewsCategoryItem, self).__init__()

    sources = scrapy.Field()  # 来源：cena
    url = scrapy.Field()  # 链接
    level = scrapy.Field()  # 分类级别
    category_name = scrapy.Field()  # 分类名称
    en_name = scrapy.Field()  # 英文-分类名称
    category_id = scrapy.Field()  # 分类id
    p_category_id = scrapy.Field()  # 父类-分类id
    p_category_name = scrapy.Field()  # 父类-分类名称
    p_number = scrapy.Field()  # 子类数量
    jsons = scrapy.Field()  # 额外参数
    attrs = scrapy.Field()  # 属性名称列表
    number = scrapy.Field()  # 总数量
    spider_flag = scrapy.Field()  # 是否爬取当前url: 1是，0否
    spider_number = scrapy.Field()  # 已爬取数量
    spider_date = scrapy.Field()  # 爬虫年月日
    spider_time = scrapy.Field()  # 爬虫时间
    create_time = scrapy.Field()  # 创建时间
    creator = scrapy.Field()  # 创建人
    update_time = scrapy.Field()  # 更新时间
    updator = scrapy.Field()  # 更新人
    del_flag = scrapy.Field()  # 删除标记


# 原厂简讯
class FactoryNewSletterItem(scrapy.Item):
    table = 'app_newsletter'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(FactoryNewSletterItem, self).__init__()

    source = scrapy.Field()  # *来源 <-----
    source_url = scrapy.Field()  # *来源链接<-----
    title = scrapy.Field()  # *标题<-----
    content = scrapy.Field()  # *内容<-----
    article_from = scrapy.Field()  # *文章来源<-----
    author = scrapy.Field()  # 作者
    tips = scrapy.Field()  # 标签
    publish_time = scrapy.Field()  # *新闻时间<-----
    create_time = scrapy.Field()  # *创建时间<-----
    creator = scrapy.Field()  # *创建人<-----
    update_time = scrapy.Field()  # 更新时间
    updator = scrapy.Field()  # 更新人
    del_flag = scrapy.Field()  # 删除标记
    note = scrapy.Field()  # 备注
    image_url = scrapy.Field()  # *图片链接(文章图片链接"|"做分割) <-----
    img_num = scrapy.Field()  # 用做图片数量(弃用不用写)
    nsource = scrapy.Field()  # 资讯来源分类
    reviewer = scrapy.Field()  # 审核人
    read_num = scrapy.Field()  # 用户阅读次数
    is_save = scrapy.Field()  # 是否入库（0：否；1：是）


# 突发事件资讯
class NewsItemtufa(scrapy.Item):
    table = 'news_detail'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(NewsItemtufa, self).__init__()

    source = scrapy.Field()  # *来源 <-----
    country_zh = scrapy.Field()  # 所属国家(中文)<-----
    country_en = scrapy.Field()  # 所属国家(英文)<-----
    city_zh = scrapy.Field()  # *所属城市(中文) <-----
    city_en = scrapy.Field()  # *所属城市(英文) <-----
    source_url = scrapy.Field()  # *来源链接<-----
    title = scrapy.Field()  # *标题<-----
    content = scrapy.Field()  # *内容<-----
    article_from = scrapy.Field()  # *文章来源<-----
    author = scrapy.Field()  # 作者<-----
    tips_zh = scrapy.Field()  # 标签(中文)<-----
    tips_en = scrapy.Field()  # 标签(英文)<-----
    publish_time = scrapy.Field()  # *新闻时间<-----
    create_time = scrapy.Field()  # *创建时间<-----
    creator = scrapy.Field()  # *创建人<-----
    img_url = scrapy.Field()  # *首页图片<-----
    abstract_content = scrapy.Field()  # 摘要<-----
    disaster_type = scrapy.Field()  # 灾害类型<-----
    is_existence = scrapy.Field()  # 是否存在（0：否；1：是）<-----
    status = scrapy.Field()  # 是否存在（0：否；1：是）<-----
    news_type = scrapy.Field()
    aging_start_date = scrapy.Field()  # *开始时间<-----
    aging_end_date = scrapy.Field()  # *失效时间<-----


# 地方掠影资讯
class NewsItemglimpse(scrapy.Item):
    table = 'glimpse_news_detail'  # 正式库/测试库bd-spider

    def __init__(self, *args, **kwargs):
        table_params = {'table': kwargs.get('table', self.table)} if not kwargs.get('table_add', '') \
            else {'table': kwargs.get('table', self.table) + kwargs.get('table_add', '')}
        self.__dict__.update(table_params)
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
        super(NewsItemglimpse, self).__init__()

    source = scrapy.Field()  # *来源 <-----
    country_zh = scrapy.Field()  # 所属国家(中文)<-----
    country_en = scrapy.Field()  # 所属国家(英文)<-----
    city_zh = scrapy.Field()  # *所属城市(中文) <-----
    city_en = scrapy.Field()  # *所属城市(英文) <-----
    source_url = scrapy.Field()  # *来源链接<-----
    title = scrapy.Field()  # *标题<-----
    content = scrapy.Field()  # *内容<-----
    article_from = scrapy.Field()  # *文章来源<-----
    author = scrapy.Field()  # 作者<-----
    tips_zh = scrapy.Field()  # 标签(中文)<-----
    tips_en = scrapy.Field()  # 标签(英文)<-----
    publish_time = scrapy.Field()  # *新闻时间<-----
    create_time = scrapy.Field()  # *创建时间<-----
    creator = scrapy.Field()  # *创建人<-----
    img_url = scrapy.Field()  # *首页图片<-----
    abstract_content = scrapy.Field()  # 摘要<-----
    disaster_type = scrapy.Field()  # 灾害类型<-----
    is_existence = scrapy.Field()  # 是否存在（0：否；1：是）<-----
    status = scrapy.Field()  # 是否存在（0：否；1：是）<-----
    news_type = scrapy.Field()  # 新闻类型(突发时间、政策、地方新闻)<-----
    aging_start_date = scrapy.Field()  # *开始时间<-----
    aging_end_date = scrapy.Field()  # *失效时间<-----
    country_id = scrapy.Field()
    province_id = scrapy.Field()
    city_id = scrapy.Field()
    area_id = scrapy.Field()
    region_id = scrapy.Field()