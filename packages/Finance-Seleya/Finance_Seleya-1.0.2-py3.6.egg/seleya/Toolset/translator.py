import pdb,os
import numpy as np
import httpx,httpcore,typing,math,time
from httpx import Timeout
from googletrans import urls, utils
from googletrans.utils import rshift
from googletrans import Translator as GTranslator
from googletrans.gtoken import TokenAcquirer as GTokenAcquirer
from googletrans.constants import (
    DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES,
    DEFAULT_RAISE_EXCEPTION, DUMMY_DATA
)
from googletrans.models import Translated, Detected
max_retries = 5
retry_interval = 2

EXCLUDES = ('en', 'ca', 'fr')

class TokenAcquirer(GTokenAcquirer):
    def _update(self, client):
        """update tkk
        """
        # we don't need to update the base TKK value when it is still valid
        now = math.floor(int(time.time() * 1000) / 3600000.0)
        if self.tkk and int(self.tkk.split('.')[0]) == now:
            return
        
        for i in range(1, max_retries + 1):
            r = client.get(self.host)
            raw_tkk = self.RE_TKK.search(r.text)
            if raw_tkk is not None:
                break
            time.sleep(retry_interval)
            
        if raw_tkk:
            self.tkk = raw_tkk.group(1)
            return
        else:
            return
            

        # this will be the same as python code after stripping out a reserved word 'var'
        code = self.RE_TKK.search(r.text).group(1).replace('var ', '')
        # unescape special ascii characters such like a \x3d(=)
        code = code.encode().decode('unicode-escape')

        if code:
            tree = ast.parse(code)
            visit_return = False
            operator = '+'
            n, keys = 0, dict(a=0, b=0)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    name = node.targets[0].id
                    if name in keys:
                        if isinstance(node.value, ast.Num):
                            keys[name] = node.value.n
                        # the value can sometimes be negative
                        elif isinstance(node.value, ast.UnaryOp) and \
                                isinstance(node.value.op, ast.USub):  # pragma: nocover
                            keys[name] = -node.value.operand.n
                elif isinstance(node, ast.Return):
                    # parameters should be set after this point
                    visit_return = True
                elif visit_return and isinstance(node, ast.Num):
                    n = node.n
                elif visit_return and n > 0:
                    # the default operator is '+' but implement some more for
                    # all possible scenarios
                    if isinstance(node, ast.Add):  # pragma: nocover
                        pass
                    elif isinstance(node, ast.Sub):  # pragma: nocover
                        operator = '-'
                    elif isinstance(node, ast.Mult):  # pragma: nocover
                        operator = '*'
                    elif isinstance(node, ast.Pow):  # pragma: nocover
                        operator = '**'
                    elif isinstance(node, ast.BitXor):  # pragma: nocover
                        operator = '^'
            # a safety way to avoid Exceptions
            clause = compile('{1}{0}{2}'.format(
                operator, keys['a'], keys['b']), '', 'eval')
            value = eval(clause, dict(__builtin__={}))
            result = '{}.{}'.format(n, value)

            self.tkk = result

    def do(self, text, client: httpx.Client):
        self._update(client)
        tk = self.acquire(text)
        return tk
    
class Translator(GTranslator):
    def __init__(self, service_urls=None, user_agent=DEFAULT_USER_AGENT,
                 raise_exception=DEFAULT_RAISE_EXCEPTION,
                 proxies: typing.Dict[str, httpcore.SyncHTTPTransport] = None,
                 timeout: Timeout = None,
                 http2=True):
        self.client = httpx.Client(http2=http2)
        if proxies is not None:  # pragma: nocover
            self.client.proxies = proxies

        self.client.headers.update({
            'User-Agent': user_agent,
        })

        if timeout is not None:
            self.client.timeout = timeout

        self.service_urls = service_urls or ['translate.google.cn']
        self.token_acquirer = TokenAcquirer(
            client=self.client, host=self.service_urls[0])
        self.raise_exception = raise_exception
      
    def _update_proxy(self):
        proxy_ips = os.environ['proxy'] if 'proxy' in os.environ else None
        if proxy_ips is None:
            return None
        proxy_ips = proxy_ips.split(',')
        pos = np.random.randint(0,len(proxy_ips))
        return {'http':proxy_ips[pos]}
    
    def _translate(self, text, dest, src, override):
        token = ''
        for i in range(1, max_retries + 1):
            #代理更新
            self.client.proxies = self._update_proxy()
            token = self.token_acquirer.do(text, self.client)
            if token != '635410.635410':
                break
            time.sleep(retry_interval)
                
        params = utils.build_params(query=text, src=src, dest=dest,
                                    token=token, override=override)

        url = urls.TRANSLATE.format(host=self._pick_service_url())
        reponse = self.client.get(url, params=params)

        if reponse.status_code == 200:
            data = utils.format_json(reponse.text)
            return data

        if self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                reponse.status_code, self.service_urls))

        DUMMY_DATA[0][0][0] = text
        return DUMMY_DATA