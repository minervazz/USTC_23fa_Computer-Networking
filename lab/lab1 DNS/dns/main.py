from onl.sim import Environment
from client import DNSClient
from server import DNSServer

env = Environment()
urls = [
    "pic1.zhimg.com",
    "pic2.zhimg.com",
    "pic3.zhimg.com",
    "www.feest.net",
    "ward.org",
    "www.roberts.com",
    "thiel.com",
    "www.ryan.com",
    "mohr.biz",
    "www.morar.com",
    "www.lowe.net",
    "feil.info",
    "zieme.com",
    "www.powlowski.org",
    "www.kuphal.com",
    "www.baidu.com",
    "www.douban.com",
    "www.youdao.com"
]

client = DNSClient(env, urls=urls, debug=True)
server = DNSServer(env, True)
client.out = server
server.out = client

env.run(client.proc)
print(client.responses)
