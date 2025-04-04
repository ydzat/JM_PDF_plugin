# JM PDF Plugin

适用于**LangBot+NapCat**的漫画下载插件🧩，将你想看的漫画转换为PDF发送到QQ群聊/QQ私信中，支持缓存，指定章节下载，文案匹配，定时撤回，关键词搜索，白名单管理✨

## 插件功能🎨

- [x] 下载漫画并转换为PDF，转发到群聊/私信
- [x] 多章节漫画指定章节转换
- [x] 匹配文案对应jmID
- [x] 定时撤回，更适合Bot体质
- [x] 缓存已下载漫画，自动清理较早缓存 
- [x] 关键词搜索漫画
- [x] 白名单管理
- [x] 指令管理  

## 使用方法❗

### 插件安装🛠️

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/AmethystTim/JM_PDF_plugin.git
```
或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

### 网络配置🛜

访问`NapCat`的webui（默认为`http://127.0.0.1:6099`），在**网络配置**栏目中新建**HTTP服务器**，主机为`127.0.0.1`，端口为`3000`

<div align="center">

<img src="./images/napcat_1.png" width="60%">

</div>

> 若发生端口冲突，请修改端口为其他值，同时将`main.py`文件中`self.napcat = NapCatApi('127.0.0.1', 3000)`中的端口修改为新端口

### 偏好配置🔧

- 修改`config.yml`中的`base_dir`为你想存储漫画的目录

```yaml
# Github Actions 下载脚本配置
version: '2.0'

dir_rule:
  base_dir: "C:\\Users\\Hello\\Desktop\\downloads" # 漫画/PDF的存储目录
  rule: Bd_Aid_Pindex

download:
  cache: true # 如果要下载的文件在磁盘上已存在，不用再下一遍了吧？
  image:
    decode: true # JM的原图是混淆过的，要不要还原？
    suffix: .jpg # 把图片都转为.jpg格式
  threading:
    # batch_count: 章节的批量下载图片线程数
    # 数值大，下得快，配置要求高，对禁漫压力大
    # 数值小，下得慢，配置要求低，对禁漫压力小
    # PS: 禁漫网页一般是一次请求50张图
    batch_count: 45

# 插件项配置，若不需要请使用“#”注释掉
plugins:
  after_init:
    - plugin: login # 登录插件，以下载某些需要登录才能下载的漫画，需要配置登录信息
      kwargs:
        username: your_username # 用户名
        password: your_password # 密码
```

- 编辑`commands.yml`，可以自定义白名单、激活/禁用指令，请根据自己的需求进行修改

```yaml
# 插件指令管理

# 白名单机制，启用后仅允许白名单群聊使用指令
whitelist: 
  # 是否启用群聊白名单
  enabled: false
  # 白名单群聊id
  groups: [
    114514,
  ]

# 指令管理列表，若需禁用某指令，则将其对应值由true修改为false
commands: [
  # 指令：/jm [jmID]
  "/jm [ID]": true,
  # 指令：/jm [jmID] [chapter]
  "/jm [ID] [CHAPTER]": true,
  # 指令：文案匹配
  "[text]": true,
  # 指令：/jm search [keyword]
  "/jm search [KEYWORD]": true,
]
```

## 指令🤖

|指令|说明|参数|备注|
|-|-|-|-|
|`/jm`||||
|`/jm [jmID]`|根据禁漫号下载漫画|`jmID`|`jmID`：漫画ID|
|`/jm [jmID] [chapter]`|下载指定章节漫画|`jmID` `chapter`|`chapter`：指定章节|
|`/jm search [keyword]`|搜索漫画|`keyword`|`keyword`：搜索关键字|

## 演示✨

### 单章节漫画

<div align="center">

<img src="./images/readme.png" width="65%">

</div>

### 多章节漫画

<div align="center">

<img src="./images/readme_multichap1.png" width="65%">

</div>

<div align="center">

<img src="./images/readme_multichap2.png" width="65%">

</div>

### 文案匹配

<div align="center">

<img src="./images/readme_match.png" width="65%">

</div>

### 搜索漫画

<div align="center">

<img src="./images/readme_search.png" width="55%">

<img src="./images/readme_searchres.png" width="65%">

</div>

## 计划实现🔮

先挖坑，之后随缘填，有任何想法欢迎提issue或PR

- [x] 定时撤回
- [x] 定期清理缓存漫画
- [x] 搜索漫画
- [ ] 获取分类/排行榜

## 常见问题❓

|Q|A|
|-|-|
|插件加载失败|请按照README中的安装步骤进行，并确保您的插件**目录名称**为`JM_PDF_plugin`|
|漫画下载失败|1. 检查网络配置，推荐添加网络代理<br>2. 检查`jmcomic`包是否为最新版本，建议`pip install -U jmcomic`后重启bot（issue [#23](https://github.com/AmethystTim/JM_PDF_plugin/issues/23)）|
|与`langbot`内置AI对话冲突|issue [#4](https://github.com/AmethystTim/JM_PDF_plugin/issues/4)|
|`Docker`部署langbot导致的路径问题|issue [#9](https://github.com/AmethystTim/JM_PDF_plugin/issues/9)|


> 有其他问题欢迎提issue或在交流群讨论

## 致谢🤝

- **用于爬取JM的Python API封装**：[JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) by [hect0x7](https://github.com/hect0x7)
- **图像转PDF**：[image2pdf](https://github.com/salikx/image2pdf) by [salikx](https://github.com/salikx)
