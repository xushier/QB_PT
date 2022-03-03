# QB-PT

需搭配青龙面板使用

青龙添加任务
`ql repo https://ghproxy.com/https://github.com/xushier/QB_PT.git "" "__" "logger|notifier|qbittorrent|get_free|shift"`

添加之后，在环境变量添加
```
QB_URL(QB地址)
QB_USERNAME(QB用户名)
QB_PASSWORD(QB密码)
PUSH_PLUS_TOKEN(PushPlusToken)
XXX_COOKIE(需要刷流的站的cookie)
XXX_RSS_URL(需要刷流的站的rss地址)
XXX_CONFIG(需要刷流的站的筛选和限速配置)
```

# 举例：
刷 hdhome 的话，在环境变量里添加如下 7 个环境变量，或者直接在配置文件里添加如下 7 行，对应值改成你自己的。

HDHOME_CONFIG 的值以 xx-xx-xx 的形式填写，比如 15-800-25 就是筛选 15G 到 800G 的种子，上传限速 25 M/s。

默认筛选免费（包含免费、两倍上传，两倍上传%50下载，%30下载），筛选 HR，筛选过老的种子（默认10分钟之前的会过滤掉）。
```
export QB_URL="http://192.168.1.2:8080"
export USERNAME="username"
export PASSWORD="password"
export PUSH_PLUS_TOKEN="token"
export HDHOME_COOKIE="hdhome_cookie"
export HDHOME_RSS_URL="hdhome_rss_url"
export HDHOME_CONFIG="15-800-25"
```
注：若不需要通知，PUSH_PLUS_TOKEN 随便填就可以，但一定要有。
