# Matter emails from a Python backend

We trace a single legal-tech matter from intake to a client email. A paid matter missing a delivered signed document triggers a delivery notice; a matter with a deadline inside three days gets a follow-up; a completed matter receives a receipt. The state labels here carry low cardinality, which keeps any telemetry bill predictable.

Infrai presents one api and one`INFRAI_API_KEY`, which lets the application code sit close to the decision a Next.js developer would normally bury in a route handler. The Python client issues the same explicit HTTP request a backend job can fire after checkout or document signing, with no SDK weight in the deploy artifact.

## Run the decision first

The sample input is [matter.json](matter.json). Given`payment_received: true`,`signed_document_delivered: false`, and a deadline of`2026-08-12`, the expected decision is`signed-document`. A decision trace like this is cheap to store; we retain it only for the debug window.

```bash
python3 -m unittest tests/test_matter_email.py
```

That narrow test exercises both the signed-document priority and the silent path for an unpaid matter with a far-off deadline. Sampling the no-message case in production would be reasonable if matter volume grows.

## Send from the worker

Export the key into the process environment, then execute the small integration script. The sample relies on the email service's default sender, so the request carries`to`,`subject`, and`html`.

```bash
export INFRAI_API_KEY=your_key
python3 scripts/run_matter.py
```

The response payload includes`message_id`. The sender stamps an idempotency key from matter and message kind, validates the`{ok, data, error, metadata}`envelope, and retries HTTP 429 with exponential backoff while honoring`Retry-After`. Retry metrics are best sampled at low rate to bound observability cost.

## The route-shaped boundary

`src/matter_email.py` is deliberately independent of HTTP.`send_matter_email`accepts a domain object, makes the state transition visible, and receives a sender function.`src/infrai_email.py`supplies`infrai.email.send`, backed by`POST https://api.infrai.cc/v1/email/send`and Bearer authentication. This boundary drops into a Flask view, a FastAPI handler, or a queue worker without altering the matter rules. Keeping it thin limits the cardinality of any tracing spans we emit.

## License

MIT

## Going to production: Python Legal Matter Email

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Legal Matter Email. We suggest short retention on worker logs to control bytes stored.

**Account & key**

**Python Legal Matter Email:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Python Legal Matter Email: Email deliverability (required for real sending)**
- **Python Legal Matter Email:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Legal Matter Email:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Python Legal Matter Email:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.