from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from pkg.core.entities import LauncherTypes
from plugins.JM_PDF_plugin.utils.callapi import *
from plugins.JM_PDF_plugin.utils.image2pdf import *
from plugins.JM_PDF_plugin.utils.undofile import undo_file
from plugins.JM_PDF_plugin.utils.sendfile import send_file
from plugins.JM_PDF_plugin.utils.search import searchManga
import re
import os
import shutil
import asyncio

current_dir = os.path.dirname(__file__)

# 注册插件
@register(name="JMcomicPDF", description="迅速突破卡脖子核心技术", version="1.0", author="Amethyst")
class JMcomicPDFPlugin(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.napcat = NapCatApi('127.0.0.1', 3000)
        config = os.path.join(os.path.dirname(__file__), "config.yml")
        with open(config, "r", encoding="utf8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            self.pdf_dir = data["dir_rule"]["base_dir"]
        self.instructions = {
            "/jm": r"^/jm$",
            "/jm [ID]": r"^/jm (\d+)$",
            "/jm [ID] [CHAPTER]": r"^/jm (\d+) (\d+)$",
            "/jm search [KEYWORD]" : r"^/jm search (.+)$"
        }
        self.waittime = 20  # 自动撤回时间
        self.maxfilecount = 20 # 最大文件数量
        
        commands = os.path.join(os.path.dirname(__file__), "commands.yml")
        with open(commands, "r", encoding="utf-8") as f:
            self.command_manager = yaml.load(f, Loader=yaml.FullLoader)
            for command in self.command_manager.get("commands", []):
                if not list(command.values())[0]:
                    if not self.instructions.get(list(command.keys())[0]):
                        self.instructions[list(command.keys())[0]] = r"^\s\S"
    
    def matchPattern(self, msg):
        '''
        匹配指令
        
        args:
            msg: 指令内容
        return:
            匹配结果
        '''
        res = None
        for pattern in self.instructions:
            if re.match(self.instructions[pattern], msg):
                res = pattern
        return res
    
    # 异步初始化
    async def initialize(self):
        pass

    # 当收到群/私聊消息时触发
    @handler(PersonMessageReceived)
    @handler(GroupMessageReceived)
    async def group_message_received(self, ctx: EventContext):
        # 群聊白名单机制
        if self.command_manager.get("whitelist").get("enabled"):
            if ctx.event.query.launcher_type == LauncherTypes.GROUP:
                if not int(ctx.event.launcher_id) in self.command_manager.get("whitelist").get("groups"):
                    self.ap.logger.info(f"[JM PDF plugin] 群{ctx.event.launcher_id}不在白名单中，忽略命令")
                    return
        msg = str(ctx.event.message_chain).strip()
        # 文案匹配
        if not msg.startswith("/jm"):
            if next((item["[text]"] for item in self.command_manager.get("commands", []) if "[text]" in item), None):
                manga_id = "".join([char for char in msg if char.isdigit()])
                if 6 <= len(manga_id) <= 7:
                    await ctx.reply(MessageChain([
                        Plain(f"检测到jm号{manga_id}")
                    ]))
                    msg = f"/jm {manga_id}"
        # 匹配指令
        match self.matchPattern(msg):
            case "/jm":
                await ctx.reply(MessageChain([
                    Plain("jm卡脖子核心技术\n"),
                    Plain("将jm号对应本子转化为pdf，请输入jm号进行转化，如：/jm 123456\n"),
                    Plain("指定章节转化，如转化jm号为123456的第2章：/jm 123456 2\n"),
                    Plain("jm站内搜索，如：/jm search 偶像大师\n")
                ]))
            case "/jm [ID]":
                manga_id = re.search(r"^/jm (\d+)$", msg).group(1)
                await ctx.reply(MessageChain([
                    Plain(f"正在将jm{manga_id}转换为PDF...\n可能需要10s至1min不等，请耐心等待")
                ]))
                chap = ""
                if not mangaCache(manga_id):
                    match downloadManga(manga_id):
                        case 0:
                            pass
                        case 1:
                            self.ap.logger.info(f"[JM PDF plugin] jm{manga_id}对应漫画不存在")
                            await ctx.reply(MessageChain([
                                Plain(f"jm{manga_id}对应漫画不存在或需要配置登录信息")
                            ]))
                            return
                        case -1:
                            self.ap.logger.info(f"[JM PDF plugin] 未知错误")
                            await ctx.reply(MessageChain([
                                Plain(f"发生未知错误")
                            ]))
                            return
                match convertPDF(manga_id):
                    case 1:
                        await ctx.reply(MessageChain([
                            Plain(f"检测到jm{manga_id}存在多个章节，现在默认转换第一话\n请输入“/jm [jmID] [章节数]”指定章节")
                        ]))
                        chap = "-1"
                    case -1:
                        await ctx.reply(MessageChain([
                            Plain(f"检测到jm{manga_id}存在多个章节，尝试转换第一话，但是第一话不存在\n请输入“/jm [jmID] [章节数]”指定存在章节")
                        ]))
                        return
                self.ap.logger.info(f'[JM PDF plugin] 发送文件：{os.path.join(self.pdf_dir, f"{manga_id}{chap}.pdf")}')
                await send_file(
                    self.napcat, 
                    ctx, 
                    os.path.normpath(os.path.join(self.pdf_dir, f"{manga_id}{chap}.pdf")), 
                    f"{manga_id}{chap}.pdf"
                )
                if ctx.event.query.launcher_type == LauncherTypes.GROUP:
                    await ctx.reply(MessageChain([Plain(f"文件发送完成，{self.waittime}s后自动撤回")]))
                    asyncio.create_task(undo_file(self.napcat, ctx, manga_id, chap, self.waittime))
            case "/jm [ID] [CHAPTER]":
                manga_id = re.search(r"^/jm (\d+) (\d+)$", msg).group(1)
                chap = str(re.search(r"^/jm (\d+) (\d+)$", msg).group(2))
                await ctx.reply(MessageChain([
                    Plain(f"正在将jm{manga_id}章节{chap}转换为PDF...\n可能需要10s至1min不等，请耐心等待")
                ]))
                chap = "-" + chap   # 拼接章节号
                if not mangaCache(manga_id):
                    match downloadManga(manga_id):
                        case 0:
                            pass
                        case 1:
                            self.ap.logger.info(f"[JM PDF plugin] jm{manga_id}对应漫画不存在")
                            await ctx.reply(MessageChain([
                                Plain(f"jm{manga_id}对应漫画不存在或需要配置登录信息")
                            ]))
                            return
                        case -1:
                            self.ap.logger.info(f"[JM PDF plugin] 未知错误")
                            await ctx.reply(MessageChain([
                                Plain(f"发生未知错误")
                            ]))
                            return
                match all2PDF(os.path.join(self.pdf_dir, manga_id), self.pdf_dir, f"{manga_id}{chap}", int(chap.replace('-', ''))):
                    case 0:
                        self.ap.logger.info(f"[JM PDF plugin] jm{manga_id}转换完成")
                    case -1:
                        self.ap.logger.info(f"[JM PDF plugin] jm{manga_id}转换失败-章节{chap.replace('-', '')}不存在")
                        await ctx.reply(MessageChain([
                            Plain(f"jm{manga_id}转换失败-章节{chap.replace('-', '')}不存在")
                        ]))
                        return
                await send_file(
                    self.napcat, 
                    ctx, 
                    os.path.normpath(os.path.join(self.pdf_dir, f"{manga_id}{chap}.pdf")), 
                    f"{manga_id}{chap}.pdf"
                )
                if ctx.event.query.launcher_type == LauncherTypes.GROUP:
                    await ctx.reply(MessageChain([Plain(f"文件发送完成，{self.waittime}s后自动撤回")]))
                    asyncio.create_task(undo_file(self.napcat, ctx, manga_id, chap, self.waittime))
            case "/jm search [KEYWORD]":
                keyword = re.search(r"^/jm search (.+)$", msg).group(1)
                self.ap.logger.info(f"[JM PDF plugin] 搜索关键字：{keyword}")
                await ctx.reply(MessageChain([
                    Plain("获取搜索结果中，请坐和放宽")
                ]))
                try:
                    await asyncio.wait_for(searchManga(self.napcat, ctx, keyword, "site"), timeout=15)
                except asyncio.TimeoutError:
                    await ctx.reply(MessageChain([Plain("搜索超时，可能是网络连接问题，请稍后重试")]))
            case _:
                pass
            
        files = os.listdir(self.pdf_dir)
        files = [f for f in files if not f.endswith(".gitkeep")]    # 忽略.gitkeep
        if len(files) >= self.maxfilecount: # 超过设定文件数量上限清除缓存
            self.ap.logger.info(f"[JM PDF plugin] 超过设定文件数量上限，清除缓存")
            file_time = [{f: os.path.getmtime(os.path.join(self.pdf_dir, f))} for f in files]
            file_time.sort(key=lambda x: list(x.values())[0])
            try:
                for f in file_time[:self.maxfilecount//2]:
                    if os.path.isfile(os.path.join(self.pdf_dir, list(f.keys())[0])):
                        os.remove(os.path.join(self.pdf_dir, list(f.keys())[0]))
                    elif os.path.isdir(os.path.join(self.pdf_dir, list(f.keys())[0])):
                        shutil.rmtree(os.path.join(self.pdf_dir, list(f.keys())[0]))
                self.ap.logger.info(f"[JM PDF plugin] 已清除缓存")
            except PermissionError as e:
                self.ap.logger.error(f"[JM PDF plugin] 权限错误，无法删除文件: {os.path.join(self.pdf_dir, list(f.keys())[0])}. 错误信息: {e}")
            except Exception as e:
                self.ap.logger.error(f"[JM PDF plugin] 删除文件时发生未知错误: {e}")
        
    # 插件卸载时触发
    def __del__(self):
        pass
