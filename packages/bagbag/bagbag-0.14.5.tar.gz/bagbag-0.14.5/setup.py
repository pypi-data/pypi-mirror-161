# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bagbag', 'bagbag.Funcs', 'bagbag.Tools']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.1.3,<3.0.0',
 'PyMySQL>=1.0.2,<2.0.0',
 'ipdb>=0.13.9,<0.14.0',
 'langid>=1.1.6,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'orator>=0.9.9,<0.10.0',
 'prometheus-client>=0.14.1,<0.15.0',
 'redis>=4.3.4,<5.0.0',
 'requests>=2.28.1,<3.0.0',
 'selenium>=4.3.0,<5.0.0',
 'telethon>=1.24.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'bagbag',
    'version': '0.14.5',
    'description': 'An all in one python library',
    'long_description': '# bagbag\n\nAn all in one python library\n\n# Install \n\n```bash\npip3 install bagbag --upgrade\n```\n\n# Library\n\n* Lg 日志模块\n  * Lg.SetLevel(level:日志级别:str)\n  * Lg.SetFile(path:日志路径:str, size:文件大小，MB:int, during:日志保留时间，天:int, color:是否带ANSI颜色:bool=True, json:是否格式化为json:bool=False):\n  * Lg.Debug(message:日志内容)\n  * Lg.Trace(message:日志内容)\n  * Lg.Info(message:日志内容)\n  * Lg.Warn(message:日志内容)\n  * Lg.Error(message:日志内容)\n* String(string:str) 一些字符串处理函数\n  * HasChinese() -> bool 是否包含中文\n  * Language() -> str 语言\n* Time 时间\n  * Strftime(format:str, timestamp:float|int) -> str\n  * Strptime(format:str, timestring:str) -> int\n* Re 正则\n  * FindAll(pattern: str | Pattern[str], string: str, flags: _FlagsType = ...) -> list\n* Base64\n  * Encode(s:str) -> str\n  * Decode(s:str) -> str\n* Json\n  * Dumps(obj, indent=4, ensure_ascii=False) -> str\n  * Loads(s:str) -> list | dict\n* Tools 一些工具\n  * URL(url:str)\n    * Parse() -> URLParseResult\n    * Encode() -> str\n    * Decode() -> str\n  * PrometheusMetricServer(listen:str="0.0.0.0", port:int=9105)\n    * NewCounter(name:str, help:str) -> prometheusCounter\n      * Add(num:int|float=1)\n    * NewCounterWithLabel(name:str, labels:list[str], help:str) -> prometheusCounterVec\n      * Add(labels:dict|list, num:int|float=1)\n    * NewGauge(name:str, help:str) -> prometheusGauge\n      * Set(num:int|float)\n    * NewGaugeWithLabel(name:str, labels:list[str], help:str) -> prometheusGaugeVec\n      * Set(labels:dict|list, num:int|float=1)\n  * Queue(db:Tools.MySql|Tools.SQLite)\n    * New(queueName="__queue__empty__name__") -> NamedQueue\n      * Size() -> int\n      * Get(waiting=True) -> str|None\n      * Put(string:str)\n  * Selenium(SeleniumServer:str=None)\n    * ResizeWindow(width:int, height:int)\n    * ScrollRight(pixel:int)\n    * ScrollLeft(pixel:int)\n    * ScrollUp(pixel:int)\n    * ScrollDown(pixel:int)\n    * Url() -> str\n    * Cookie() -> List[dict]\n    * SetCookie(cookie_dict:dict)\n    * Refresh()\n    * GetSession() -> str\n    * Get(url:str)\n    * PageSource() -> str\n    * Title() -> str\n    * Close()\n    * Find(xpath:str, waiting=True) -> SeleniumElement\n      * Clear()\n      * Click()\n      * Text() -> str\n      * Attribute(name:str) -> str\n      * Input(string:str)\n      * Submit()\n      * PressEnter()\n  * Telegram(appid:str, apphash:str, sessionString:str=None)\n    * SessionString() -> str\n    * ResolvePeerByUsername(username:str) -> TelegramPeer\n      * History(limit:int=100, offset:int=0) -> list\n      * Resolve() # 如果手动根据ID初始化一个TelegramPeer实例, 调用这个函数可以补全这个ID对应的Peer的信息\n  * ProgressBar(iterable_obj, startfrom=0, total=None, title=None, leave=False)\n  * Redis(host: str, port: int = 6379, database: int = 0, password: str = "")\n    * Set(key:str, value:str, ttl:int=None) -> (bool | None)\n    * Get(key:str) -> (str | None)\n    * Del(key:str) -> int\n    * Lock(key:str) -> RedisLock\n      * Acquire()\n      * Release()\n  * MySQL(host: str, port: int, user: str, password: str, database: str, prefix:str = "")\n  * SQLite(path: str, prefix:str = "")\n    * Execute(sql: str) -> (bool | int | list)\n    * Tables() -> list\n    * Table(tbname: str) -> MySQLSQLiteTable\n      * AddColumn(colname: str, coltype: str, default=None, nullable:bool = True) -> MySQLSQLiteTable\n      * AddIndex(*cols: str) -> MySQLSQLiteTable\n      * Fields(*cols: str) -> MySQLSQLiteTable\n      * Where(key:str, opera:str, value:str) -> MySQLSQLiteTable\n      * WhereIn(key:str, value: list) -> MySQLSQLiteTable\n      * WhereNotIn(key:str, value: list) -> MySQLSQLiteTable\n      * WhereNull(key:str) -> MySQLSQLiteTable\n      * WhereNotNull_WillNotImplement(key:str)\n      * OrWhere(key:str, opera:str, value:str) -> MySQLSQLiteTable\n      * OrWhereIn_WillNotImplement(key:str, value: list)\n      * OrderBy(*key:str) -> MySQLSQLiteTable\n      * Limit(num:int) -> MySQLSQLiteTable\n      * Paginate(size:int, page:int) -> MySQLSQLiteTable\n      * Data(value:map) -> MySQLSQLiteTable\n      * Offset(num:int) -> MySQLSQLiteTable\n      * Insert()\n      * Update()\n      * Delete()\n      * InsertGetID() -> int\n      * Exists() -> bool\n      * Count() -> int\n      * Find(id:int) -> map\n      * First() -> map\n      * Get() -> list\n      * Columns() -> list[map]',
    'author': 'Darren',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/darren2046/bagbag',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
