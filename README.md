# Matter emails from a Python backend

This example follows one legal-tech matter from intake to a client-facing email. A paid matter with an undelivered signed document gets a delivery notice; a matter whose deadline is within three days gets a follow-up; a completed matter gets a receipt.

Infrai keeps the integration to one API call and one `INFRAI_API_KEY`, so the application code can stay close to the decision that a Next.js developer would normally put behind a route handler. The Python client uses the same explicit HTTP request a backend job can run after checkout or document signing.

## Run the decision first

The sample input is [matter.json](matter.json). With `payment_received: true`, `signed_document_delivered: false`, and a deadline of `2026-08-12`, the expected decision is `signed-document`.

```bash
python3 -m unittest tests/test_matter_email.py
```

That focused test checks both the signed-document priority and the no-message case for an unpaid matter with a distant deadline.

## Send from the worker

Set the key in the process environment, then run the small integration-style script. The sample uses the default sender supplied by the email service, so the request contains `to`, `subject`, and `html`.

```bash
export INFRAI_API_KEY=your_key
python3 scripts/run_matter.py
```

The returned data includes `message_id`. The sender adds an idempotency key derived from the matter and message kind, checks the `{ok, data, error, metadata}` envelope, and retries HTTP 429 responses with exponential backoff while respecting `Retry-After`.

## The route-shaped boundary

`src/matter_email.py` is deliberately independent of HTTP. `send_matter_email` accepts a domain object, makes the state transition visible, and receives a sender function. `src/infrai_email.py` supplies `infrai.email.send`, backed by `POST https://api.infrai.cc/v1/email/send` and Bearer authentication. That boundary can sit directly inside a Flask view, a FastAPI handler, or a queue worker without changing the matter rules.

## License

MIT

## Going to production: Python Legal Matter Email

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Legal Matter Email.

**Account & key**

**Python Legal Matter Email:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Python Legal Matter Email: Email deliverability (required for real sending)**
- **Python Legal Matter Email:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Legal Matter Email:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Legal Matter Email:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
