from scrapy import signals
import base64,random
# from Team_Public.configs import dnot_use_proxy_spiders
from scrapy.utils.conf import get_config


class ProxyMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, proxies, weights):
        self.proxies = proxies
        # 优先settings中参数PROXIES_WEIGHTS配置代理随机权重值
        self.weights = [eval(i.get("weights","1")) for i in proxies] if not weights else weights 

    @classmethod
    def from_crawler(cls, crawler): 
        proxies = [{i:j for i,j in get_config()[proxy].items()} for proxy in get_config().sections() if proxy.startswith("proxy_no")]
        weights = [i for i in [crawler.settings.get("PROXIES_WEIGHTS",{}).get(proxy) for proxy in get_config().sections() if proxy.startswith("proxy_no")] if i is not None]
        s = cls(proxies=proxies,weights=weights)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        proxy = random.choices(self.proxies,weights=self.weights)[0]
        proxyUser = proxy.get("proxy_user")
        proxyPass = proxy.get("proxy_pass")
        proxyServer = proxy.get("proxy_server")
        if proxyUser and proxyPass and proxyServer:
            proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
            request.meta["proxy"] = proxyServer
            request.headers["Proxy-Authorization"] = proxyAuth

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
