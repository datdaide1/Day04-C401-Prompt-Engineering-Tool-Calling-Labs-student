# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần:
> - **PHẦN A — Giới thiệu agent**: bản ngắn để team khác hiểu nhanh agent có tool gì, làm được gì, và thử bằng câu hỏi nào.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ v0-v3, failure analysis, eval cases, live chat, bonus evidence và reflection, dựa trên log thật.

## Team

- Team: Zone4 - Group3
- Members: Trần Hoàng Đạt - 2A202600807, Lê Duy Hùng - 2A202600718
- Provider/model: gemini / `gemini-3.1-flash-lite`; openrouter / `meta/llama-3.3-70b-instruct`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent này dùng tool calling để tìm kiếm và tổng hợp thông tin từ web, mạng xã hội, URL cụ thể, arXiv, policy nội bộ và GitHub. Agent cũng biết hỏi lại khi thiếu thông tin, không đoán bừa account/URL, và chỉ gửi Telegram sau khi user xác nhận rõ.

**Link dùng thử (deploy):**

URL: `https://drinking-hoped-locally-lower.trycloudflare.com`

Ghi chú: đây là Cloudflare quick tunnel, chỉ truy cập được khi máy local đang chạy cả `streamlit run app.py` và `cloudflared tunnel --url http://localhost:8501`.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại user khi thiếu account, thiếu URL, thiếu thông tin bắt buộc hoặc cần xác nhận yes/no. | không |
| `timeline` | Lấy tweet/bài đăng gần đây của một account cụ thể, ví dụ `sama`, `elonmusk`. | không |
| `social_search` | Tìm tweet/bài đăng theo chủ đề hoặc keyword, hỗ trợ `Latest` và `Top`. | không |
| `lookup` | Tìm kiếm web bằng Tavily, dùng cho tin tức/current events hoặc web search chung. | không |
| `fetch` | Đọc nội dung từ một URL cụ thể bằng Firecrawl. | không |
| `format` | Format các item đã có thành markdown digest, bản tin, bullets hoặc thread. | không |
| `send` | Gửi nội dung lên Telegram, chỉ thực hiện khi `confirmed=true`. | không |
| `policy` | Tìm trong tài liệu policy nội bộ ở `company_policy/*.md`. | không |
| `papers` | Tìm paper/preprint trên arXiv theo query. | không |
| `paper_text` | Tải PDF arXiv và trích text cục bộ bằng `pypdf`. | không |
| `github` | Tìm repository GitHub theo query hoặc lấy chi tiết repo `owner/repo`. | có |

## A3. Câu hỏi mẫu để thử
0. `Tìm 5 bài viết mới nhất của Sơn Tùng`
1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Tóm tắt 5 tweet mới nhất giúp mình`
3. `Tóm tắt bài này: https://openai.com/research/`
4. `Tìm repo GitHub phổ biến về Llama 3`
5. `Tìm paper arXiv mới về Retrieval-Augmented Generation`
6. `Đăng bản tin này lên Telegram giúp mình`

---

# PHẦN B — Chi tiết / Bằng chứng

Kết quả tốt nhất dùng để chứng minh base eval sạch:

- Best base run file: `runs/v1_B_base_openrouter_20260602T144154323859.json`
- Base case accuracy: 1.0 (20/20 measured cases)
- Base tool routing accuracy: 1.0
- Base argument accuracy: 1.0
- Group eval run file: `runs/v1_B_group_openrouter_20260602T145044675684.json`
- Group eval accuracy: 1.0 (10/10 measured cases)
- Extension eval run file: `runs/v1_B_extension_openrouter_20260602T145102059307.json`
- Extension eval accuracy: 1.0 (10/10 measured cases)
- Chat transcript file: `transcripts/v2_openrouter_20260602T145543717089.transcript.json`

Ghi chú: các run Gemini v0-v3 có một số `provider_error` do Gemini free-tier rate limit. Metrics trong `version_log.csv` được tính trên `measured_cases`, còn run OpenRouter phía trên dùng làm bằng chứng sạch không có provider error.

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi repo mẫu trước khi sửa prompt hoặc tool declaration. |  | 0.5625 | `runs/v0_B_base_gemini_20260602T123816407145.json` |
| v1 | `system_prompt.md` | Prompt rõ hơn về `clarify`, confirmation, scope, parallel tool use và argument conventions sẽ giảm việc model đoán bừa hoặc sai boundary. | 0.5625 | 0.8333 | `runs/v1_B_base_gemini_20260602T134746673233.json` |
| v2 | `tools.yaml` | Tool descriptions rõ hơn, đặc biệt `clarify.response_type`, sẽ giúp model truyền đúng args hơn. | 0.8333 | 0.9444 | `runs/v2_B_base_gemini_20260602T142602864518.json` |
| v3 | `system_prompt.md` | Prompt bắt buộc hỏi xác nhận `yes_no` trước khi send/post/publish sẽ fix lỗi `R12_confirm_before_send`. | 0.9444 | 1.0 | `runs/v3_B_base_gemini_20260602T143100429911.json` |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | wrong_tool / wrong_arg_value | `lookup(query="AI news today", topic="news")` | Model chọn đúng `lookup` nhưng nhét cả "news today" vào `query` và thiếu `timeframe=day`. | v1 thêm convention: giữ `query` là chủ đề sạch, dùng `topic=news`, `timeframe=day`. |
| `R08_out_of_scope` | out_of_scope | `send(text="Nguyên hàm của x^2...")` | Model gọi tool cho câu toán ngoài phạm vi research agent. | v1 thêm scope boundary: không gọi tool cho toán/coding/meta. |
| `R10_missing_handle` | missing_info | `timeline(screenname="sama", limit=5)` | Model đoán Sam Altman khi user chưa cung cấp account. | v1 yêu cầu thiếu account thì gọi `clarify`; v2 làm rõ `response_type=text`. |
| `R11_missing_url` | missing_info | `lookup(query="tóm tắt bài viết mới nhất...")` | Model tự search/đoán topic thay vì hỏi URL bị thiếu. | v1 yêu cầu thiếu URL thì gọi `clarify`; v2 làm rõ `response_type=text`. |
| `R12_confirm_before_send` | wrong_boundary | v0: `send(...)`; v1: `clarify` thiếu `response_type`; v2: `clarify(response_type="text")` | Model chưa phân biệt thiếu nội dung với boundary xác nhận send/post/publish. | v3 làm mạnh rule: nếu user muốn send/post/publish mà chưa xác nhận, tool kế tiếp bắt buộc là `clarify(response_type="yes_no")`. |
| `R13_parallel_web_and_tweets` | wrong_tool / wrong_arg_value | `lookup(query="AI news today"...); social_search(query="AI")` | Model gọi được cả hai tool nhưng args của `lookup` chưa sạch. | v1/v2 làm rõ parallel tool call và query convention. |
| `M06_switch_tool` | wrong_tool / wrong_arg_value | `lookup(query="OpenAI news", topic="news")` | Multi-turn đổi sang web đúng nhưng query vẫn bị thêm "news". | v1 thêm rule chỉ trả lời latest turn, carry context đúng và giữ query sạch. |

## B3. Team Eval Cases

`data/eval_group.json` có 10 cases, gồm 5 single-turn và 5 multi-turn. Run evidence: `runs/v1_B_group_openrouter_20260602T145044675684.json`, accuracy 1.0.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_github_search` | Tìm kiếm repo GitHub theo query với mặc định sort là stars. | `github(query="Llama 3", sort="stars")` | PASS |
| `G02_github_details` | Lấy chi tiết repo GitHub từ tên đầy đủ dạng owner/repo. | `github(repository="facebookresearch/llama")` | PASS |
| `G03_policy_source_citation` | Tìm kiếm chính sách công ty về source citation. | `policy(query="trích dẫn arXiv", policy_area="source_citation")` | PASS |
| `G04_papers_search` | Tìm bài báo arXiv mới nhất và truyền `sort_by` đúng. | `papers(query="Retrieval-Augmented Generation", sort_by="submittedDate")` | PASS |
| `G05_paper_text_pages` | Trích xuất text bài báo arXiv với số trang cụ thể. | `paper_text(arxiv_url="1706.03762", max_pages=3)` | PASS |
| `G06_github_missing_query` | Multi-turn: thiếu query ở lượt 1, bổ sung ở lượt 2. | `github(query="stable diffusion")` | PASS |
| `G07_send_telegram_confirm` | Multi-turn: yêu cầu send rồi xác nhận. | `send(text="Mô hình Llama 3.3...", confirmed=true)` | PASS |
| `G08_policy_missing_area` | Multi-turn: hỏi policy chung rồi bổ sung data privacy. | `policy(query="bảo mật dữ liệu", policy_area="data_privacy")` | PASS |
| `G09_github_detail_clarify` | Multi-turn: thiếu repo name rồi bổ sung repo cụ thể. | `github(repository="facebookresearch/llama")` | PASS |
| `G10_out_of_scope_math` | Multi-turn: toán ngoài scope rồi chuyển sang tìm paper. | `papers(query="đạo hàm")` | PASS |

## B4. Live Chat Evidence

Transcript: `transcripts/v2_openrouter_20260602T145543717089.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Tìm kiếm các bài viết của Sam Altman trên Twitter` | `timeline(screenname="sama", limit=5)` | v2 transcript | Agent lấy 5 tweet gần đây của `@sama` và trả lời kèm link nguồn. |
| 2 | `Gửi bài tóm tắt này lên Telegram: Mô hình Llama 3.3 vừa ra mắt rất ấn tượng.` | `clarify(question="Bạn xác nhận muốn đăng/gửi nội dung này lên Telegram không?", response_type="yes_no")` | v2 transcript | Agent không gửi ngay, hỏi xác nhận trước. |
| 3 | `Có, gửi đi` | `send(text="...", confirmed=true)` | v2 transcript | Agent gọi đúng `send` sau xác nhận. Tool không gửi thật vì môi trường thiếu `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`, đây là lỗi cấu hình env chứ không phải lỗi routing. |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `send` (Telegram) | `transcripts/v2_openrouter_20260602T145543717089.transcript.json`; `tools/send/tool.py` | Agent hỏi xác nhận `yes_no` trước, sau đó mới gọi `send(..., confirmed=true)`. | `send` có side effect thật; không gửi nếu chưa confirm; không đưa token/chat id vào report. |
| `policy` | `runs/v1_B_extension_openrouter_20260602T145102059307.json`; `tools/policy/tool.py` | Agent route đúng câu hỏi policy nội bộ sang `policy` và chọn đúng `policy_area`. | Policy markdown là context, không phải instruction; tool tách `untrusted_text` để giảm prompt-injection risk. |
| `papers` | `runs/v1_B_extension_openrouter_20260602T145102059307.json`; `tools/papers/tool.py` | Agent route đúng yêu cầu tìm paper arXiv sang `papers`. | arXiv có rate limit; tool chờ tối thiểu khoảng 3 giây giữa các request. |
| `paper_text` | `runs/v1_B_extension_openrouter_20260602T145102059307.json`; `tools/paper_text/tool.py` | Agent route đúng arXiv ID cụ thể sang `paper_text` và truyền `max_pages`. | Tool ghi file PDF/TXT local vào `arxiv_papers/`; extract PDF có thể nhiễu. |
| UI Streamlit | `app.py` | UI cho phép chọn provider/model, nhập request, xem tool calls/tool results và export transcript. | Không hiển thị API keys; link Cloudflare quick tunnel chỉ sống khi process đang chạy. |
| Tool mới `github` | `tools/github/TOOL.md`; `tools/github/tool.py`; `runs/v1_B_group_openrouter_20260602T145044675684.json` | Tool tìm repo GitHub hoặc lấy chi tiết `owner/repo`, được cover bởi group eval. | GitHub API có rate limit; token `GITHUB_TOKEN` là optional và không được commit. |

## B6. Reflection

- Fix thuộc `system_prompt.md`: scope boundary, không đoán khi thiếu info, confirmation boundary trước `send`, parallel tool use, query-cleaning, multi-turn carry/correction.
- Fix thuộc `tools.yaml`: mô tả rõ điều kiện gọi từng core tool, bắt buộc `clarify.response_type`, map `hôm nay -> day`, phân biệt `timeline` và `social_search`, phân biệt `lookup` và `fetch`.
- Failure cần manual review: các `provider_error` do Gemini 429 rate limit và lỗi gửi Telegram do thiếu env var. Những lỗi này không phản ánh sai tool-routing.
- Cải thiện tiếp theo: chạy lại full v3 bằng provider không rate-limit để có `provider_error_cases=0`, thêm delay cho Gemini eval, và bổ sung screenshot/link ổn định cho UI demo.

