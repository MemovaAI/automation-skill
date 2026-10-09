# 飞书自动报销（私有团队版）

用于公司内部处理费用报销和付款申请：先检查费用与凭证，完成查重，再通过飞书桌面端准备表单、选择已保存账户、上传原始附件；最终提交前由当前员工确认，提交后验单并归档队列副本。

本仓库包含公司内部审批表标识和操作规则，必须保持为私有仓库。不要将发票、工资表、身份证件、银行卡号、飞书凭证或真实审批导出文件提交到 GitHub。

## 目录

```text
.agents/plugins/marketplace.json
plugins/feishu-reimbursement/
  plugin.json
  skills/process-feishu-reimbursements/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/find_exact_duplicates.py
```

## 使用前提

- macOS 上已安装并登录 Codex 和飞书桌面端；
- 已安装并可使用 `lark-cli`；
- 已启用 Codex Computer Use，以及控制飞书、Finder 和系统文件选择器所需的系统权限；
- 使用者本人完成飞书 OAuth 授权，不能共用他人的登录状态；
- 能访问团队共享的 `报销工作站/待提交` 和 `报销工作站/已处理`；
- 飞书中已经保存并可选择本人的收款账户。

首次运行时，skill 会检查这些条件并进行可撤销的文件选择器测试，不会直接提交报销。

## 安装与更新

仓库管理员先在 GitHub 私有仓库中邀请同事，并确认对方已接受邀请。团队成员需要在当前电脑具备访问该私有仓库的 GitHub 凭据。

添加团队插件源：

```bash
codex plugin marketplace add MemovaAI/automation-skill --ref main
```

安装报销插件：

```bash
codex plugin add feishu-reimbursement@memova-automation-skills
```

安装后重新打开 Codex 会话，再发起一次“使用自动化报销 skill，只做首次环境检查，不提交”的请求。

需要获取仓库更新时运行：

```bash
codex plugin marketplace list
codex plugin marketplace upgrade <列表中显示的 marketplace 名称>
```

如果团队暂时不使用插件市场，也可以在 GitHub 网页下载 ZIP，解压后把完整的 `plugins/feishu-reimbursement/skills/process-feishu-reimbursements` 文件夹复制到个人 Codex Skills 目录；不要只复制 `SKILL.md`。这种方式不会自动获取后续更新。

## 首次运行仍需本人完成

安装成功不等于可以立即提交真实报销。每位同事第一次使用时仍需完成：

1. 用自己的公司飞书账号完成 OAuth 授权；
2. 允许 Codex Computer Use 控制飞书和系统文件选择器；
3. 在 macOS 中批准屏幕录制、辅助功能和必要的自动化权限；
4. 确认可以访问共享报销工作站；
5. 确认飞书中已经保存并能选择本人的收款账户；
6. 完成一次只打开文件选择器、不上传、不提交的可撤销测试。

Skill 会逐项引导并检查这些条件，但不能代替同事批准系统权限、登录个人飞书账号或创建收款账户。完成首次配置后，日常任务通常只需在最终提交前确认一次。

## 常用请求

```text
使用自动化报销 skill，检查待提交目录中以我姓名开头的文件，只准备表单，不提交。
```

```text
使用自动化报销 skill，处理我刚上传的发票；查重、准备飞书报销，最终提交前让我确认。
```

```text
检查这批发票是否已经报销，不要创建或提交申请。
```

## 安全边界

- 报销和付款是不同表单，不为方便而互换；
- 禁止替票、虚构用途或把个人消费描述为公司费用；
- 无票、特殊凭证、税务和研发归集必须由财务或审计复核；
- 默认只读取当前员工姓名前缀的队列文件；
- 只有最终点击“提交”前需要例行确认；
- 提交后必须打开审批详情核对，不能把一次点击视为成功；
- 不得在仓库、日志或聊天总结中保存完整银行卡号或账户号码。

## 团队配置

公司组织、审批表标识、共享队列和财务复核角色位于：

```text
plugins/feishu-reimbursement/skills/process-feishu-reimbursements/references/team-config.md
```

飞书组织、表单或财务负责人发生变化时，先更新该文件并验证，再发布新版本。

## 版本规则

- `0.1.x`：不改变主要流程的修正和文案调整；
- `0.x.0`：新增能力、表单或流程步骤；
- `x.0.0`：存在需要团队重新配置或培训的不兼容变化。

每次修改后先在测试材料和草稿模式下验证；涉及真实提交时，仍需在最后一步由使用者明确确认。
