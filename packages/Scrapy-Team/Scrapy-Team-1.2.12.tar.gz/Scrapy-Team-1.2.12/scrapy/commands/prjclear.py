from scrapy.commands import ScrapyCommand
import os
from scrapy.exceptions import UsageError

class Command(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <path>"

    def short_desc(self):
        return "Clear empty folders or cache files left by 'git checkout '"

    def del_pyc_files(self,path):
        # 清除pyc缓存文件
        for root , dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".pyc"):
                    os.remove(os.path.join(root, name))
    def del_empty_dirs(self,path):
        # 清除空目录
        for root , dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                if not os.listdir(os.path.join(root, name)):
                    os.rmdir(os.path.join(root, name))

    def run(self, args, opts):
        if len(args) < 1:
            path = "."
        elif len(args) > 1:
            raise UsageError("No more parameters are supported")
        else:
            path = args[0]
        self.del_pyc_files(path)
        self.del_empty_dirs(path)
