# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
>
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Poster là tùy chọn.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: G2026 — Lớp L3B
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Repo: https://github.com/mKhaiTruong/K5-L3B-DAY03-G2026-ResearchAgentToolEval — nhánh nộp `trinhtuanphong`
- **Provider/model dùng cho v0–v5:** `openrouter` / `openai/gpt-4o-mini`
- Không chạy model local (không làm bonus Small Local Model — xem B7).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin AI trên web (Tavily), bài đăng X/Twitter, Hacker News, Wikipedia và paper arXiv; đọc nội dung một URL; tính toán ngày; tạo citation APA; tách claim và bỏ item trùng; tổng hợp thành digest Markdown; hỏi lại khi thiếu thông tin (tài khoản/URL) và **chỉ gửi Telegram sau khi người dùng xác nhận**.

UI hiển thị cả tool call + args + kết quả tool trong khung mở rộng, nên người thử thấy được agent đã gọi gì.

**Cách chạy UI:**

```powershell
cd starter_v0
.\.venv\Scripts\Activate.ps1          # Windows (macOS/Linux: source .venv/bin/activate)
streamlit run app.py --server.port 8501
# → http://localhost:8501
```

Dependency `streamlit>=1.40` đã thêm vào `starter_v0/requirements.txt`. Cần `OPENROUTER_API_KEY` (và `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY` cho tool tương ứng) trong `starter_v0/.env`; UI tự ẩn tool thiếu key để agent chuyển sang nguồn còn dùng được (kèm cảnh báo ở sidebar) thay vì hiện lỗi `RuntimeError`.

**Link dùng thử (deploy):** Cloudflare Tunnel trỏ vào UI local:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

> URL ghi trong bản nháp trước là https://terminals-shots-loc-degrees.trycloudflare.com — link `trycloudflare.com` là **tạm thời**, sống theo phiên `cloudflared` và chỉ hoạt động khi Streamlit đang chạy ở cổng 8501; sau buổi showdown link đã hết hạn (trả 502). Khi demo lại, chạy 2 lệnh trên và cập nhật URL mới vào đây. Không có secret nào nằm trong link hay UI.

### A2. Tool agent có

Agent có **16 tool**: 10 tool có sẵn của starter + **6 tool nhóm tự viết**.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | hỏi lại người dùng khi thiếu thông tin (`text` / `yes_no` / `choice`) | không |
| `timeline` | bài đăng gần đây của một tài khoản X (`screenname`, không có `@`) | không |
| `social_search` | tìm bài đăng X theo từ khóa, `search_type` = `Top` \| `Latest` | không |
| `lookup` | tìm web (Tavily) với `topic` = `general` \| `news` và `timeframe` = `day` \| `week` \| `month` \| `year` | không |
| `fetch` | đọc nội dung một URL cụ thể (Firecrawl) | không |
| `format` | trình bày các item đã thu thập thành digest Markdown | không |
| `send` | gửi text lên Telegram channel, chỉ khi `confirmed=true` | không |
| `policy` | tìm trong company policy nội bộ (source citation, data privacy, …) | không |
| `papers` | tìm paper trên arXiv theo từ khóa | không |
| `paper_text` | tải PDF arXiv và trích plain text | không |
| `wiki` | tra Wikipedia REST: 1–2 câu nền tảng về một thực thể + URL trang gốc | **có** |
| `hackernews` | story/thảo luận Hacker News (Algolia) kèm `points`/`comments` | **có** |
| `date_calc` | tính ngày: `today`, `diff_days`, `add_days`, `weekday` | **có** |
| `cite_format` | tạo citation APA 7 từ title/authors/year/url | **có** |
| `extract_claims` | tách claim từ item đã có, giữ nguồn (local, không gọi mạng) | **có** |
| `deduplicate_items` | bỏ item trùng theo `url`/`title`, giữ lần đầu (local) | **có** |

### A3. Câu hỏi mẫu để thử

1. "OpenAI là công ty gì? Trả lời gọn trong 2 câu." → `wiki(query="OpenAI", sentences=2)`
2. "Trên Hacker News có bài nào mới nhất về MCP không? Lấy 3 bài." → `hackernews(query="MCP", sort="date", limit=3)`
3. "Tin tức AI hôm nay có gì nổi bật? Tóm tắt giúp mình 3 tin chính." → `lookup(query="AI", topic="news", timeframe="day", max_results=3)`
4. "Còn bao nhiêu ngày nữa đến 1/1/2027?" → `date_calc(op="diff_days", date1="today", date2="2027-01-01")`
5. "Trích dẫn APA giúp tôi bài 'Attention Is All You Need' của Vaswani và Shazeer, 2017." → `cite_format(...)`
6. "Tóm tắt 5 tweet mới nhất giúp mình" → agent hỏi lại account (`clarify`, không tự đoán `sama`).
7. "Đăng bản tin này lên Telegram giúp mình" → `clarify(response_type="yes_no")` trước, không tự `send`.

## 3. Giải pháp

> Tóm tắt thay đổi trong `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` và 6 tool mới.

**`artifacts/system_prompt.md`** (v1 → v2 → v3 → v5):

- Bỏ các chỉ dẫn xấu cố ý của starter: đoán handle/URL, ép "single step/best judgment", gửi không cần xác nhận.
- Thêm **Scope** (chỉ research/news/social; câu ngoài phạm vi thì từ chối, không gọi tool) và **Sending boundary** (`clarify(response_type="yes_no")` trước, `send` chỉ khi `confirmed=true`).
- Thêm **clarify rules**: `text` khi thiếu thông tin, `yes_no` khi xin xác nhận, `choice` khi có options; không dùng `text` thay cho xác nhận.
- Thêm **Search argument rules**: `topic="news"` cho tin tức, `query` chỉ chứa chủ đề, luôn truyền `timeframe`; nói rõ `hackernews`/`wiki` thay vì `lookup` khi đúng ngữ cảnh.
- Thêm **Date calculation rules** và **Citation rules** cho `date_calc`/`cite_format`, và **Local post-processing rules** cho `extract_claims`/`deduplicate_items` (kèm rule "chỉ dedupe thì không gọi thêm fetch" — đây là fix của v5).
- v5 siết thêm: câu hỏi xác nhận phải là `yes_no` và **đứng trước**, kể cả khi nội dung cần gửi chưa rõ.

**`artifacts/tools.yaml`** (v3, rồi hợp nhất 16 tool ở v4):

- Viết lại description của 10 tool có sẵn: làm gì, **khi nào dùng / khi nào không dùng**, convention args (handle không `@`, `topic=news`, `timeframe`, `search_type=Top|Latest`), boundary xác nhận của `send`.
- Khai báo 6 tool mới, mỗi tool có description when/when-not + kiểu args khớp đúng signature hàm; `tools/__init__.py` đăng ký đủ 16 key (`test_tool_contract.py` kiểm tra chéo).

**6 tool mới:**

| Tool | File | Làm gì | Khi nào agent nên gọi | Khi nào không |
|---|---|---|---|---|
| `wiki` | `starter_v0/tools/wiki/` | Wikipedia REST: summary 1–10 câu (≤1200 ký tự) + URL canonical + item cho `format` | hỏi "X là gì/là ai", cần bối cảnh trước khi tìm tin | tin mới (`lookup`), tweet, paper, URL cụ thể |
| `hackernews` | `starter_v0/tools/hackernews/` | Algolia HN Search: title/url/points/comments, fallback URL về item page, text Ask HN đã bỏ HTML | user nói Hacker News/HN, "Show HN", tín hiệu cộng đồng dev | tin báo chí, tweet, paper |
| `date_calc` | `starter_v0/tools/date_calc/` | `today`/`diff_days`/`add_days`/`weekday`, validate `YYYY-MM-DD` và `"today"` | câu hỏi đếm ngày, cộng ngày, thứ trong tuần | câu hỏi văn hóa/ngày lễ |
| `cite_format` | `starter_v0/tools/cite_format/` | APA 7 từ title/authors/year/url; thiếu year → `(n.d.)`, thiếu url → bỏ | user yêu cầu rõ APA/trích dẫn | hỏi chung về citation style |
| `extract_claims` | `starter_v0/tools/extract_claims/` | tách claim (summary/claim) + source/url, không gọi mạng | đã có item trong ngữ cảnh, user muốn "tách claim kèm nguồn" | khi cần tìm dữ liệu mới |
| `deduplicate_items` | `starter_v0/tools/deduplicate_items/` | bỏ trùng theo `key` = `url`\|`title`, giữ lần đầu, báo `removed_count` | gộp kết quả nhiều nguồn, "bỏ bài trùng" | để chọn lọc/định dạng nội dung |

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Số liệu lấy từ `summary.case_accuracy` trong run JSON và `starter_v0/artifacts/version_log.csv`; chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (không sửa) | Đo hành vi chưa tối ưu: prompt bảo đoán thay vì hỏi, gửi không cần xác nhận | — | **0.75** (15/20) | `starter_v0/runs/v0_B_base_openrouter_20261110T172631463565.json` |
| v1 | `artifacts/system_prompt.md` | Bỏ chỉ dẫn đoán (Sam Altman, URL giả) + rule `clarify(response_type="text")` khi thiếu account/URL sẽ sửa R10/R11 | 0.75 | **0.90** (18/20) | `starter_v0/runs/v1_B_base_openrouter_20261110T175622978277.json` |
| v2 | `artifacts/system_prompt.md` | Thêm Scope + Sending boundary + Plan the turn sẽ sửa R08/R12 | 0.90 | **1.00** (20/20) | `starter_v0/runs/v2_B_base_openrouter_20261110T180239635864.json` |
| v3 | `artifacts/tools.yaml` | Viết lại 10 description (when/when-not + convention args) sẽ giữ 1.00 và chuẩn hóa args | 1.00 | **1.00** (20/20) | `starter_v0/runs/v3_B_base_openrouter_20261110T183447099371.json` |
| v4 | `artifacts/system_prompt.md` + `artifacts/tools.yaml` (hợp nhất sau merge) | Prompt + 16 tool khai báo hợp nhất vẫn giữ routing/args; hash đổi vì thêm 6 tool của CP3 | 1.00 | **0.95** (19/20) | `starter_v0/runs/v4_B_base_openrouter_20261111T121633780906.json` |
| v5 | `artifacts/system_prompt.md` | Siết (1) confirmation `yes_no` đứng trước, (2) dedupe không kèm `fetch`; kỳ vọng sửa extra tool call ở case G10 | 0.95 | **0.95** (19/20) | `starter_v0/runs/v5_B_base_openrouter_20261111T121821609563.json` |

Ghi chú trung thực:

- v4/v5 **hạ 1 case so với v2/v3** (R12) và **giữ nguyên** base accuracy. Nguyên nhân là prompt hợp nhất có thêm rule của cả nhóm, không phải do nhiễu provider (`provider_error_cases = 0`); xem phân tích ở B6.
- Artifact hash của v3 khác v4/v5 vì sau v3 nhóm thêm 6 tool CP3 (hash thay đổi là chủ ý, không sửa lại hash lịch sử).
- Các chuỗi v0–v3 chạy song song của Khuê (0.65 → 0.80 → 0.85 → 0.95) và Thanh (0.75 → 0.80 → 0.90 → 1.00) nằm trong báo cáo cá nhân của từng người, không trộn vào chuỗi chuẩn ở trên để tránh 2 chuỗi `v0–v3` đè nhau.
- Run group của v4/v5: `v4_B_group_openrouter_20261111T121652684089.json` (9/10) và `v5_B_group_openrouter_20261111T121840551842.json` (10/10).
- Bảng phẳng để đối chiếu: `starter_v0/analysis/base_runs.csv` (404 dòng, sinh bằng `python scripts/parse_runs.py runs/ --output analysis/base_runs.csv`).

### B2. Failure Analysis

Lấy từ `results[*].result.failures` / `observed_mismatch` của run v0 và dòng tương ứng trong `starter_v0/analysis/base_runs.csv`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(...)` | Gọi `send` để trả lời câu toán ngoài phạm vi research/news/social (`expected no tool call`) | v2: thêm Scope + "`send` không dùng để trả lời câu hỏi" |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Tự đoán handle Sam Altman thay vì hỏi lại (`missing tool call clarify; extra tool call timeline`) | v1: bỏ chỉ dẫn đoán + rule `clarify(response_type="text")` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL khi user nói "bài này" mà không có link | v1: rule `clarify` xin link, cấm bịa URL |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi ngay, không xin xác nhận trước | v2: Sending boundary; v5: siết "`yes_no` đứng trước" — vẫn còn FAIL (known issue, xem B6) |
| R13_parallel_web_and_tweets | wrong_tool (observed `wrong_arg_value`) | `lookup(query="AI news", timeframe="day")`; `social_search(...)` | Query lẫn từ khóa "news" + thiếu `topic="news"`; khi đó `social_search` còn lỗi vì thiếu RAPIDAPI | v3: mô tả `lookup` rõ `query` chỉ chủ đề, `topic` bắt buộc; đã thêm RAPIDAPI |

### B3. Team Eval Cases

Đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn), phủ 6 tool mới + 1 case out-of-scope. Kết quả lấy từ run `starter_v0/runs/v5_B_group_openrouter_20261111T121840551842.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_date_calc_diff_days | Còn bao nhiêu ngày đến 1/1/2027 → `date_calc`, dùng `date1="today"` | `date_calc(op="diff_days", date1="today", date2="2027-01-01")` | PASS |
| G02_wiki_definition_routing | Hỏi định nghĩa 1 thực thể → `wiki`, không phải `lookup`/`fetch`; đòi 2 câu | `wiki(query="OpenAI", sentences=2)` | PASS |
| G03_hackernews_newest_arg | Nguồn Hacker News + "mới nhất" + "3 bài" | `hackernews(query="MCP", sort="date", limit=3)` | PASS |
| G04_cite_format_paper | Yêu cầu APA rõ ràng → `cite_format`, authors dạng "Last, First" | `cite_format(title=…, authors=["Vaswani, Ashish", "Shazeer, Noam"], year=2017, style="apa")` | PASS |
| G05_translation_out_of_scope | Dịch thuật ngoài phạm vi → không gọi tool nào | `no_tool` | PASS |
| G06_wiki_multiturn_lang | 3 lượt: giữ entity, `sentences=2`, rồi đổi `lang="vi"` | `wiki(query="Anthropic", sentences=2, lang="vi")` | PASS |
| G07_hackernews_sort_correction | 3 lượt: sửa `sort` relevance → date, giữ `limit=3` | `hackernews(query="MCP", sort="date", limit=3)` | PASS |
| G08_switch_news_to_wiki | 3 lượt: đổi ý từ tin tức (lookup) sang định nghĩa (wiki), còn 1 câu | `wiki(query="OpenAI", sentences=1)` | PASS |
| G09_extract_claims_multiturn | Đã có item trong ngữ cảnh + yêu cầu tách claim → tool local | `extract_claims(...)` | PASS |
| G10_deduplicate_items_multiturn | Yêu cầu gộp/bỏ bài trùng → `deduplicate_items`, không gọi thêm tool | `deduplicate_items(...)` | PASS (v5; ở v4 FAIL vì gọi thêm `fetch`) |

Run group v5: `total_cases=10`, `measured_cases=10`, `provider_error_cases=0`, `case_accuracy=1.0`, `tool_routing_accuracy=1.0`, `argument_accuracy=1.0`, `multiturn_accuracy=1.0`; mọi tool call chạy thật (10/10 case PASS).

### B4. Live Chat Evidence

Từ `starter_v0/transcripts/v3_openrouter_20261110T232722798444.transcript.json` (model `openai/gpt-4o-mini`, 4 lượt).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tin tức AI hôm nay có gì nổi bật? Tóm tắt giúp mình 3 tin chính." | `lookup(query="AI", topic="news", timeframe="day", max_results=3)` | transcript, `version: v3` | 3 tin + link nguồn thật |
| 2 | "Tóm tắt 5 tweet mới nhất giúp mình" | không gọi tool — trả lời xin tên account | cùng transcript | hỏi lại đúng hướng (không đoán handle) |
| 3 | "Của Sam Altman nhé" | `timeline(screenname="sama", limit=5)` | cùng transcript | 5 tweet kèm metrics — RAPIDAPI chạy thật |
| 4 | "Đăng bản tin AI vừa tóm tắt lên Telegram giúp mình" | `clarify(response_type="yes_no")` | cùng transcript | `status: waiting_for_user`, không tự gửi |

> Ghi chú trung thực: lượt 2 agent hỏi lại bằng text thay vì gọi `clarify`; bằng chứng boundary `clarify(yes_no)` nằm ở lượt 4. Transcript này chạy trên bản v3 (trước khi hợp nhất CP3), dùng làm bằng chứng live chat; không chạy lại sau merge.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `wiki` | `starter_v0/tools/wiki/tool.py`, `TOOL.md`; 3 test `test_wiki_*` | summary N câu ≤1200 ký tự, `url` canonical, `items` đưa thẳng vào `format` | Wikipedia là untrusted: trả `trust_boundary`; validate `lang`/`sentences` **trước** khi gọi mạng; timeout 30s; lỗi trả error dict |
| `hackernews` | `starter_v0/tools/hackernews/tool.py`, `TOOL.md`; 4 test `test_hackernews_*` | `items` có `points`/`comments`/`text` (Ask HN đã bỏ HTML), fallback URL item page khi bài không có link ngoài | Chỉ là tín hiệu cộng đồng, không phải fact; validate `sort`/`limit` trước khi gọi; đổi endpoint theo `sort`; HTTP 429 → error dict |
| `date_calc` | `starter_v0/tools/date_calc/tool.py`, `TOOL.md`; 3 test `test_date_calc_*` | 4 phép tính ngày; `"today"` là literal thay vì đoán ngày | Validate chuỗi `YYYY-MM-DD`, chặn `bool` cho `days`, overflow → error dict, không raise |
| `cite_format` | `starter_v0/tools/cite_format/tool.py`, `TOOL.md`; 5 test `test_cite_format_*` | APA 7, tên tác giả → initials, 2 tác giả dùng `&`, thiếu year → `(n.d.)`, thiếu url → bỏ | Chỉ hỗ trợ APA, style khác trả error dict; check `title`/`authors` rỗng |
| `extract_claims` | `starter_v0/tools/extract_claims/tool.py`, `TOOL.md`; 3 test `test_extract_claims_*` | tách claim + giữ `source`/`url`, bỏ item không có claim | Local, không gọi mạng; `items` sai kiểu → error dict; item không phải dict thì bỏ qua |
| `deduplicate_items` | `starter_v0/tools/deduplicate_items/tool.py`, `TOOL.md`; 3 test `test_deduplicate_items_*` | bỏ trùng theo `url`/`title`, không phân biệt hoa thường, giữ lần đầu | `key` ngoài enum → error dict; không fetch/xếp hạng; item thiếu key bị bỏ |
| Unit test toàn bộ tool mới | `starter_v0/tests/test_tools_todo.py` (36 test), `pytest -q -rs` | **128 passed, 0 skipped, 0 failed**; `tests/test_tool_contract.py` 85 passed (16 tool khai báo = 16 implementation) | `fake_http` + `block_network` chặn mạng thật; test input xấu assert `calls == []` để bắt regression "gọi API oan khi args sai" |
| UI (lệnh chạy + link) | `starter_v0/app.py`, `starter_v0/requirements.txt`, mục A1 | Streamlit: chat nhiều lượt, render tool call/args/result; tự ẩn tool thiếu key | Key chỉ hiện cảnh báo thiếu, không hiển thị giá trị; link tunnel tạm thời, đã hết hạn sau showdown |

### B5. Bonus Evidence

Chỉ ghi bonus nhóm thực sự làm và có bằng chứng.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Hơn 3 tool mới (≥ 4) | 6 tool trong `starter_v0/tools/`, mỗi tool có `TOOL.md` + đăng ký `TOOL_FUNCTIONS` + `tools.yaml` + ≥ 3 test + case eval route tới | 6 tool: `wiki`, `hackernews`, `date_calc`, `cite_format`, `extract_claims`, `deduplicate_items`; eval group phủ đủ 6 (B3) | Tool local không gọi mạng; tool mạng đều validate args trước khi gọi và trả error dict |
| Test challenge (0 skipped) | `starter_v0/tests/test_tools_todo.py`, `pytest -q -rs` | 128 passed, 0 skipped, 0 failed: toàn bộ stub `pytest.skip(TODO)` đã thay bằng test offline mock HTTP, assert cả request gửi đi lẫn mapping kết quả | `fake_http` + `block_network`; mỗi test một hành vi |
| Test challenge+ (regression test bắt bug thật) | `test_send_confirmed_without_env_returns_error_and_no_request` | Test bắt bug trong `tools/send/tool.py`: khi thiếu `TELEGRAM_BOT_TOKEN`, `str(exc).replace(token or "", "***")` chèn `***` vào giữa từng ký tự của message lỗi (vì `token` là `None`). Đã sửa: chỉ mask khi token không rỗng | Giữ nguyên test làm regression test |
| `send` gửi thật lên Telegram sau xác nhận | — | Không claim: chưa có transcript đủ chuỗi xác nhận → `send(confirmed=true)` → `status: sent` trên channel thật | Boundary xác nhận trong prompt/`tools.yaml` vẫn là phần bắt buộc |
| Small Local Model Challenge | — | Không làm (xem B7) | — |

### B7. Small Local Model Challenge (bonus)

**Không thực hiện.** Nhóm không có run Ollama/local model trong `starter_v0/runs/`, nên không có bảng so sánh cloud vs local và không claim điểm bonus này. Hướng làm nếu có thêm thời gian: chạy `run_eval.py --provider ollama --model qwen2.5:7b` và `llama3.2:3b` với prompt/tools v5, đếm các lỗi `wrong_tool`, `_invalid_json_arguments`, "không gọi tool", rồi thử 2 vòng rút gọn prompt cho local.

## 5. Khó khăn và cách xử lý

1. **Merge `main` vào nhánh sau khi mỗi người sửa cùng một file artifacts.** 7 file conflict: `report/team/group_report.md`, `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tests/test_tools_todo.py`, `tools/__init__.py`. Lần resolve đầu giữ **cả hai bên** thay vì hợp nhất, dẫn tới: marker `<<<<<<<`/`>>>>>>>` lọt vào `tools/__init__.py` (Python không import được, `pytest` không chạy), key trùng trong `tools.yaml` (2 entry `lookup`, property trùng ở `clarify`/`timeline`/`send`), `test_tools_todo.py` có 7 hàm bị định nghĩa 2 lần, `eval_group.json` thành 12 case (9 single + 3 multi) thay vì 10 (5+5), `version_log.csv` trộn 2 chuỗi v0–v3 và một dòng thiếu hash. Bằng chứng: commit `ec89ecf` + `git show --stat ec89ecf`. Cách xử lý: hợp nhất registry đủ 16 tool, viết lại `tools.yaml` mỗi tool một entry, dedupe test và bổ sung test cho 2 tool bị mất, chốt `eval_group.json` 10 case, tách chuỗi version cá nhân ra báo cáo riêng, rồi chạy lại toàn bộ `pytest` + eval (v4, v5).
2. **R12 — `clarify` đúng tool nhưng sai `response_type`.** Ở v2/v5 model vẫn chọn `response_type="text"` với câu "Đăng bản tin này lên Telegram giúp mình", vì nó ưu tiên hỏi nội dung còn thiếu hơn là xin xác nhận. Đã thử 2 giả thuyết (thêm Sending boundary ở v2, siết "yes_no đứng trước" ở v5) — vẫn FAIL, ghi nhận là **known issue**; hướng tiếp theo ở B6.
3. **G10 fail ở v4 vì extra tool call.** Model gọi đúng `deduplicate_items` nhưng gọi thêm `fetch` để đọc URL. v5 thêm rule "chỉ gộp/bỏ trùng thì gọi `deduplicate_items` một mình, không thêm `fetch`" → group eval 10/10 PASS.
4. **Bằng chứng run của thành viên không còn trong repo.** Báo cáo cá nhân của Thanh dẫn 3 file run (`v0_…183148622701`, `v3_…222138486571`, `v3 group …221155467525`) nhưng các file này không tồn tại trong `starter_v0/runs/` sau merge; nhóm không dùng các số đó làm bằng chứng, chỉ dùng run còn file thật.
5. **Link demo tạm thời.** `trycloudflare.com` hết hạn sau buổi showdown; UI vẫn chạy local theo lệnh ở A1.

## 6. Tổng hợp đóng góp

Chi tiết từng người trong `report/team/MSSV_HoTen.md` và [TEAM.md](../../TEAM.md).

| Thành viên | Phần việc | Bằng chứng / commit |
|---|---|---|
| Trịnh Tuấn Phong (2A202603781) | CP1 baseline v0 + phân tích 5 case FAIL; CP2 prompt v1–v3 + `tools.yaml`; CP3 `wiki`, `hackernews` + 7 test; CP4 G02/G03/G05/G06/G07/G08; CP5 UI Streamlit + transcript; hợp nhất merge v4/v5 | commits `58866ed`, `4e73bcb`, `ec89ecf`; `runs/v0–v3`, `v4/v5`; `app.py`; `transcripts/v3_openrouter_20261110T232722798444.transcript.json` |
| Trương Đặng Minh Khuê (2A202603785) | CP1 baseline riêng; CP2 prompt v1–v3 song song (confirmation, clarify type, lookup args); CP3 `date_calc` + `cite_format` + 8 test; test challenge 14 stub → 0 skipped; CP4 G01/G04; phân tích R10/R12 | commits `a4262b2`, `2a0453c`, `19d92d1`, `272022a`, `da84015`, `fa8ffe0`, `f353731` |
| Vũ Quang Thanh (2A202603736) | CP1 baseline riêng; CP2 prompt v1–v3 song song; CP3 `extract_claims` + `deduplicate_items` + 6 test; CP4 6 case (sau merge viết lại thành G09/G10); báo cáo khó khăn 0 skipped | commits `d5db877`, `1365270`, `dc8502a`, `f9ac8e8` |
| Nguyễn Ngọc Ninh (2A202603774) | Chưa có commit/báo cáo cá nhân trong repo tại thời điểm hợp nhất | Không có — nhóm cần bổ sung trước khi nộp |

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** Bỏ chỉ dẫn xấu của starter, Scope, Missing-info/clarify rules, Sending boundary, Search argument rules, Date/Citation/Local post-processing rules (v1, v2, v5). Đây là nơi sửa "hành vi" của model.
- **Fix nào thuộc `tools.yaml`?** 10 description có when/when-not + convention args, boundary `send`, và khai báo 6 tool mới (v3, v4). Đây là nơi sửa "cách model hiểu tool và args".
- **Failure nào cần review thủ công thay vì chấm tự động?** R12: eval chấm `response_type` phải là `yes_no`, nhưng agent hỏi nội dung trước — về nghiệp vụ đây vẫn là "hỏi lại trước khi làm", song sai loại câu hỏi; cần người xem ngữ cảnh "bản tin này" chưa có nội dung để quyết định đúng/sai. Tương tự, extra tool call (G10 ở v4) cần người xem `fetch` đó có thực sự vô ích không.
- **Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?** (1) Đưa rule confirmation thành **few-shot 2 ví dụ** ngay đầu prompt (user yêu cầu đăng → `clarify(yes_no)`), vì rule dạng mệnh lệnh đã không thắng được xu hướng hỏi nội dung; (2) tách `send`/`clarify` thành một "confirmation protocol" trong description của `send`; (3) chạy Small Local Model để đo khoảng cách prompt cloud → local.
- **Hạn chế khác:** eval nhóm chỉ 10 case; v4/v5 base 19/20; transcript live chat chạy trên bản v3 trước merge, chưa quay lại trên v5; chưa có báo cáo của thành viên thứ 4.

## 8. Tài liệu tham khảo

- Wikipedia REST API — `https://en.wikipedia.org/api/rest_v1/page/summary/`
- Algolia Hacker News Search API — `https://hn.algolia.com/api/v1/`
- Tavily Search API — `https://api.tavily.com/search`
- Firecrawl Scrape API — `https://api.firecrawl.dev/v1/scrape`
- arXiv API — `https://export.arxiv.org/api/query`
- APA 7th edition — Publication Manual of the American Psychological Association
