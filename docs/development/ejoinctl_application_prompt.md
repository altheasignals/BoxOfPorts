# # System / Architecture Prompt for Codegen
You are scaffolding a **Python 3.11** command-line application named **bop** that wraps the **EJOIN Multi-WAN Router HTTP API v2.2**. The goal is to give operators a fast, reliable CLI for day-to-day tasks: sending test SMS (with variable substitution and per-port routing), monitoring tasks and delivery, browsing the inbox, basic device ops (switch SIM, lock/unlock, reboot, save config), and initial proxy/allowlist config.
## Authoritative API (must implement exactly)
Use the following endpoints and payloads as specified:
* **Device/port status (subscribe & push):** /goip_get_status.html?url=...&period=...&all_sims=... (server supplies a report URL; device pushes dev-status and port-status JSON). Message bodies and fields are defined in §3.1.3–3.1.4.ejoin_multiwan_router_http_api_…
* **Operate / device commands (GET params + JSON body):** POST /goip_send_cmd.html?username=...&password=... with body {"type":"command","op":"...","ports":"...","ops":[...]}
  * Supported op: get, set, lock, unlock, switch, reset(module), save, reboot, redial (+ mode, optional delay). (§4.1.1–4.1.3)ejoin_multiwan_router_http_api_…
* **Send SMS (bulk capable):** POST /goip_post_sms.html?username=...&password=... body:
  * {"type":"send-sms","task_num":N,"tasks":[{"tid":..., "from":"...", "to":"...", "sms":"...", "chs":"utf8|base64", "coding":0|1|2, "smstype":0, "smsc":"", "intvl":"ms", "tmo":sec, "sdr":0|1, "fdr":0|1, "dr":0|1, "sr_prd":sec, "sr_cnt":N}]} (§5.3.1)ejoin_multiwan_router_http_api_…
  * Response: { "code":200, "reason":"OK", "type":"task-status", "status":[{"tid":..., "status":"0 OK|..."}, ...]} with error codes 0–16. (§5.3.1.4)ejoin_multiwan_router_http_api_…
* **Task status report (push from device):** {"type":"status-report","rpt_num":n,"rpts":[{"tid":..., "sending":..,"sent":..,"failed":..,"unsent":..,"sdr":[...],"fdr":[...]},...]} (§5.3.2)ejoin_multiwan_router_http_api_…
* **Pause / Resume / Delete queued SMS:**
  * POST /goip_pause_sms.html body {"tids":[...]} (§5.3.3)ejoin_multiwan_router_http_api_…
  * POST /goip_resume_sms.html body {"tids":[...]} (§5.3.4)ejoin_multiwan_router_http_api_…
  * POST /goip_remove_sms.html body {"tids":[...]} (§5.3.5)ejoin_multiwan_router_http_api_…
* **Query queued tasks:** GET /goip_get_tasks.html?version=1.1&username=...&password=...&port={1-based}&pos={start}&num={count}&has_content=0|1 (§5.3.6)ejoin_multiwan_router_http_api_…
* **Receive SMS (push from device):** {"type":"recv-sms","sms_num":n,"sms":[[drFlag, "port","ts","sender","recipient","payload"], ...]}; payload is base64 for normal SMS; delivery reports carry "code scts". (§6.2)ejoin_multiwan_router_http_api_…
* **Query received SMS:** GET /goip_get_sms.html?username=...&password=...&sms_id=...&sms_num=...&sms_del=0|1 returning {"code":0,"reason":"OK","ssrc":"...","sms_num":...,"next_sms":...,"data":[...]}(§7.2)ejoin_multiwan_router_http_api_…
* **Proxy / whitelist / blacklist config:**
  * Proxy: GET/POST /proxy?username=...&password=...&mode=http|socks5 with op=enabled|disabled|add|update|delete and body {"proxies":[{"name":"...","port":...,"interfaces":[...], "active":0|1}]}. (§8.1)ejoin_multiwan_router_http_api_…
  * Proxy users: GET/POST /proxy_user?... with op=... and body {"users":[{"name":"...","pwd":"...","interfaces":[...],"mark":"..."}]}. (§8.2)ejoin_multiwan_router_http_api_…
  * URL whitelists/blacklists: GET/POST /proxy_white_list?... and /proxy_black_list?... with op=enabled|disabled|add|delete body {"urls":[ "1,*", "2,example.com", "3,*.example.com", "4,www.example.*" ]} (§8.3–8.4)ejoin_multiwan_router_http_api_…
* **IP allow/deny (device access):**
  * Whitelist: GET/POST /ip_white_list?username=...&password=... with body {"enbale":0|1,"deleted_set":[...], "added_set":[...]} (§9)ejoin_multiwan_router_http_api_…
  * Blacklist: GET/POST /ip_black_list?username=...&password=... with body {"enbale":0|1,"deleted_set":[...], "added_set":[...]}Note: “*” blocks all IPs; enable whitelist first to avoid lockout. (§10)ejoin_multiwan_router_http_api_…

⠀Use exactly the field names and codes as written above.
## Tech stack & quality bar
* **Python 3.11**, **Typer** (CLI), **httpx** (async client), **pydantic** (typed models), **rich** (pretty tables, progress), **sqlite** (lightweight local state), **jinja2** (message templating).
* Full type hints, docstrings, unit tests (pytest), and ruff-clean.
* .env support (python-dotenv) for EJOIN_HOST, EJOIN_PORT, EJOIN_USER, EJOIN_PASS.
* Provide a **Dockerfile** and make targets: make dev, make test, make lint, make build, make run.

⠀Project layout

bop/
  __init__.py
  config.py           # env & profile loader
  http.py             # httpx client factory, auth, retries, timeouts
  api_models.py       # pydantic models mirroring request/response shapes
  templating.py       # jinja2 environment, helper filters
  ports.py            # port parsing (e.g., "1A", "2B", "4-32", "2.02")
  sms.py              # send/pause/resume/delete/query
  inbox.py            # receive pull; local webhook receiver (optional)
  status.py           # subscribe to dev/port status & pretty print
  ops.py              # lock/unlock/switch/reset/save/reboot/redial
  proxy.py            # proxy/whitelist/blacklist & users
  iplists.py          # IP whitelist/blacklist convenience commands
  store.py            # sqlite for sent logs, task map tid→ports/vars
  cli.py              # Typer app wiring
tests/
  test_sms.py ...
## CLI: required commands & behavior
### 1) Send test SMS with variable substitution and per-port routing

bop sms send \
  --to +15551234567 \
  --text "Port {{port}} says hi at {{ts}}" \
  --ports 1A,2B,3C,4-8 \
  --repeat 1 \
  --intvl-ms 500 \
  --timeout 30
* Expand --ports into the device’s accepted forms; support ranges and 1.02 style.
* Render template variables per message: built-ins include port, ts (UTC ISO), idx (iteration index), and any --var key=val.
* Build send-sms body (one task per port for clarity), task_num == len(tasks). (§5.3.1)ejoin_multiwan_router_http_api_…
* Show a rich table: TID, Port, To, Status (“accepted” or error reason from task-status). (§5.3.1.4)ejoin_multiwan_router_http_api_…
* Persist a local mapping tid → {port,to,text,ts} in sqlite for follow-up.

⠀2) “Spray” the same number via multiple ports quickly

bop sms spray --to +15551234567 --text "Probe from {{port}}" --ports 1A-8D --intvl-ms 250
* Same as above; respect intvl and tmo. (§5.3.1 attributes intvl, tmo)ejoin_multiwan_router_http_api_…

⠀3) Track delivery / progress

bop sms watch --tids 1201,1202 --poll
* If your environment can’t expose a callback URL, support **polling** with /goip_get_tasks.html and print aggregates: sending/sent/failed/unsent plus per-destination details if present. (§5.3.2, §5.3.6)ejoin_multiwan_router_http_api_…ejoin_multiwan_router_http_api_…
* If --listen :8080 is provided, spin up an optional uvicorn/FastAPI endpoint to accept status-report pushes and update the display in real time. (§5.3.2)ejoin_multiwan_router_http_api_…

⠀4) Pause / resume / delete queued tasks

bop sms pause  --tids 1201,1202
bop sms resume --tids 1201,1202
bop sms rm     --tids 1201,1202
* Implement per spec with bodies {"tids":[...]} and print result codes. (§5.3.3–5.3.5)ejoin_multiwan_router_http_api_…

⠀5) Browse queued tasks

bop sms queue --port 1 --pos 0 --num 25 --content
* Calls /goip_get_tasks.html with has_content=1 when --content is set. (§5.3.6)ejoin_multiwan_router_http_api_…

⠀6) Inbox (received messages)

bop inbox pull --start-id 1 --limit 50 --delete
* Calls /goip_get_sms.html with sms_id, sms_num, sms_del. Decode base64 payloads. Print port, timestamp, sender, recipient, text, and whether it’s a delivery report. (§7.2)ejoin_multiwan_router_http_api_…

⠀7) Device/port status

bop status subscribe --callback https://ops.example.com/ejoin --period 60 --all-sims
bop status tail      # pretty-print dev-status / port-status as they arrive
* Send /goip_get_status.html?url=...&period=...&all_sims=1 to set the report URL. Render both dev-status (aggregate) and port-status (on change). (§3.1.1–3.1.4)ejoin_multiwan_router_http_api_…

⠀8) Operations: lock/unlock/switch/reset/save/reboot/redial

bop ops lock    --ports 1A,2B
bop ops unlock  --ports 1A
bop ops switch  --ports 2.02      # switch SIM to slot 2 on port 2
bop ops reset   --ports 3C        # reboot module on port
bop ops save
bop ops reboot  # device reboot
bop ops redial  --ports 1A --mode flight --delay 5
* Use /goip_send_cmd.html with body {"type":"command","op":"...", "ports":"...", ...} or with ops[] when op=multiple. Respect mode 0=flight, 1=fast and optional delay (seconds). (§4.1.2–4.1.3)ejoin_multiwan_router_http_api_…

⠀**IMEI note:** If IMEI is configurable via op=set + parameter name, expose:

bop ops set --param imei --value 86xxxxxxxxxxxxx --ports 2B
Wire this generically using par_name(n) semantics if present; otherwise document that IMEI requires device-specific parameter support. (§4.1.2, parameterized get/set)
ejoin_multiwan_router_http_api_…
### 9) Proxy and access rules (initially minimal)

bop proxy enable --mode socks5
bop proxy add --mode socks5 --name foo --port 1080 --interfaces 0 --active
bop proxy ls  --mode socks5
bop proxy-user add --mode http --name alice --pwd secret --interfaces 0
bop proxy-urls whitelist enable --mode http
bop proxy-urls whitelist add --mode http --url "3,*.example.com"
bop ip allow  --enable --add 192.168.1.0/24
bop ip deny   --enable --add "*"
* Implement per §8 (proxy) and §9–10 (IP lists), including warning that blacklist "*" blocks all IPs unless whitelist is enabled.ejoin_multiwan_router_http_api_…ejoin_multiwan_router_http_api_…

⠀UX & ergonomics
* Default host/port/user/pass from env or a saved **profile**. Commands accept overrides --host/--port/--user/--pass.
* Rich tables with columns, colors, and status codes decoded to human text (map all codes 0–16). (§5.3.1.4)ejoin_multiwan_router_http_api_…
* **Templating**: jinja2 with safe filters and built-in variables (port, ts, idx). Support --vars key=val multipliers.
* **Retries**: httpx with exponential backoff on 5xx, connection errors.
* **Timeouts**: default 10s connect, 30s read; make configurable.
* **Logging**: -v/--verbose toggles DEBUG HTTP logs; redact passwords.
* **SQLite**: store tasks (tid, ports, to, text hash, submitted_at), reports (tid, sent, failed, details), inbox (device ssrc, sms_id, sender, text).

⠀Security & safety
* Never log password or token query params.
* Confirm dangerous ops (device reboot, adding blacklist "*").
* Add a --dry-run to render JSON bodies without sending.

⠀Tests (pytest)
* Unit tests for: port parsing, templating, JSON bodies for send/ops, response parsing, error code mapping, inbox decoding base64, and CLI argument contracts.
* Use respx to mock httpx; include golden JSONs for each endpoint.

⠀Example session (golden paths)
**1** **Probe a number across 4 ports**

⠀
bop sms send --to +15551234567 --text "Hi from {{port}} at {{ts}}" --ports 1A,1B,1C,1D --intvl-ms 200
# Expect: task-status table with code 0 OK for each tid.
**2** **Watch delivery**

⠀
bop sms watch --tids 101,102 --poll
# Expect: aggregates updating until sent==total or failed>0 with reasons.
**3** **Check inbox and delete fetched**

⠀
bop inbox pull --start-id 1 --limit 100 --delete
# Expect: table with sender, ts, text; next_sms printed.
**4** **Switch SIM and reboot module**

⠀
bop ops switch --ports 2.02
bop ops reset  --ports 2B
**5** **Enable socks5 proxy on all SIM WANs**

⠀
bop proxy add --mode socks5 --name ops --port 1080 --interfaces 0 --active
bop proxy enable --mode socks5
bop proxy ls --mode socks5
## Implementation hints
* Normalize port tokens: accept 1A..1D, 1.01..1.04, ranges like 4-32 (expand to all ports per device capability; keep it purely syntactic on client side).
* For **status subscribe**, just set the URL once; the device then POSTs status periodically or on change. (§3.1)ejoin_multiwan_router_http_api_…
* When **spraying** one recipient with multiple ports, either:
  * one task per port with same to, or
  * a single task with from listing multiple ports; choose the **one-task-per-port** approach for easier attribution.
* Decode delivery reports vs normal SMS using the array’s first element and payload rules. (§6.2, §7.2)ejoin_multiwan_router_http_api_…

⠀Deliverables
* Working CLI with commands above, unit tests passing, and README containing:
  * Quickstart, env config, safety notes, endpoint references (section/page pointers as above), and examples.
* Dockerfile and Makefile.
* A minimal FastAPI server for optional **status-report** and **recv-sms** webhooks (behind --listen).
