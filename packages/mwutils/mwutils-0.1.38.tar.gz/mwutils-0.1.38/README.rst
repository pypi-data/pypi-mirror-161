`rst file editor <http://rst.ninjs.org>`_

mwutils

maxwin 团队开发框架utils
**为了兼容windows开发环境，日期时间parse模块采用python-dateutil，但ciso8601的pars性能比之快百倍，如果是linux下安装，请先安装**
"pip install ciso8601"

安装


``$ pip install mwutils``

mw_time.py 单元


.. code-block:: python

    from mwutils.mw_time import *
    # 字符串转为本地日期时间
    print(str2datetime('2018-01-01'))
    print(str2datetime('2018-01-01T12:00:00'))
    print(str2datetime('2018-01-01T12:00:00Z'))
    print(str2datetime('2018-01-01T12:00:00+02:00'))
    # 字符串转日期
    print(str2date('2018-01-01'))
    # 字符串转时间
    print(str2time('11:11:11'))
    # 日期时间转iso8601 tz 格式字符串
    print(datetime2isostr(datetime.now()))
    # 日期时间转本地日期时间字符串
    print(datetime2str(datetime.now()))
    # 日期时间转integer时间戳
    print(datetime2timestamp(datetime.now()))
    # 时间戳转本地日期时间
    print(timestamp2datetimestr(1515579120.0))
    # get locale timezone
    print(get_locale_timezone())
    # min_time(dt1,dt2),max_time(dt1,dt2) 两个日期时间取最小和最大时间

utils.py 单元


.. code-block:: python

    from mwutils.utils import getConfig,hostname
    # 读取config.ini
    print(getConfig('./config.ini')
    # 获取电脑的 hostname
    print(hostname)

mw_consul.py 单元


> 访问consul 中的常用服务配置

.. code-block:: python

    from mw_consul import *
    # reg_service : 向consul中注册服务
    # dereg_service： 注销服务
    # AgentConf() : 獲取本機agent
    # RedisConf() : redis的配置
    # RedisConfMaster()： master redis的配置
    # RedisConfSlave():离本机最近的slave redis 配置
    # DatabaseConf('maxbus'):获取tag=maxbus的database服务的配置
    # KongConf（）：取kong的配置
    # KongAdminConf（）：取kong admin 的配置
    # KafkaConf（）：取kafka的配置
    # Cassandra()：取Cassandra的配置
    # ServiceConf(service_name,tag)：取设定tag，service_name的服务配置

cache.py 单元


> sigleton，内存中只会创建一个实例

.. code-block:: python

    from cache import Cached
    # # Example
    class Spam(metaclass=Cached):
      def __init__(self, name):
          print('Creating Spam({!r})'.format(name))
          self.name = name

sendemail.py 单元


> 发送邮件

.. code-block:: python

    from sendemail import Emailsender

