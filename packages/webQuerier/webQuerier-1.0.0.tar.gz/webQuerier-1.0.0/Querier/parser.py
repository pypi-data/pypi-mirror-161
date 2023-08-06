import urllib.parse
from . import util


class Parser:
    def __init__(self, url: str):
        self.query_list = util.NonRewritable()
        self.url = url
        self.default = {}

    def __getattr__(self, name: str):
        if name in self.query_list:
            return self.query_list[name]

        else:
            return None

    def check(self, query: str) -> bool:
        return query in self.query_list

    def add(self, query: str, default_value=None):
        self.default[query] = default_value

    def parse(self) -> dict:
        split = self.url.split('?')

        if len(split) > 1:
            queries = split[1].split('&')

            for query in queries:
                split = query.split('=', 1)
                key = split[0]

                if len(split) > 1:
                    value = split[1]
                    self.query_list[key] = urllib.parse.unquote(value)

                else:
                    if key in self.default:
                        self.query_list[key] = self.default[query]

                    else:
                        self.query_list[key] = None

        for query in self.default:
            if query not in self.query_list:
                self.query_list[query] = self.default[query]

        return self.query_list
