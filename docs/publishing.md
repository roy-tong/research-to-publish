# 发布与回执

## 网站

1. `build` 后检查稿件与来源，真正检查完才 `review`。
2. `export --to 新版本目录 --site-repo 现有Jekyll仓库` 写 `_posts/YYYY-MM-DD-topic-id.md`。同名文件停止；既有文章修订需人工检查 diff，不强制覆盖。
3. 如果目标站点有 `_data/knowledge_topics.json`，在 `editorial.json` 的 site 中填写有效的 `knowledge_topic` 和 `knowledge_units`；导出会校验主题及资料存在，生成文章 front matter，让现有网站自动建立知识库回链。不修改原索引。
4. 按站点规范构建。Roy 的站点要求 `bundle exec jekyll build`、`python3 scripts/verify_knowledge.py` 和 `python3 scripts/verify_library.py`。
5. 在已授权发布范围内使用正常 Git 流程提交／推送或提 PR，CLI 不自动推送。创建 PR 的宿主 agent 应附到当前任务。
6. 检查部署和线上正文后记录真实回执：

```bash
r2p --workspace /work/editorial record my-research --channel site --url https://example.com/notes/my-research/ --note '已核对线上正文和部署版本'
```

回执为操作者核验记录，CLI 不伪装已联网验证。日期由 `editorial.json` 显式指定。

## 公众号与小红书

打开 `wechat.html`，复制文章区域到编辑器，手机预览后发布。HTML 使用内联样式和纯文本段落；保留 Markdown 备份。

`xiaohongshu.json` 包含标题、正文与每页结构；`cards/*.svg` 是1080×1440可编辑图稿。平台需要 PNG 时用常用图像工具转换；例如装有 CairoSVG 的环境：

```bash
cairosvg cards/01.svg -o cards/01.png
```

也可使用本项目的可选 PNG 渲染器（Pillow，真实字体度量检查，不依赖浏览器）：

```bash
r2p --workspace /work/editorial rasterize --package /work/releases/my-research-v1 --to /work/releases/my-research-v1-png --font /path/to/chinese-font.ttf
```

`python3 -m pip install '.[images]'` 安装可选依赖。字体由使用者提供，不随仓库打包。PNG 目录也必须是新目录，避免覆盖手动修图。

CairoSVG 不是本项目运行依赖。检查实际字体与裁切。固定模板适合短观点，不伪造产品照片。

社媒可提前起草，正式分发建议在网站上线核验后完成；每篇必须独立可读。公众号不加商业转化，小红书商品安排另行决定。发布后分别 `record --channel wechat` 或 `xiaohongshu`。`status` 提示哪些已发版本需要修订；不要把交付包当作发布成功。

## GitHub 开源

仅提交代码、docs、Skill、合成 examples、tests 与 CI。私有工作台、真实会话、研究原稿、机器路径、凭据不进入代码发布包。运行测试与 demo，再检查待提交差异。远端仓库名称、可见性、创建与推送按用户授权执行；“可发布”不等于已经上线。
