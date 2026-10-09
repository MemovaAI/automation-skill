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

- Queue root: `报销工作站`
- Pending: `报销工作站/待提交`
- Processed: `报销工作站/已处理/<员工姓名>`
- Default isolation: process only files beginning with the current colleague's exact `姓名_` prefix.

## Finance review

- Finance owner: the organization-designated finance reviewer for the current task.
- Do not assume a permanent named individual. If the reviewer is not available from current instructions or approved local configuration, ask before submitting any no-invoice, special-evidence, tax, or R&D-classification case.

## Local-only values

Never commit any of the following to this repository:

- Feishu access or refresh tokens;
- passwords, cookies, session data, or QR-code captures;
- full bank-account or card numbers;
- invoices, payroll files, identity documents, or live approval exports;
- colleague-specific local paths or personal queue preferences.
