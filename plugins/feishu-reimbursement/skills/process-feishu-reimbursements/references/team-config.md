# Team Configuration

This file contains the private team's shared operating configuration. Keep the repository private and review this file whenever the Feishu organization or approval forms change.

## Feishu organization

- Organization: 杭州能量橙子科技有限公司
- Each colleague must sign in and authorize Feishu with their own company account.

## Approval forms

| Purpose | Form | Definition code |
|---|---|---|
| Employee expense reimbursement | 报销申请 | `707F3C6D-50AA-49BF-87A3-E8CBFA6E1EF4` |
| Salary, investment, deposit, supplier, or other outgoing payment | 付款申请 | `2BD96C6D-0979-46DB-9811-403C71C33DCC` |

Verify the visible organization and form name before using either identifier. A matching identifier alone is not sufficient authorization to submit.

## Shared queue

- System of record: the company SharePoint site, document library `公司文档库`.
- Queue root: `公司文档库/报销工作站`
- Pending: `公司文档库/报销工作站/待提交`
- Processed: `公司文档库/报销工作站/已处理/<员工姓名>`
- Resolve the actual site URL, library/drive ID, and pending/processed folder item IDs from the authenticated company SharePoint connection at runtime. Library names alone may be ambiguous; stop and ask for the exact company site/library if there are multiple matches.
- Verify the authenticated company tenant and the library/folder hierarchy before any queue write. Do not create a replacement queue in a personal OneDrive or local directory when access fails.
- OneDrive-synced local paths may be used as upload caches only after mapping them to these company cloud folders. Always verify staging and final archiving through SharePoint server-side listing and content checks. Record cloud links and item IDs in the task result.
- Respect workspace read-only policies. If a current workspace policy requires explicit authorization for particular shared files, obtain that authorization before writing them. Skill installation or a general reimbursement instruction does not override that policy.
- Default isolation: process only files beginning with the current colleague's exact `姓名_` prefix.

### Verified cloud mapping

Read-only integration check on 2026-11-11 resolved the company site as `https://memova.sharepoint.com/sites/team` (公司共享盘). Its document library has the API name `Documents` and URL `/sites/team/Shared%20Documents`. The queue is at library-relative `报销工作站`, with `待提交` and `已处理` confirmed as immediate children.

Treat `公司文档库/报销工作站` above as the business-facing description of this verified company-library queue. Do not require the API display name to equal `公司文档库`, and do not prepend `公司文档库` or `Shared Documents` to a drive-relative queue path. Re-resolve the site, library, and folder IDs at runtime and stop if the hierarchy differs. Do not confuse the archive with the separate `公司知识安全副本` library.

## Finance review

- Finance owner: the organization-designated finance reviewer for the current task.
- Do not assume a permanent named individual. If the reviewer is not available from current instructions or approved local configuration, ask before submitting any no-invoice, special-evidence, or tax case.

## Local-only values

Never commit any of the following to this repository:

- Feishu access or refresh tokens;
- passwords, cookies, session data, or QR-code captures;
- full bank-account or card numbers;
- invoices, payroll files, identity documents, or live approval exports;
- colleague-specific local paths or personal queue preferences.
