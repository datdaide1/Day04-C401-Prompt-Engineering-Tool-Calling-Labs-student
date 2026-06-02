# Báo Cáo Demo Day 04 Lab v2 - Research Agent

## Nhóm

- Team:
- Members:
- Provider/model: gemini / gemini-3.1-flash-lite

## Metrics Base Eval

Các kết quả dưới đây lấy từ `runs/*.json` thật. Một số case bị `provider_error` do Gemini free-tier rate limit, nên `case_accuracy` được tính trên số case đo được (`measured_cases`), không phải toàn bộ 20 case.

| Version | Run File | Artifact Version | Case Được Đo | Provider Error | Case Accuracy | Tool Routing Accuracy | Argument Accuracy | Multiturn Accuracy |
|---|---|---|---:|---:|---:|---:|---:|---:|
| v0 | runs/v0_B_base_gemini_20260602T123816407145.json | v0+pf0c107a9d7a1+t011c271ef0bb | 16/20 | 4 | 0.5625 | 0.75 | 0.5625 | 0.5 |
| v1 | runs/v1_B_base_gemini_20260602T134746673233.json | v1+pd745c44513e8+t011c271ef0bb | 18/20 | 2 | 0.8333 | 1.0 | 0.8333 | 1.0 |
| v2 | runs/v2_B_base_gemini_20260602T142602864518.json | v2+pd745c44513e8+t390f5d5c4a81 | 18/20 | 2 | 0.9444 | 1.0 | 0.9444 | 1.0 |
| v3 | runs/v3_B_base_gemini_20260602T143100429911.json | v3+p4f7db33f5460+t390f5d5c4a81 | 17/20 | 3 | 1.0 | 1.0 | 1.0 | 1.0 |

## Version Evidence

| Version | Artifact Đã Sửa | Giả Thuyết | Metric Trước | Metric Sau | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi repo mẫu trước khi sửa prompt hoặc tool declaration. |  | 0.5625 | runs/v0_B_base_gemini_20260602T123816407145.json |
| v1 | system_prompt.md | Prompt rõ hơn về `clarify`, confirmation, scope, parallel tool use và argument conventions sẽ giảm việc model đoán bừa hoặc sai boundary. | 0.5625 | 0.8333 | runs/v1_B_base_gemini_20260602T134746673233.json |
| v2 | tools.yaml | Tool descriptions rõ hơn, đặc biệt `clarify.response_type`, sẽ giúp model truyền đúng args hơn. | 0.8333 | 0.9444 | runs/v2_B_base_gemini_20260602T142602864518.json |
| v3 | system_prompt.md | Prompt bắt buộc hỏi xác nhận `yes_no` trước khi send/post/publish sẽ fix lỗi `R12_confirm_before_send`. | 0.9444 | 1.0 | runs/v3_B_base_gemini_20260602T143100429911.json |

## Các Thay Đổi Chính

### v1 - Sửa `system_prompt.md`

Mục tiêu của v1 là đảo ngược prompt mẫu ban đầu, vì prompt cũ khuyến khích model đoán bừa, không hỏi lại, gửi luôn, và chỉ chọn một tool.

Các rule đã thêm:

- Thiếu account hoặc URL thì gọi `clarify`, không tự đoán.
- Send/post/publish phải hỏi xác nhận trước.
- Câu ngoài scope research/news/social/url thì không gọi tool.
- Cho phép gọi nhiều tool nếu user yêu cầu nhiều nguồn.
- Chuẩn hóa argument: `query` là chủ đề sạch, thời gian đi vào `timeframe`.

### v2 - Sửa core tools trong `tools.yaml`

Mục tiêu của v2 là làm rõ declaration của các core tools, không đổi tên tool và không đổi implementation.

Các phần đã sửa:

- `clarify`: bắt buộc truyền `response_type`; `text` cho thiếu account/URL, `yes_no` cho xác nhận gửi/đăng/publish.
- `timeline`: chỉ dùng cho tweet/post của account cụ thể; thiếu account thì `clarify`.
- `social_search`: dùng cho tweet theo chủ đề; `Top` khi user nói top/phổ biến/viral.
- `lookup`: dùng cho web/news; `query` là chủ đề sạch; `hôm nay -> timeframe=day`.
- `fetch`: chỉ dùng khi có URL rõ ràng.
- `format`: chỉ format items đã có, không fetch/search dữ liệu mới.

### v3 - Sửa tiếp `system_prompt.md`

Mục tiêu của v3 là fix lỗi còn lại ở `R12_confirm_before_send`.

Các rule đã làm mạnh:

- Rule thiếu thông tin không được override rule xác nhận send/post/publish.
- Nếu latest user request yêu cầu send/post/publish/upload lên Telegram hoặc external channel mà chưa xác nhận, tool tiếp theo bắt buộc là `clarify(response_type="yes_no")`.
- Không hỏi nội dung bản tin trước trong boundary case này; phải hỏi xác nhận trước.

## Phân Tích Lỗi Theo Version

### v0

| Case ID | Failure Type | Tool Call Thực Tế | Lỗi Gì | Fix Sau Đó |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | lookup(query="AI news today", topic="news") | Chọn đúng tool nhưng query bị nhét cả "news today" và thiếu `timeframe=day`. | v1 thêm convention: `query="AI"`, `topic="news"`, `timeframe="day"`. |
| R08_out_of_scope | out_of_scope | send(text="Nguyên hàm của x^2...") | Gọi tool cho câu toán ngoài scope. | v1 thêm scope boundary, không dùng tool cho toán/coding/meta. |
| R10_missing_handle | missing_info | timeline(screenname="sama", limit=5) | Tự đoán account Sam Altman dù user không cung cấp account. | v1 yêu cầu dùng `clarify` khi thiếu account. |
| R11_missing_url | missing_info | lookup(query="tóm tắt bài viết mới nhất về công nghệ AI") | Tự đoán topic thay vì hỏi URL. | v1 yêu cầu dùng `clarify` khi thiếu URL. |
| R12_confirm_before_send | wrong_boundary | send(text="Bản tin mới nhất...") | Gọi `send` khi chưa có xác nhận rõ ràng. | v1 thêm confirmation boundary trước khi gửi/đăng. |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | lookup(query="AI news today"...); social_search(query="AI") | Đã gọi cả hai tool nhưng query lookup chưa sạch. | v1/v2 làm rõ query convention. |
| M06_switch_tool | wrong_tool / wrong_arg_value | lookup(query="OpenAI news", topic="news") | Multi-turn đổi tool đúng nhưng query vẫn bị thêm "news". | v1 thêm multi-turn và query-cleaning rules. |

### v1

| Case ID | Failure Type | Tool Call Thực Tế | Lỗi Gì | Fix Sau Đó |
|---|---|---|---|---|
| R10_missing_handle | missing_info | clarify(question="Bạn muốn xem 5 tweet mới nhất của tài khoản nào?") | Đúng tool `clarify` nhưng thiếu `response_type="text"`. | v2 sửa declaration `clarify`, đưa `response_type` vào required. |
| R11_missing_url | missing_info | clarify(question="Bạn vui lòng cung cấp đường dẫn...") | Đúng tool `clarify` nhưng thiếu `response_type="text"`. | v2 làm rõ `text` cho thiếu account/URL. |
| R12_confirm_before_send | wrong_boundary | clarify(question="Bạn vui lòng cung cấp nội dung bản tin...") | Đúng tool `clarify` nhưng thiếu `response_type="yes_no"` và hỏi nội dung thay vì xác nhận. | v2 làm rõ `yes_no` cho send/post/publish. |

### v2

| Case ID | Failure Type | Tool Call Thực Tế | Lỗi Gì | Fix Sau Đó |
|---|---|---|---|---|
| R12_confirm_before_send | wrong_boundary | clarify(question="Bạn vui lòng cung cấp nội dung bản tin muốn đăng lên Telegram nhé?", response_type="text") | Model vẫn xem đây là thiếu nội dung nên hỏi text, trong khi eval muốn hỏi xác nhận yes/no. | v3 làm mạnh rule: send/post/publish luôn hỏi xác nhận `yes_no` trước, không hỏi nội dung trước. |

### v3

Không còn failure do tool-routing hoặc argument trên các case được đo. Run v3 vẫn có 3 `provider_error` do Gemini rate limit:

- M04_clarify_then_url
- M05_correction_limit
- M06_switch_tool

Các lỗi này là lỗi provider/quota, không phải lỗi chọn tool. Trong summary v3: `passed_cases=17`, `measured_cases=17`, `case_accuracy=1.0`.

## Hạn Chế

- Các run dùng Gemini free-tier nên bị `429 RESOURCE_EXHAUSTED` ở một số case.
- Để có run sạch hơn, nên thêm delay giữa các case hoặc chạy lại sau khi quota reset để đạt `provider_error_cases=0`.

## Việc Cần Làm Tiếp

- Thêm 10 case vào `data/eval_group.json`, gồm 5 single-turn và 5 multi-turn.
- Chạy group eval bằng version v3.
- Chạy `chat.py` bằng version v3 để lấy transcript evidence.
- Phần bonus tools do thành viên phụ trách bonus điền thêm nếu có chạy `policy`, `papers`, `paper_text`, `send`.
- Điền `REPORT.md` chính thức từ log thật sau khi có group eval và chat transcript.

