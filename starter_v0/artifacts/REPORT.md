# Day 04 Lab v2 Report — Research Agent

## Team

- **Team Name**: VinUni AI20k
- **Members**: VinUni AI20k Team & Students
- **Provider/model**: openrouter / `meta/llama-3.3-70b-instruct` (Evaluation runs) & gemini / `gemini-1.5-flash` (Baseline development runs)

## Final Metrics

- **Final version**: v2 (Day 04 Lab v2 Completion)
- **Final artifact_version**: v2+pec91d053d30f+t6e21845ea3a5
- **Best base run file**: `runs/v1_B_base_openrouter_20260602T144154323859.json`
- **Base case accuracy**: 1.0 (20/20 cases passed)
- **Base tool routing accuracy**: 1.0
- **Base argument accuracy**: 1.0
- **Group eval run file**: `runs/v1_B_group_openrouter_20260602T145044675684.json`
- **Group eval accuracy**: 1.0 (10/10 cases passed)
- **Chat transcript file**: `transcripts/v2_openrouter_20260602T145543717089.transcript.json`

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi repo mẫu trước khi sửa prompt hoặc tool declaration. | - | 0.5625 | `runs/v0_B_base_gemini_20260602T123816407145.json` |
| v1 | system_prompt.md | Prompt rõ ràng về `clarify`, confirmation, scope, parallel tool use và argument conventions sẽ giảm việc model đoán bừa hoặc sai boundary. | 0.5625 | 0.8333 | `runs/v1_B_base_gemini_20260602T134746673233.json` |
| v2 | tools.yaml | Làm rõ core tool declarations đặc biệt là `clarify.response_type`, giúp model truyền đúng args. | 0.8333 | 0.9444 | `runs/v2_B_base_gemini_20260602T142602864518.json` |
| v3 | system_prompt.md | Prompt bắt buộc hỏi xác nhận `yes_no` trước khi send/post/publish sẽ fix lỗi `R12_confirm_before_send`. | 0.9444 | 1.0 | `runs/v3_B_base_gemini_20260602T143100429911.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| **R03_web_news_routing** | wrong_tool / wrong_arg_value | `lookup(query="AI news today", topic="news")` | Chọn đúng tool nhưng query bị nhét cả "news today" và thiếu `timeframe=day`. | v1 thêm convention: `query="AI"`, `topic="news"`, `timeframe="day"`. |
| **R08_out_of_scope** | out_of_scope | `send(text="Nguyên hàm của x^2...")` | Gọi tool cho câu toán ngoài scope. | v1 thêm scope boundary, không dùng tool cho toán/coding/meta. |
| **R10_missing_handle** | missing_info | `timeline(screenname="sama", limit=5)` | Tự đoán account Sam Altman dù user không cung cấp account. | v1 yêu cầu dùng `clarify` khi thiếu account. |
| **R11_missing_url** | missing_info | `lookup(query="tóm tắt bài viết mới nhất...")` | Tự đoán topic thay vì hỏi URL. | v1 yêu cầu dùng `clarify` khi thiếu URL. |
| **R12_confirm_before_send** | wrong_boundary | `send(text="Bản tin mới nhất...")` | Gọi `send` khi chưa có xác nhận rõ ràng. | v1 thêm confirmation boundary trước khi gửi/đăng. |

## Team Eval Cases

List of 10 cases added to `data/eval_group.json` covering core, bonus, and new tools:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| **G01_github_search** | Tìm kiếm repo GitHub theo query với mặc định sort là stars | `github(query="Llama 3", sort="stars")` | PASS |
| **G02_github_details** | Lấy chi tiết repo GitHub từ tên đầy đủ dạng owner/repo | `github(repository="facebookresearch/llama")` | PASS |
| **G03_policy_source_citation** | Tìm kiếm chính sách công ty về source_citation | `policy(query="trích dẫn arXiv", policy_area="source_citation")` | PASS |
| **G04_papers_search** | Tìm bài báo arXiv mới nhất và truyền tham số sort_by chính xác | `papers(query="Retrieval-Augmented Generation", sort_by="submittedDate")` | PASS |
| **G05_paper_text_pages** | Trích xuất text bài báo arXiv với max_pages cụ thể | `paper_text(arxiv_url="1706.03762", max_pages=3)` | PASS |
| **G06_github_missing_query** | Thiếu query ở lượt 1, bổ sung ở lượt 2 và gọi github tool | `github(query="stable diffusion")` | PASS |
| **G07_send_telegram_confirm** | Yêu cầu send ở lượt 1 -> clarify, lượt 2 xác nhận -> send với confirmed=true | `send(text="Mô hình Llama 3.3...", confirmed=true)` | PASS |
| **G08_policy_missing_area** | Hỏi chung chung về chính sách -> hỏi lại, lượt 2 bổ sung -> policy data_privacy | `policy(query="bảo mật dữ liệu", policy_area="data_privacy")` | PASS |
| **G09_github_detail_clarify** | Muốn xem chi tiết repo nhưng thiếu tên -> hỏi lại, lượt 2 cung cấp -> github details | `github(repository="facebookresearch/llama")` | PASS |
| **G10_out_of_scope_math** | Lượt 1 toán học ngoài phạm vi -> từ chối, lượt 2 chuyển sang tìm paper arXiv -> gọi papers | `papers(query="đạo hàm")` | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| **Turn 1** | Tìm kiếm các bài viết của Sam Altman trên Twitter | `timeline(screenname="sama", limit=5)` | v2 | Lấy thành công 5 tweet gần đây của `@sama` |
| **Turn 2** | Gửi bài tóm tắt này lên Telegram: Mô hình Llama 3.3... | `clarify(question="...", response_type="yes_no")` | v2 | Hỏi lại xác nhận trước khi thực hiện gửi |
| **Turn 3** | Có, gửi đi | `send(text="Mô hình Llama 3.3...", confirmed=true)` | v2 | Gọi tool gửi tin nhắn với cờ xác nhận `confirmed=true` |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram)** | `tools/send/tool.py` | Kiểm tra cờ xác nhận `confirmed` và gửi dữ liệu lên Telegram API. | Guardrail: Yêu cầu bắt buộc hỏi xác nhận qua `clarify(yes_no)` trước khi gọi `send`. |
| **arXiv / Company Policy** | `tools/papers/tool.py`, `tools/policy/tool.py` | Tìm kiếm chính sách công ty và tra cứu paper arXiv qua API. | Phân loại đúng phân vùng tài liệu và chủ đề tìm kiếm. |
| **UI** | `app.py` | Streamlit UI trực quan với giao diện cao cấp, cài đặt tham số, quản lý prompt và log tool chạy. | Phục vụ demo thực tế, hiển thị rõ ràng từng bước gọi tool của Agent. |

## Reflection

- **Which fixes belonged in `system_prompt.md`?**
  - Các quy định về phạm vi (out of scope), quy tắc chuẩn hóa argument (lấy query sạch, map timeframe), quy tắc hội thoại nhiều lượt (carrying over context), và đặc biệt là ranh giới xác nhận an toàn (safety confirmation boundary) trước khi thực hiện gửi.
- **Which fixes belonged in `tools.yaml`?**
  - Định nghĩa kiểu dữ liệu chính xác cho tham số, mô tả chi tiết nhiệm vụ và điều kiện kích hoạt của từng tool (như loại phản hồi của `clarify` là `text`/`yes_no`/`choice`), giúp mô hình tự tin trích xuất tham số.
- **Which failure needed manual review instead of automatic grading?**
  - Các trường hợp gọi API bị lỗi mạng hoặc bị rate limit từ nhà cung cấp (429 Resource Exhausted) cần được đánh giá thủ công hoặc phân tách rõ ràng để tránh làm giảm điểm đánh giá logic của agent.
- **What would you improve next?**
  - Nâng cấp cơ chế lưu vết (session history) thông minh hơn để xử lý tốt hơn các câu lệnh sửa đổi phức tạp (complex correction) và tối ưu hóa thêm tốc độ phản hồi của các tool gọi API ngoài.
