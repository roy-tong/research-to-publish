# 数据与状态

## 三种不同的可追溯对象

Source：ID、SHA256、origin、可选 public_url、snapshot、采集时间。Local 来源保留本机路径，GitHub 来源保留 repo／ref／path，ChatGPT 保留会话与读取范围；全部只在私有工作台。

Topic：ID、研究问题、来源ID、claims。每个 claim 包含性质、判断文本、边界、准确的证据原文。不是按文章字数拆卡，也不自动声称事实核验成功。

Editorial：site／wechat／xiaohongshu。三份独立编辑内容，段落与卡片用 claims 字段连回研究。site 可按现有 Jekyll 主题填写 knowledge_topic、knowledge_units、lang、tags。

## 状态转换

导入 → 研究与编辑 → 结构校验 → 构建 → 内容复核 → 本地交付 → 核验线上发布 → 发布回执。

CLI 自动化来源管理与构建；agent/作者承担研究和编辑；网站及社媒由正常发布通道执行。不存在通过隐藏 API 一键发帖的旁路。

指纹包括 topic、editorial、来源当前内容和来源元数据、渲染格式版本。review 绑定指纹；任何这些依赖变动使审核失效。build 存完整文件哈希，export 再次检查。发布回执绑定当时指纹，不覆盖历史。

生成数据保存在 `builds/topic/fingerprint/`，相同输入可重建。对本地原文件，validate/status 检测是否变化；对 GitHub 和 ChatGPT，需要主动更新导入版本。sources 旧快照和元数据保留在源ID目录。

## v0.2 的增量状态

Topic 的 channels 为可选字段，缺失时兼容三个渠道。routing_history 保留渠道决策。feedback.json 保存私有编辑反馈与操作者处理记录；打开的 counterevidence 阻止该专题审核和导出，处理后必须重新审核。status 区分内容版本变化需修订与反证打开需复核；impact 汇总依赖关系。详见 [反馈](feedback.md)。

渲染器版本 3 使旧审核指纹失效，旧数据保留；不修改 workspace schema。

## 公开边界

代码仓库只保存工具、文档与合成例子。公开交付包不包含私有来源 origin、原始快照或证据引文；保留文章明确选定的公开参考链接。文章正文是否可公开仍由真实编辑复核，结构检查不能代替。

review 是本地工作流标记，并不是密码学签名或多人审批系统。假设单一可信作者顺序执行；不提供并发写、多租户权限与自动原子跨目录发布。

## 扩展位置

来源解析在 core.py 的 ingest/chatgpt_text；新来源应转换为相同快照契约。写作不绑定模型厂商，由 Skill 与 brief 驱动。站点输出在 build/export，公众号格式在 render_article，小红书 SVG 在 render_card，PNG 在 cards.py。增加平台先定义受众与编辑字段，再接渲染器，不把一份长文截断后冒充平台适配。
