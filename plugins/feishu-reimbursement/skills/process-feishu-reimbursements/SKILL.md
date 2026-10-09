---
name: process-feishu-reimbursements
description: Process company reimbursements and payment requests from invoice PDFs, invoice images, PDF bundles, payroll spreadsheets, folders, or natural-language instructions through expense-evidence validation, duplicate detection, source parsing, Feishu form preparation, saved-account selection, submission verification, and queue archiving. Use for requests mentioning 自动化报销、报销工作站、待提交、PDF发票、图片发票、JPG、JPEG、PNG、HEIC、费用报销、工资付款、付款申请、收款账户、查重、替票、无票、境外订阅、研发费用、飞书提交、审批验单或已处理归档.
---

# Process Feishu Reimbursements

Read all three references before querying Feishu, preparing a form, or moving files:

- [references/reimbursement-must-read.md](references/reimbursement-must-read.md) for expense and evidence eligibility;
- [references/operating-contract.md](references/operating-contract.md) for form, account, duplicate, submission, and queue rules;
- [references/team-config.md](references/team-config.md) for the private team's Feishu form identifiers, queue location, and finance-review role.

## Outcome

Turn a file or folder into a traceable reimbursement/payment task while preventing duplicate submissions and wrong payee accounts.

## Non-negotiable rules

- Treat finance, payroll, invoices, identities, and bank data as sensitive. Read only the authorized paths and expose the minimum necessary fields.
- Run the expense/evidence gate before duplicate checking or form preparation. A valid-looking invoice does not by itself prove that an expense is reimbursable.
- Never accept an invoice whose seller, buyer, item/service, amount, or transaction background differs from the actual business. Treat suspected substitute invoices (`替票`) as a hard stop.
- A missing invoice is not permission to invent or substitute evidence. Mark it `无票或特殊凭证待财务复核`; do not submit until the named finance owner explicitly approves the evidence path.
- Do not represent an expense as tax-deductible, VAT-creditable, R&D-eligible, or subsidy-eligible. Those are separate finance/audit determinations.
- In the shared work queue, default to self-service isolation: resolve the current colleague's name first and read only files whose names start with the exact `姓名_` prefix. Do not open, submit, or move another colleague's files.
- Never persist full card or account numbers in this Skill, indexes, logs, or summaries. Use payee name, bank, and last four digits only.
- Preserve every source file. When the user asks this Skill to process files attached in the current Codex task or located outside the shared queue, create verified byte-for-byte queue copies under `报销工作站/待提交`; keep the originals untouched. Do not otherwise rename, move, delete, or rewrite originals without explicit authorization for the exact target.
- Accept invoice sources with case-insensitive extensions `.pdf`, `.jpg`, `.jpeg`, `.png`, and `.heic`. Preserve each original file and extension throughout the workflow.
- Use Feishu CLI only for read-only definition, initiated-instance, status, and detail checks unless a production-safe write path has been separately validated.
- Select complex `收款账户` fields from Feishu's saved-account list in the desktop client. Do not synthesize an account object or submit display text as the account value.
- Confirm the organization, form type, payee, bank/last four, amount, date, and attachment before submission.
- Obtain action-time confirmation immediately before the final UI submission.
- After submission, verify the approval detail page. A selected label in the edit form is not sufficient evidence.
- Treat financial conclusions as pending human review by the finance owner configured in `references/team-config.md` or explicitly named for the current task.

## New colleague/device preflight

When a colleague first asks Codex to use this Skill for a reimbursement, treat that request as both authorization setup and the requested reimbursement task. Run the setup yourself before preparing the live form; do not merely give the colleague a checklist or ask them to configure everything separately.

1. Confirm this complete Skill folder is installed in a Codex-discoverable Skills directory, not supplied as `SKILL.md` alone.
2. Read `references/team-config.md` and confirm that its organization, form identifiers, queue location, and finance-review role match the current company environment. Stop if the configuration is incomplete or belongs to another organization.
3. Check Feishu OAuth with `lark-cli auth status --verify --json`. If approval-read access is missing, expired, or belongs to another person, explain that Codex is about to create persistent Feishu read authorization for duplicate checking and ask for confirmation immediately before starting it. Then run `lark-cli auth login --scope approval:instance:read` and open the exact authorization flow. The colleague must personally approve the Feishu login with their own company account. Never reuse another colleague's OAuth and never substitute Microsoft, Outlook, or SharePoint authorization for Feishu authorization.
4. After Feishu authorization, verify all of the following instead of trusting the login screen:

   ```text
   lark-cli auth status --verify --json
   lark-cli auth check --scope approval:instance:read --json
   lark-cli approval instances initiated --as user --page-size 1 --json
   ```

   Confirm the authenticated identity is the current colleague in the correct company organization and that the read-only initiated-approval query succeeds.
5. Confirm the official `computer-use` plugin, its Skill, and its runtime are installed and enabled. Before enabling persistent control of Feishu, Finder, or the native file picker, explain exactly which applications Codex needs to control and ask for confirmation. Open Codex **Settings > Computer Use** and enable the required app approvals; use `Any App` only when company policy permits it.
6. Open macOS **System Settings > Privacy & Security** and guide the colleague to enable **Screen Recording**, **Accessibility**, and any displayed **Automation/App Control** permission required for Codex Computer Use to control Feishu and the system file picker. These security prompts must be approved personally by the colleague; Codex must not claim to approve them. Resume the same task immediately after the colleague finishes.
7. Prove the Computer Use permissions with an actual reversible test: read the visible Feishu state, open Feishu's attachment picker, use `Command+Shift+G` to navigate to an exact local source directory, verify the expected file is visible, and cancel without uploading. This dry run must prove control of both Feishu and the native file picker. Installation status alone is not sufficient.
8. Open the configured Feishu organization and forms, then verify the requested payee has a saved account selectable from `收款账户`.
9. Locate the configured shared queue's `待提交` and `已处理` folders and verify they are readable and writable. Do not require personal queue folders.
10. Resolve the current colleague's default reimbursement name from a user-authored instruction or user-local Codex preference. If it is not configured, ask once before listing or opening queue files.

Do not start the live form until every applicable authorization and reversible test has passed. If any check fails, identify the exact missing authorization and give the single next action needed, then resume validation; do not fall back to asking the colleague to select or upload routine attachments manually.

First use may therefore require separate confirmations for Feishu OAuth and persistent Computer Use permissions, plus the colleague's own clicks on macOS security prompts. After this bootstrap has been observed to pass, later routine reimbursements require only the final action-time confirmation before submission unless OAuth expires, an app approval is revoked, macOS permissions change, or the environment otherwise fails validation.

## Workflow

### 1. Classify the request

Choose one mode:

- **Check only**: compare files and report whether they are duplicates or already submitted.
- **Prepare**: parse sources and fill a draft, stopping before final submission.
- **Submit**: prepare, confirm, submit, and verify a specific request.
- **Reconcile**: match files to Feishu records and archive only verified approved items.

Do not broaden a check-only request into a submission or file move.

### 2. Validate the expense and evidence

Identify and reconcile only the minimum needed facts:

```text
business_entity, applicant_or_payee, actual_seller,
actual_item_or_service, business_purpose, amount, date,
payment_evidence, invoice_or_alternative_evidence
```

Check that the expense is for company business and that the selected form is correct:

- Use **报销申请** only when an employee has already advanced a company expense and reimbursement is payable to that employee.
- Use **付款申请** for salary, supplier, consultant, deposit, investment, or other direct company payment.
- Do not convert a direct company payment into an employee reimbursement merely to simplify the workflow.

Reconcile the invoice or alternative evidence with the real transaction. Stop when the buyer/entity, seller, item/service, amount, or business purpose is inconsistent; when the expense appears personal; or when an invoice appears altered, cropped, or substituted.

Classify the evidence before continuing:

- `凭证初审通过`: the transaction and evidence are facially consistent; continue.
- `无票或特殊凭证待财务复核`: organize the minimum evidence and stop before submission unless finance explicitly approves the path.
- `不合规或疑似替票`: stop and describe the exact inconsistency; do not offer a replacement-invoice workaround.
- `信息不足`: request only the missing material needed to decide.

Apply special routes:

- **Natural-person small occasional service**: collect a receipt with company name, recipient name and ID number, actual item/service, amount, date, signature, plus payment evidence. Check the current tax threshold rather than assuming a durable amount. Always route to finance review.
- **Overseas software/API/cloud/subscription**: require the original invoice/receipt or statement, order/plan and service period, payment evidence, business use, and RMB conversion basis. Add contract, approval, or usage evidence when material or recurring. Route tax-withholding and deductibility questions to finance.
- **R&D-related expense**: record the project name, direct relationship, and allocation basis when shared. Label only `申请研发归集，待财务/审计认定`; never promise R&D or subsidy eligibility.

### 3. Establish the task record

Collect only:

```text
form_type, business_entity, payee, reason, category, amount,
expense_or_payment_date, payment_method, source_paths,
expected_account_label, attachment_paths, evidence_status,
rd_project_tag
```

For payroll, use the value under the exact `实发工资` header. Do not substitute `应发合计`.

Stop and ask when payee, amount, reason, or form type cannot be determined safely.

For the shared work queue, use filenames in this order when practical:

```text
收款人_报销事由_费用日期_金额_原文件名.ext
```

Do not place bank-account numbers or other sensitive identifiers in filenames. Treat filenames as routing hints only; source documents and the Feishu form remain authoritative.

In self-service mode, list and process only files matching the exact current-colleague prefix, for example `王维杰_`. Use the current colleague's own Feishu login and saved account. A delegated submission for another person is allowed only when the user explicitly names that person in the current request; never infer delegation from seeing another name in the shared queue.

### Stage direct attachments in the shared queue

Before duplicate checking or form preparation, stage every source that is not already under `报销工作站/待提交`:

1. Copy the original bytes into `待提交`; never move or alter the original task attachment.
2. Name the queue copy with the exact current-colleague prefix and, when practical, the pattern `收款人_报销事由_费用日期_金额_原文件名.ext`.
3. If the destination name exists, compare SHA-256 hashes. Reuse an identical copy; stop for review when the bytes differ.
4. Verify the source and queue-copy hashes match and re-list the destination. Set `source_paths` and `attachment_paths` to the stable queue-copy paths used by the live form.

A request to reimburse or submit the explicitly attached files authorizes this queue-staging copy as part of the requested workflow. Do not ask for a second confirmation merely to create the copy. Missing queue copies after direct task upload are a failed preparation check, not an optional archival condition.

### Source parsing by format

- **PDF**: extract text and render pages when needed; reconcile the visible invoice totals, dates, numbers, buyer, seller, and line items.
- **JPG/JPEG/PNG**: inspect the original image and use OCR/visual reading. Verify that the whole invoice is visible, legible, and not cropped before trusting extracted fields.
- **HEIC**: inspect directly when supported. Otherwise create a temporary preview only for reading, keep the HEIC untouched, and upload the original when Feishu accepts it.
- **Multiple images**: treat each image as a separate source unless their filenames and visible contents clearly show that they are pages of one invoice. Reconcile every included amount and attachment count.

If an image is blurred, incomplete, or has ambiguous amount/date/invoice-number text, stop and ask for a clearer original. Never infer missing financial fields. Do not convert an image into a replacement PDF merely for upload; if Feishu rejects the original image format, report it and ask before creating a derived attachment.

### 4. Deduplicate before form entry

Run the bundled script against the candidate files and relevant source/archive directories:

```bash
python3 scripts/find_exact_duplicates.py <candidate-path> --against <directory> [--against <directory>]
```

Use `报销工作站/已处理` as a recursive comparison root. Include every descendant, including `已处理/历史记录`, so archived evidence cannot be reimbursed again.

Then query Feishu's initiated reimbursement/payment records and match form type, amount, date, payee, reason, and attachment count.

Apply this decision:

- Exact hash match plus an approved or pending Feishu record: stop; report the record and do not resubmit.
- Same amount/date but different hash: inspect invoice numbers/content before deciding.
- No reliable match: continue and mark the result `未发现重复` rather than `绝对无重复`.

### 5. Present a concise preview

Before touching the live form, show or internally verify:

```text
申请类型：
费用承担主体：
收款人：
事由/类别：
金额：
日期：
收款账户：银行 + 尾号
附件：
凭证状态：
研发归集：非研发 / 申请研发归集，待财务或审计认定
查重结果：
```

### 6. Prepare the Feishu form

Use the logged-in Feishu desktop client in the correct company organization.

1. Open `审批` and the correct form.
2. Fill ordinary fields once.
3. Choose the saved account from the account dropdown.
4. If the payee is outside the visible list, scroll the account list and re-read the page state.
5. Upload every intended original PDF or image exactly once from its verified `待提交` queue-copy path, preserving its filename and extension.
6. Drive the native file picker with Computer Use. Use `Command+Shift+G`, enter the exact queue-copy path, verify the selected filename, and choose it without handing routine selection to the colleague.
7. After choosing an attachment, wait for the attachment card to show the expected filename and a stable completed state, then re-read the page before taking any other action.
8. Never retry an upload only because the attachment card is delayed. If two identical cards appear, stop and remove the extra copy only after explicit confirmation.
9. If the native picker cannot be controlled, stop and report the failed permission or app approval. Do not continue through manual colleague selection as though the automated upload passed.
10. Do not continue if text input duplicates characters, the organization is wrong, or the account cannot be verified.

Write business-facing fields such as `报销事由` and `报销内容` in Chinese when the Feishu form is Chinese. Do not replace them with English as an input workaround; use a reliable value-setting method and re-read the saved Chinese text.

### 7. Confirm and submit

Re-read the complete form and compare it with the task record. When the user's request explicitly identifies the files and asks to reimburse or submit them in Feishu, queue staging and attachment upload need no additional confirmation. Ask for the colleague's only routine confirmation when the next action is the final `提交` click.

After confirmation, submit once. Do not click repeatedly while the UI is loading.

### 8. Verify the result

Open the created approval and verify:

- status is submitted/pending or approved;
- reason, amount, date, and payee match;
- the full `收款账户` block exists and shows the expected bank and last four;
- every intended original PDF/image attachment is present, recognizable, and has the expected filename/extension;
- an approval instance code is available.

If any value is wrong, stop subsequent tasks and report the exact mismatch. Withdraw only with explicit authorization.

### 9. Close the shared queue item

After submission, first verify the created approval detail as required in step 8. Then move every current-colleague queue copy used by that approval from `待提交` to that colleague's folder under `已处理`. Create the colleague folder when it does not exist:

```text
报销工作站/待提交/<filename>
-> 报销工作站/已处理/<员工姓名>/<filename>
```

This closes the queue item even while the approval is pending; it does not mean the reimbursement has been approved or paid. Never move unrelated company originals. Never overwrite an existing destination file: compare hashes and stop for review if the destination name already exists. After moving, verify the destination listing, the archived hashes, and that the source queue no longer contains any copy used by the approval.

Every submitted attachment must have a corresponding archived queue copy. If a verified approval unexpectedly has no queue copy, mark closure incomplete, do not resubmit, recover the exact original from the current task source or the verified approval attachment, verify its identity, and place it in `已处理/<员工姓名>/` before reporting the workflow complete.

## Stop conditions

Stop without submission when any of these occurs:

- wrong Feishu organization;
- stale or unrelated draft;
- duplicate/repeated input characters;
- ambiguous payee or multiple unverified accounts;
- missing attachment or amount mismatch;
- personal or non-business expense;
- invoice buyer/entity, seller, item/service, or amount does not match the actual transaction;
- suspected substitute invoice, altered evidence, or invented expense category;
- no-invoice or special-evidence route has not been approved by finance;
- claimed R&D expense lacks a named project, direct relationship, or reasonable allocation evidence;
- concurrent user interaction changes the UI;
- account is visible in the form but absent from the submitted detail;
- exact duplicate already pending or approved.

## Completion report

Report only the useful audit trail:

- action taken;
- amount and masked account label;
- approval instance code and status, if submitted;
- duplicate evidence, if found;
- evidence status and any finance/audit review still required;
- final queue-file location, if moved;
- any remaining human review.
