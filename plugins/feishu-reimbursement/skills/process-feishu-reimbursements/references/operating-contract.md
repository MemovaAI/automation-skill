# Operating Contract

## Form selection

| Request | Feishu form |
|---|---|
| Employee expense reimbursement with invoices | 报销申请 |
| Salary, investment, deposit, supplier, or other outgoing payment | 付款申请 |

Use the corresponding form identifiers from `team-config.md`. Stop if the configured forms do not belong to the current Feishu organization.

Do not select a form until the expense/evidence gate in `reimbursement-must-read.md` has been completed. A direct company payment must not be routed through employee reimbursement merely because the employee can provide an invoice.

## Source-to-field rules

### Reimbursement

- `报销类别`: use the user's instruction or the form's closest valid choice; do not infer from amount alone.
- `报销事由` and `报销内容`: use a concise description supported by the source.
- `费用发生日期`: use the actual expense date; if a bundle spans dates, ask for the intended reporting date.
- `报销金额`: reconcile to invoice totals before form entry.
- `收款账户`: select the saved employee/company account and verify bank plus last four.
- `附件`: accept original `.pdf`, `.jpg`, `.jpeg`, `.png`, and `.heic` files case-insensitively. Upload every intended original once and preserve its filename and extension. Do not silently replace an image with a converted PDF.
- `凭证状态`: retain the internal classification `凭证初审通过`, `无票或特殊凭证待财务复核`, `不合规或疑似替票`, or `信息不足`. Do not put an unapproved no-invoice case into the live form.
- `研发归集`: record only `非研发` or `申请研发归集，待财务/审计认定`. Never state that the automation has recognized a reimbursed item as an eligible R&D or subsidy expense.

### Invoice image rules

- Read JPG/JPEG/PNG using visual inspection and OCR; verify the full invoice is visible and legible.
- For HEIC, use a temporary preview only when direct inspection is unavailable; do not modify the original.
- Reconcile invoice number, date, buyer, seller, line items, tax, and total from visible evidence.
- Treat multiple images as separate invoices unless they clearly form one multi-page invoice.
- Stop for a clearer source when an image is cropped, blurred, incomplete, or financially ambiguous.
- If Feishu rejects an original image format, ask before creating or uploading a derived file.

### Overseas expense RMB conversion

For every overseas reimbursement line item:

- Use the official RMB central parity rate published for the transaction date. Prefer the rate published by the China Foreign Exchange Trade System and exposed by the People's Bank of China or State Administration of Foreign Exchange; record the source and applicable date in the calculation or form note.
- Treat the actual transaction/payment date shown by the payment evidence as the conversion date. Do not substitute the invoice issue date, billing-period end date, statement date, or reimbursement-submission date when they differ.
- If no official rate is published for that date because it is a weekend, public holiday, or other non-publishing day, use the latest official rate available before that date. Do not use a later date's rate.
- Convert the published quote to `1 unit of foreign currency = CNY` according to its stated unit, without prematurely rounding the official rate. Calculate each transaction separately, then round each RMB result to two decimal places using ordinary half-up rounding. Sum the rounded RMB line-item amounts for the reimbursement total.
- Preserve the original foreign-currency amount, currency, transaction date, applied official rate/date, RMB result, and source so the conversion can be reproduced. If the official source does not publish a usable rate for the currency, stop and obtain a finance-approved conversion basis rather than inferring a cross-rate.

### Payment

- `付款事由`: use `姓名+月份+工资发放` for payroll; otherwise use the user's stated business reason.
- `付款金额`: use `实发工资` for payroll or the user-approved contract/payment amount.
- `付款方式`: default to `银行卡` when a saved bank account is used.
- `付款日期`: use the user-specified date; otherwise use the submission date and state that assumption in the preview.
- `收款账户`: select the saved account; never reconstruct the complex account control from bank text.
- `附件`: payroll attachment is optional only when the form/policy permits it; invoices and contracts follow the form requirement.

## Duplicate matching hierarchy

1. **Exact duplicate**: identical SHA-256 hash.
2. **Invoice duplicate**: same invoice/ticket number even when one copy is a PDF and another is an image, or their bytes/filenames differ.
3. **Probable duplicate**: same payee, amount, date, reason, and attachment count.
4. **Not proven**: amount/date similarity without stable identifiers.

Never treat a renamed file as new when its hash matches an approved or pending item.

The bundled duplicate script exits successfully by default and reports matches in its output. Add `--fail-on-duplicate` only when a nonzero exit should block an automated pipeline.

## Feishu record checks

Use read-only initiated-instance queries before creating a new request. Relevant status values:

| Status | Meaning | Duplicate action |
|---|---|---|
| `1` | Pending/in approval | Do not resubmit |
| `2` | Approved | Do not resubmit; eligible for approved archive |
| `3` | Rejected | Review the rejection before any new submission |
| `4` | Withdrawn/canceled | Verify why it was withdrawn before resubmitting |

Match at least form type, amount, date, payee/account label, and reason. Use attachment hashes when the attachment file is locally available.

## Folder contract

```text
报销工作站/
  待提交/                 # shared company queue; candidates only
  已处理/
    <员工姓名>/           # submitted and detail-verified queue copies
```

All colleagues use this shared queue; do not require personal `待提交/已处理` folders. A queue file should be named `收款人_报销事由_费用日期_金额_原文件名.ext` when practical. Never include full bank-account numbers or other sensitive identifiers in filenames.

When the source is attached directly in the current Codex task or is outside the shared queue, copy its original bytes into `待提交` before duplicate checking or live-form preparation. Keep the task attachment untouched, prefix the queue copy with the exact current colleague's name, verify source and copy SHA-256 hashes match, and use that stable queue path for the Feishu upload. The request to reimburse or submit those explicitly attached files authorizes this queue-staging copy; it does not authorize unrelated file changes.

Default shared-queue operation is strict self-service isolation:

- resolve the current colleague's name before scanning;
- list, open, submit, and move only files with the exact `姓名_` prefix;
- ignore every other colleague's files;
- use the current colleague's own Feishu login and saved account;
- upload attachments from the verified `待提交` queue-copy paths through the native file picker under Computer Use control;
- deduplicate and obtain final confirmation before submission;
- move only that colleague's successfully submitted file to `已处理/<员工姓名>/`; create the employee folder when it does not exist.

Processing another person's files requires an explicit delegated-submission instruction naming that person in the current request.

Move every queue copy used by the approval to `已处理/<员工姓名>/` only after the new approval detail has been verified, and create that employee folder when it does not exist. `已处理` means the automation submission task is closed, not that the approval is approved or paid. Do not create extra queue states unless the user requests them. Do not move company originals from their source repository. If the destination filename already exists, compare hashes and stop rather than overwriting. A submitted approval without corresponding archived queue copies is incomplete: recover the exact original from the current task source or verified approval attachment, archive it without resubmitting, and verify the resulting hashes and paths.

Use the entire `已处理` tree as the recursive duplicate-check scope, including every employee folder and `已处理/历史记录`.

## Account privacy

- Accept runtime account input as payee, bank, and last four digits.
- Read a full account number only when explicitly authorized for the current task and required by the form.
- Do not copy full account numbers into Skill files, shared indexes, filenames, chat summaries, or durable logs.

## Final pre-submit gate

Require all checks to pass:

- correct organization and form;
- expense is for company business and the paying entity is correct;
- invoice/alternative evidence has passed the expense gate, with no substitute-invoice indicators;
- seller, buyer/entity, item/service, amount, date, and payment evidence are mutually consistent;
- any no-invoice, overseas, or special-evidence path has the required finance approval;
- any R&D tag includes a named project and supporting relationship/allocation evidence and remains pending finance/audit recognition;
- no pending/approved duplicate;
- reason/category matches the request;
- amount reconciles to the source;
- date is correct or the stated assumption is accepted;
- saved account matches payee, bank, and last four;
- required original attachment is present;
- user confirms the final submission action.

## Post-submit gate

Do not report success from a click alone. Confirm the detail page and capture:

```text
instance_code, status, form_type, reason, amount, date,
masked_account_label, attachment_count
```
