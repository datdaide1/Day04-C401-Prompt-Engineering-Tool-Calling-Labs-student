# Research Agent Tool Calling - Gioi Thieu Du An

## 1. Tong Quan Du An

Research Agent Tool Calling la mot du an lab ve xay dung agent nghien cuu co kha nang goi tool that. Agent nhan yeu cau tu nguoi dung, phan tich muc dich, chon tool phu hop, truyen tham so, chay tool, sau do tong hop ket qua thanh cau tra loi.

Muc tieu chinh cua du an khong chi la tao chatbot tra loi hay, ma la hieu va cai thien quy trinh:

1. Chay baseline bang model that.
2. Doc log JSON de xem model goi sai tool, sai tham so, goi tool thua, hoac thieu buoc hoi lai.
3. Sua `system_prompt.md` hoac `tools.yaml`.
4. Chay lai eval va ghi version log.
5. Tu viet them eval cases cua nhom.
6. Viet report dua tren evidence that tu run logs.

Du an hien co UI Streamlit de demo truc quan, co bo eval tu dong, co transcript chat, va co nhieu tool phuc vu nghien cuu.

## 2. Muc Tieu Chinh

Du an huong toi cac muc tieu sau:

- Xay dung mot research agent co the su dung nhieu tool khac nhau.
- Kiem tra kha nang tool routing cua model: chon dung tool va dung tham so.
- Cai thien prompt va tool declaration dua tren log that.
- Tao bo eval rieng cua nhom de kiem tra cac tinh huong ngoai base eval.
- Demo agent qua giao dien Streamlit.
- Ghi lai day du evidence: run JSON, transcript JSON, version log va report.

## 3. Cach Hoat Dong Cua Agent

Quy trinh hoat dong tong quat:

1. Nguoi dung nhap yeu cau, vi du: "Tin tuc AI hom nay co gi noi bat?"
2. Agent gui system prompt, lich su hoi thoai va danh sach tool declaration cho model.
3. Model quyet dinh co can goi tool hay khong.
4. Neu can, model tra ve tool call, vi du:

   ```text
   lookup(query="AI", topic="news", timeframe="day")
   ```

5. Chuong trinh chay tool tuong ung trong thu muc `tools/`.
6. Tool tra ve ket qua dang JSON.
7. Agent dung ket qua tool de tra loi nguoi dung.
8. Neu chay eval, toan bo qua trinh duoc luu vao `runs/*.json`.
9. Neu chat live, transcript duoc luu vao `transcripts/*.transcript.json`.

## 4. Cau Truc Thu Muc

Thu muc chinh cua project:

```text
starter_v0/
  agent.py                    # Loi agent one-shot dung cho eval
  chat.py                     # Chat live nhieu luot, co transcript
  app.py                      # Streamlit UI
  run_eval.py                 # Chay eval va tao runs/*.json
  versioning.py               # Tao artifact version, prompt hash, tools hash
  artifacts/
    system_prompt.md          # Prompt chinh cua agent
    tools.yaml                # Khai bao tool cho model
    version_log.csv           # Nhat ky version v0-v3
    REPORT.md                 # Bao cao chinh thuc
    demo_REPORT.md            # Ban demo report / nhap
  data/
    eval_base.json            # Bo eval goc, khong sua
    eval_group.json           # Bo eval do nhom tu viet
    eval_research_extension.json
  tools/
    clarify/
    timeline/
    social_search/
    lookup/
    fetch/
    format/
    send/
    policy/
    papers/
    paper_text/
    github/
  providers/
    gemini_provider.py
    openrouter_provider.py
    openai_provider.py
    anthropic_provider.py
  runs/
    *.json                    # Log eval
  transcripts/
    *.transcript.json         # Log chat live
```

## 5. Cac Thanh Phan Quan Trong

### 5.1 `system_prompt.md`

Day la file prompt chinh dinh huong hanh vi cua agent.

Prompt hien tai quy dinh:

- Chi goi tool khi yeu cau nam trong pham vi research.
- Khong goi tool cho bai toan, coding, hoac cau hoi meta khong can tool.
- Neu thieu account hoac URL thi dung `clarify`, khong doan bua.
- Neu user muon send/post/publish thi phai hoi xac nhan `yes_no` truoc.
- Dung dung tool cho tung loai request.
- Giu `query` gon sach, khong nhet "news today" vao query khi da co `topic` va `timeframe`.
- Xu ly multi-turn bang cach dung ngu canh cu nhung uu tien latest turn.

### 5.2 `tools.yaml`

Day la file khai bao tool cho model thay. Moi tool co:

- `name`: ten tool.
- `description`: mo ta khi nao dung tool.
- `parameters`: cac tham so dau vao.
- `required`: tham so bat buoc.

Model dua vao `tools.yaml` de quyet dinh:

- Goi tool nao.
- Truyen argument gi.
- Khi nao can hoi lai user.

### 5.3 `run_eval.py`

File nay dung de chay eval tu dong.

Vi du:

```bash
python run_eval.py --provider gemini --version v3 --suite base --eval-cases data/eval_base.json
```

Ket qua duoc luu vao:

```text
runs/*.json
```

Run JSON gom:

- Summary metrics.
- Tool calls thuc te.
- Tool results.
- Failures.
- Artifact version.
- Prompt hash.
- Tools hash.

### 5.4 `chat.py`

File nay dung de chat live tren terminal.

Vi du:

```bash
python chat.py --provider gemini --version v3
```

Moi phien chat duoc luu vao:

```text
transcripts/*.transcript.json
```

Transcript dung de lam evidence trong report.

### 5.5 `app.py`

Day la Streamlit UI cua agent.

UI cho phep:

- Chon provider va model.
- Nhap request bang giao dien chat.
- Xem tool calls tung round.
- Xem tool results.
- Chinh system prompt truc tiep tren UI.
- Xem danh sach tool.
- Export chat transcript.

## 6. Cac Core Tools

Core tools la nhom tool chinh de pass base eval.

### 6.1 `clarify`

Chuc nang:

- Hoi lai user khi thieu thong tin.
- Tam dung de cho user tra loi o luot tiep theo.

Dung khi:

- Thieu account/handle.
- Thieu URL.
- Can xac nhan yes/no truoc khi gui/dang.

Vi du:

```text
User: Tom tat 5 tweet moi nhat giup minh
Tool: clarify(question="Ban muon xem tweet cua tai khoan nao?", response_type="text")
```

### 6.2 `timeline`

Chuc nang:

- Lay tweet/bai dang gan day cua mot account cu the.

Input:

```text
screenname
limit
```

Vi du:

```text
User: Lay 10 tweet moi nhat cua Elon Musk
Tool: timeline(screenname="elonmusk", limit=10)
```

### 6.3 `social_search`

Chuc nang:

- Tim tweet/bai dang theo chu de hoac keyword.

Input:

```text
query
search_type
limit
```

Vi du:

```text
User: Moi nguoi dang noi gi ve GPT-5 tren Twitter?
Tool: social_search(query="GPT-5", search_type="Latest")
```

### 6.4 `lookup`

Chuc nang:

- Tim kiem web hoac tin tuc bang Tavily.

Input:

```text
query
topic
timeframe
max_results
```

Vi du:

```text
User: Tin tuc AI hom nay co gi noi bat?
Tool: lookup(query="AI", topic="news", timeframe="day")
```

### 6.5 `fetch`

Chuc nang:

- Doc noi dung mot URL cu the bang Firecrawl.

Input:

```text
url
```

Vi du:

```text
User: Tom tat bai nay: https://openai.com/research/
Tool: fetch(url="https://openai.com/research/")
```

Neu user khong dua URL, agent phai dung `clarify`, khong duoc tu doan URL.

### 6.6 `format`

Chuc nang:

- Trinh bay cac item da co thanh markdown digest.

Tool nay khong tim du lieu moi. No chi format ket qua da lay tu tool khac.

Input:

```text
items
template
headline
```

Vi du:

```text
lookup -> format(template="daily_ai_vn")
```

## 7. Cac Bonus Tools

### 7.1 `send`

Chuc nang:

- Gui message len Telegram channel.

Input:

```text
text
confirmed
```

Guardrail:

- Chi duoc goi `send` khi user da xac nhan ro.
- Neu chua xac nhan, agent phai goi:

  ```text
  clarify(response_type="yes_no")
  ```

Neu thieu `TELEGRAM_BOT_TOKEN` hoac `TELEGRAM_CHAT_ID`, tool se khong gui duoc va tra ve loi cau hinh.

### 7.2 `policy`

Chuc nang:

- Tim trong tai lieu policy noi bo o `company_policy/*.md`.

Dung khi user hoi ve:

- Source/citation.
- Data privacy.
- External publishing.
- Tool usage.
- AI research workflow.

Vi du:

```text
policy(query="API key trong prompt", policy_area="data_privacy")
```

### 7.3 `papers`

Chuc nang:

- Tim paper/preprint tren arXiv.

Input:

```text
query
max_results
sort_by
```

Vi du:

```text
papers(query="AI agent evaluation", sort_by="relevance")
```

### 7.4 `paper_text`

Chuc nang:

- Tai PDF arXiv va trich text bang `pypdf`.

Input:

```text
arxiv_url
max_pages
max_chars
```

Vi du:

```text
paper_text(arxiv_url="1706.03762", max_pages=2)
```

Tool nay co ghi file local vao:

```text
arxiv_papers/
```

### 7.5 `github`

Chuc nang:

- Tim repository GitHub theo query.
- Lay thong tin chi tiet cua repo dang `owner/repo`.

Input:

```text
query
repository
sort
```

Vi du:

```text
github(query="Llama 3", sort="stars")
github(repository="facebookresearch/llama")
```

Day la tool moi nhom them vao project.

## 8. UI Streamlit

Project co UI Streamlit tai:

```text
starter_v0/app.py
```

Chay local:

```bash
cd starter_v0
source .venv/bin/activate
streamlit run app.py
```

UI co cac chuc nang:

- Chon provider: Gemini, OpenRouter, OpenAI, Anthropic.
- Chon model.
- Chinh temperature.
- Chinh max tool rounds.
- Xem va sua system prompt.
- Xem danh sach tool va tham so.
- Chat voi agent.
- Xem tool calls va tool results theo tung round.
- Export chat transcript.

Deploy tam thoi bang Cloudflare Tunnel:

```bash
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
cloudflared tunnel --url http://localhost:8501
```

Link demo dang dung:

```text
https://drinking-hoped-locally-lower.trycloudflare.com
```

Luu y: link nay chi hoat dong khi ca Streamlit va Cloudflare Tunnel dang chay tren may local.

## 9. Eval Va Ket Qua

Project co 3 loai eval:

### 9.1 Base Eval

File:

```text
data/eval_base.json
```

Muc dich:

- Test core routing.
- Test dung tool.
- Test dung argument.
- Test clarify khi thieu thong tin.
- Test boundary truoc khi send.
- Test multi-turn carry/correction.

Ket qua versioning:

| Version | Thay doi | Accuracy |
|---|---|---:|
| v0 | Baseline | 0.5625 |
| v1 | Sua system prompt | 0.8333 |
| v2 | Sua tools.yaml | 0.9444 |
| v3 | Sua confirmation boundary | 1.0 |

Best clean base run:

```text
runs/v1_B_base_openrouter_20260602T144154323859.json
accuracy: 1.0
provider_error_cases: 0
```

### 9.2 Group Eval

File:

```text
data/eval_group.json
```

Nhom da them 10 cases:

- 5 single-turn.
- 5 multi-turn.
- Cover core tools, bonus tools va tool moi `github`.

Run evidence:

```text
runs/v1_B_group_openrouter_20260602T145044675684.json
accuracy: 1.0
```

### 9.3 Extension Eval

File:

```text
data/eval_research_extension.json
```

Muc dich:

- Test bonus tools: `policy`, `papers`, `paper_text`.
- Test request ket hop nhieu tool.

Run evidence:

```text
runs/v1_B_extension_openrouter_20260602T145102059307.json
accuracy: 1.0
```

## 10. Version History

### v0 - Baseline

Prompt ban dau khuyen khich agent:

- Khong hoi lai.
- Doan bua thong tin.
- Gui luon khi user yeu cau send/post.
- Chi chon mot tool.

Ket qua:

- Sai clarify.
- Sai boundary send.
- Sai query/timeframe.
- Goi tool cho cau ngoai scope.

### v1 - Sua `system_prompt.md`

Them rule:

- Thieu info thi `clarify`.
- Send/post/publish phai hoi xac nhan.
- Khong goi tool ngoai scope.
- Cho phep parallel tool calls.
- Query phai sach.

Ket qua:

- Tool routing tang len 1.0.
- Con loi thieu `response_type`.

### v2 - Sua `tools.yaml`

Lam ro:

- `clarify.response_type` bat buoc.
- `text` cho missing account/URL.
- `yes_no` cho send/post/publish.
- Phan biet `timeline`, `social_search`, `lookup`, `fetch`.

Ket qua:

- Argument accuracy tang len 0.9444.
- Con loi R12: model van hoi content thay vi hoi confirmation.

### v3 - Sua confirmation boundary

Lam manh rule:

- Neu latest request la send/post/publish ma chua confirm, tool tiep theo bat buoc la:

  ```text
  clarify(response_type="yes_no")
  ```

Ket qua:

- Case accuracy dat 1.0 tren measured cases.

## 11. Cac Loi Va Cach Xu Ly

### 11.1 Gemini Rate Limit

Mot so run bi:

```text
429 RESOURCE_EXHAUSTED
```

Nguyen nhan:

- Gemini free-tier bi gioi han request per minute.

Cach xu ly:

- Chay lai sau khi quota reset.
- Them delay giua cac case.
- Dung OpenRouter cho run clean.

### 11.2 Fetch URL Khong Duoc

Tool `fetch` dung Firecrawl. Neu loi doc URL, co the do:

- Thieu `FIRECRAWL_API_KEY`.
- Firecrawl het quota.
- Website chan crawler.
- URL khong truy cap duoc.

Cach xu ly:

- Kiem tra `.env`.
- Test tool fetch truc tiep.
- Dung URL khac de demo.
- Copy noi dung bai viet vao chat neu site chan crawler.

### 11.3 Twitter Tool Khong Chay

`timeline` va `social_search` can:

```text
RAPIDAPI_KEY
RAPIDAPI_TWITTER_HOST
```

Neu thieu key, tool se tra ve loi.

### 11.4 Telegram Khong Gui Duoc

`send` can:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Neu thieu env, tool van route dung nhung khong gui that.

## 12. Bao Mat

Khong bao gio commit:

```text
.env
API keys
Bot token
Telegram chat id
```

File `.env` da duoc gitignore. Tuy nhien neu key bi lo qua screenshot/chat, can revoke key va tao key moi.

Nhung key thuong dung:

```text
GEMINI_API_KEY
TAVILY_API_KEY
FIRECRAWL_API_KEY
RAPIDAPI_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
GITHUB_TOKEN
```

## 13. Cau Hoi Demo Goi Y

### Core tools

```text
Tin tuc AI hom nay co gi noi bat?
```

```text
Lay 5 tweet moi nhat cua Sam Altman
```

```text
Moi nguoi dang noi gi ve GPT-5 tren Twitter?
```

```text
Tom tat bai nay: https://openai.com/research/
```

```text
Tom tat 5 tweet moi nhat giup minh
```

### Bonus tools

```text
Theo policy cong ty, co duoc dua API key vao prompt khong?
```

```text
Tim paper arXiv moi ve AI agent evaluation
```

```text
Doc paper arXiv 1706.03762, lay text 2 trang dau
```

```text
Tim repo GitHub pho bien ve Llama 3
```

```text
Dang ban tin nay len Telegram giup minh
```

## 14. Ket Luan

Du an Research Agent Tool Calling da xay dung duoc mot agent co kha nang:

- Goi tool dung theo yeu cau.
- Hoi lai khi thieu thong tin.
- Xu ly multi-turn.
- Doc URL, tim web, tim social post, tim paper, tra policy, tim GitHub repo.
- Co guardrail truoc khi gui Telegram.
- Co UI Streamlit de demo.
- Co eval va report dua tren log that.

Qua cac vong v0-v3, agent da cai thien tu baseline con nhieu loi len muc accuracy cao tren base eval va group eval. Diem quan trong nhat cua du an la quy trinh evidence-driven: moi thay doi prompt/tool declaration deu duoc do bang run JSON va ghi vao version log.

