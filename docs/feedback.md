# 渠道选择、反馈与影响查询

以下全为合成示例。运行时使用自己的私有工作台。

```bash
r2p --workspace /work/editorial route my-research --channels wechat --reason '本轮只有专业论证增量，网站已有完整研究'
r2p --workspace /work/editorial brief my-research
r2p --workspace /work/editorial validate my-research
r2p --workspace /work/editorial build my-research
```

`route` 保留原三端草稿，只构建、校验和导出所选渠道；保留的旧草稿不会进入公开包。至少选一个渠道；纯研究阶段不 build 即可。渠道变更记录理由并使原审核失效。新建专题也接受 `topic ... --channels site wechat`。旧专题缺少 channels 字段时沿用三端行为。

仅社媒专题不能使用 `export --site-repo`，也不能给未选渠道记录发布回执。导出只产出所选渠道，不修改现有站点文章。已存在的网站研究使用正常 diff 更新流程。

## 导入反馈

私有 JSON：

```json
{
  "id": "feedback-001",
  "topic": "my-research",
  "claim": "claim-001",
  "kind": "counterevidence",
  "text": "合成示例：读者指出测试条件与文章声称的范围不同。",
  "provenance": "合成示例，非真实读者反馈",
  "next_action": "核查测试条件，决定缩小边界或补做实验"
}
```

claim 可省略，表示专题级反馈。kind 为 question / expression / counterevidence。provenance 为来源说明，可记录采集日期和授权可用的原始链接，不要求访问受保护的后台。

```bash
r2p --workspace /work/editorial feedback-add --file /work/feedback-001.json
r2p --workspace /work/editorial impact
r2p --workspace /work/editorial impact --source case
r2p --workspace /work/editorial feedback-resolve feedback-001 --decision revised --note '核查后缩小判断范围，修改了 claim 及两段正文'
```

同 ID 同输入幂等，不同输入拒绝覆盖。`revised` 要求指纹已改变；这只证明内容变化，不证明语义修复正确。`no-change` 也必须写核查理由。两种决定都是操作者声明。反证处理后必须重新审核；工具不替作者判断反证真伪。问题和表达反馈不阻断原稿审核。

`impact` 仅报告依赖关系，不调用远端、不自动修正文章。发布回执是已发版本的历史证据，不能用导出包替代。未导入的新远端资料与未记录的读者反馈不在查询覆盖范围内。

## 从 v0.1 升级

无需迁移 workspace schema。增加 feedback.json 与可选 channels / routing_history 字段。渲染器升为第 3 版，旧稿审核指纹会失效；原始材料、旧构建和发布回执都保留。重新 build → 检查 → review → 新目录 export，勿覆盖手工编辑的历史包。
