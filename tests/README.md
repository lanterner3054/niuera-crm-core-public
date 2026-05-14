# Outreach idempotency script tests

Run the offline public script tests with:

```bash
python -m unittest discover -s tests
```

The tests use only fake fixtures under `tests/fixtures/`. They do not require production
services, private repositories, environment variables, secrets, or raw n8n workflow exports.

If the public Outreach idempotency scripts from PR #19 are not present in the checkout,
the test classes skip with a message explaining that the tests should run once those
assets are available.
