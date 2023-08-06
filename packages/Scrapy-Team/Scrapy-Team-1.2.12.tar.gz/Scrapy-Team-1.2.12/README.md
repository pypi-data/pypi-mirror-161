![016af05cdfc247a801214168e1c955](https://ryan-1307030779.cos.ap-nanjing.myqcloud.com/vscode-md016af05cdfc247a801214168e1c955.jpg)
scrapy-team
=========
Scrapy-team A framework for teamwork based on scrapy

- Package many pipeline files

- Package the Item pipeline files involved in PDF processing

- A Spidermiddleware file is packaged to handle item requests 

scrapy-team 基于scrapy的团队合作模式框架

主要：

- 打包了诸多pipeline管道文件

- 打包处理了涉及pdf处理的item管道文件

- 打包处理了关于item请求的spidermiddleware文件


[ContactProjectTeam](https://github.com/buliqioqiolibusdo)


Usage：
========
#### 2022/8/3 scrapy-team==1.2.12
* 修复:下载管道检测文件不符合时返回空字符串,出现pdf_urls="|".join(["pdf_url",""])局面
* 整合自建代理池功能,增加随机代理权重参数 >> [跳转查看示例](#proxy_random_weights)
* 新增 prjclear 用于清理切换分支遗留的缓存文件和文件夹 >> [跳转查看示例](#prjclear)
* 新增 etl 用于转移数据 >> [跳转查看示例](#etl)
#### 2022/7/7 scrapy-team==1.2.11
* 回滚:mysql管道异步存储,存在断开连接情况
* 新增:资讯item
* 新增:参数CLOSESPIDER_ERROR_STATUS<tuple> :: (<错误状态码>, <出现次数>)
    * 表示出现指定多少次状态码之后主动关闭爬虫
#### 2022/6/13 scrapy-team==1.2.10
* 保留scrapy基础命令,将team模式命令独立出来,创建团队项目使用newteam代替startproject,创建爬虫用jointeam代替genspider,运行爬虫用runteam或者crawl
* 新增命令辅助创建爬虫注册配置
* 存库管道集体变更成异步存储
#### 2022/5/31 scrapy-team==1.2.8
* 更改mongo管道存储月表
#### 2022/5/12 scrapy-team==1.2.5
* 修正布隆过滤器日志警告异常
* 更新环境依赖shell
#### 2022/5/10 scrapy-team==1.2.0
* 新增布隆过滤器item管道,指定Data_Size(估算数据量)和Aim_Set(除重字段)后对爬虫名下整周期item进行除重过滤
* 向下兼容scrapyer 1.5.6版本 对不存在scrapy.cfg项目进行部分兼容
* 为避免重复引用中间件和管道,对custom_settings中引用"scrapy.xcc_"开头模块进行限制
    * 示例:
    ![变动说明](https://ryan-1307030779.cos.ap-nanjing.myqcloud.com/img/SM_]OH220OGR4B@5U][R1GH.jpg)
* 管道与中间件配置从cfg硬替换custom_settings模式,切换成cfg配置update补充custom_settings模式
* 修正了双日志异常情况
* 新增shell脚本安装更新环境,对冲突依赖进行剔除
* 增加pdf检测损坏功能,并对eof缺失部分进行补全后检测(持续跟进pdf种类变化)

#### 2022/5/6 scrapyer==1.5.11
* 新增 spider_register 爬虫注册机制，爬虫名集中配置，爬虫类中不用name属性，组件使用开关情况也在配置中写明
* 修改阶梯配置 spider_register未指定的取custom_settings模块管道配置
* 默认将所有scrapy框架非基础组件关闭


#### 2022/4/25 scrapyer==1.5.8
* ~~设置switch_register 管道组件注册机智~~
* ~~重新规则settings文件，默认将所有scrapy框架组件打开~~
* scrapy.cfg中正式，测试双配置，中间件通过.bashrc IF_PROD 判断是否是正式环境
* 爬虫随机代理修改为请求随机代理
* 修改创建项目和爬虫命令，按人物>项目>爬虫名分层结构创建，一并生成main文件
* 阿里云资源链接目录更改为hash方式处理

### 目录结构
```
├─Command(命令流程)
├─Scrapy_Prj(Scrapy物料采集项目)
|  ├─middlewares
|  ├─pipelines
|  ├─items.py
|  ├─settings
|  └─spiders
|      ├─xxxx(role)
|      └─...
├─Non_Scrapy_Prj(非Scrapy项目)
│  ├─...(feapder/asycio/multiprocessing)
├─.gitignore(git忽略文件)
├─requirements.txt(依赖库)
├─Team_Public(公共方法公共配置)
└─....
```

* 拉代码,ide创建个人分支

* 创建环境
* 安装依赖
    > 运行init环境依赖
    ``` 
   $pwd$ \Command\_win_env_init.bat
   eg: e:\news\Command\_win_env_init.bat
    ```


* 创建爬虫项目
    ```
    scrapy newteam <someprj>
    eg: scrapy newteam saas
    ```
    * 备注: 创建项目(scrapy.cfg保有单一存库方式正式和测试各一套配置,如果存在不同项目存不同mongo情况建议分出来单独项目)

* 创建爬虫文件以及配置
    ```
    scrapy jointeam <somebody> <somewebsite> <somecrawl>
    eg: scrapy jointeam zhizhong semiee detailcrawl
    ```

* 单项目完成后推代码到gitlab
* 定期review合并代码,pull到DEMP中设置周期调度并监控速度及异常



<p id="proxy_random_weights"></p> 

##### 新增随机代理权重值

* 用法一：在scrapy.cfg文件的代理配置的WEIGHTS中添加权重参数（scrapy.cfg为项目公用文件，不可私自配参）

```
    ## 例如：
    [proxy_no.1_cfg]
    # Self-built domestic tunnels
    PROXY_USER= iceasy
    PROXY_PASS= xcc2022
    PROXY_SERVER= http://10.8.108.201:9900 
    WEIGHTS = 7/10
```


* 用法二：项目在爬虫文件custom_settings中添加（特殊项目需要调整，询问后在爬虫文件中调参）
```
    ## 表示取scrapy.cfg中诸多代理隧道配置，其中如proxy_no.1_cfg配置的权重为1/<权重值合计>，例如当前表示随机到proxy_no.1_cfg代理配置的概率为1/7
    custom_settings = dict(
        PROXIES_WEIGHTS={
            "proxy_no.1_cfg":1,
            "proxy_no.1.1_cfg":1,
            "proxy_no.1.2_cfg":1,
            "proxy_no.2_cfg":1,
            "proxy_no.3_cfg":1,
            "proxy_no.4_cfg":1,
            "proxy_no.5_cfg":1,
        }
    )
```

<p id="prjclear"></p> 

##### scrapy prjclear 用法说明

* 用法：  "scrapy prjclear <path>"

```
    ## 例如：
    scrapy prjclear 
    或者：
    scrapy prjclear Scrapy_Prj
```


<p id="etl"></p> 

##### scrapy etl 用法说明

* 用法：  "scrapy etl <Set Name> <Filter Key> <Filter Value> <Aim Set Name>"

```
    ## 例如：将scrapy.cfg 中dev配置库转移到prod库
    scrapy etl ware_category_copy brand_name Winsemi
```
