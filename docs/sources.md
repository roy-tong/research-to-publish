# 来源接入

只导入显式选定文件。原项目留在原正式位置，工作台保存版本快照，不复制整仓库。

## 同步配置

私有工作台旁保存 `sources.local.json`：

```json
{
  "schema_version": 1,
  "sources": [
    {"id": "report", "path": "../project/research.md"},
    {"id": "chat", "path": "inbox/chat.json", "chatgpt": true},
    {"id": "github", "repo": "owner/repo", "ref": "FULL_40_CHAR_COMMIT_SHA", "github_path": "docs/report.md", "public": "https://example.com/research/"}
  ]
}
```

本地路径相对配置文件解析。固定 SHA 避免远端静默变化；刷新时显式选定新版本。私有 GitHub 材料从已授权的本地正式检出导入，不写 token。`sync` 顺序处理，后项失败时前项保留；修复后幂等重跑。

## ChatGPT 导出

选中官方 `conversations.json` 中一个对话 ID，通过 `--conversation-id` 导入。沿 `current_node` 的父节点读取当前分支，不混入另一分支、system/tool 消息或别的聊天。只取文本 parts；未知格式报错，不声称已读图片和附件。

## Chrome 会话摘录

宿主 agent 遵循已安装 Chrome 技能，认领实际标签页列表中的目标会话，读取可见正文。不要读取 cookies、隐藏状态和私有接口；网站禁止访问时停止该来源。

将读到的相关正文保存为封套，然后 `ingest --file … --chatgpt`：

```json
{
  "format": "chatgpt-capture-v1",
  "url": "https://chatgpt.com/c/ACTUAL_ID",
  "title": "实际会话标题",
  "method": "chrome-visible-text",
  "coverage": "visible-excerpt",
  "text": "实际读取的选定正文，不含侧栏和其他对话"
}
```

用户粘贴用 `method: user-provided-paste`，不能标成实时浏览器采集。登录会话 URL 仅留私有来源台账；`public_url` 只用于可公开资料。模型输出提供思路，事实需追原始来源。

## 修订

同一来源 ID 的新内容产生新快照，旧快照保留。不同 ID 的同文、转载、翻译不视为独立支持。`status` 提示本地文件变化；重新导入后审核失效，旧回执保留。检查受影响判断，修改稿件，重新构建与审核。
