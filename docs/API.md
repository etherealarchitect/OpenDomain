# OpenDomain API Reference

**Base URL**: `https://opendomain-api.fly.dev/api/v1` (production) or `http://localhost:8000/api/v1` (development)

**Interactive Docs**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the backend is running.

---

## Authentication

All endpoints except `POST /auth/register`, `POST /auth/login`, and `POST /whois/` require authentication.

Send a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Obtain a token by calling `POST /auth/login`.

### Example

```bash
# Login and capture token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}' \
  | jq -r '.access_token')

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/domains/
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad request — invalid input or business rule violation |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — account disabled or insufficient permissions |
| `404` | Not found — resource doesn't exist or doesn't belong to you |
| `409` | Conflict — duplicate resource (e.g., email already registered) |
| `422` | Validation error — request body failed schema validation |
| `429` | Rate limited — too many requests |
| `500` | Internal server error |

Validation errors (422) include field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Pagination

List endpoints that support pagination accept these query parameters:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `page` | integer | 1 | >= 1 | Page number |
| `per_page` | integer | 25 | 1-100 | Items per page |

---

## Auth

### Register

`POST /auth/register`

Create a new user account.

**Auth required**: No

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | Yes | Account email address |
| `password` | string | Yes | Account password |
| `full_name` | string | Yes | User's full name |
| `company` | string | No | Organization name |
| `phone` | string | No | Phone number |

**Response** (201):

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "company": null,
  "phone": null,
  "role": "USER",
  "is_active": true,
  "is_verified": false,
  "two_factor_enabled": false,
  "created_at": "2026-09-11T00:00:00Z"
}
```

**Errors**: `409` if email already registered.

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "strongpassword123",
    "full_name": "Jane Doe"
  }'
```

---

### Login

`POST /auth/login`

Authenticate and receive a JWT token.

**Auth required**: No

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | Yes | Account email |
| `password` | string | Yes | Account password |

**Response** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

**Errors**: `401` invalid credentials, `403` account disabled.

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "strongpassword123"}'
```

---

### Get Current User

`GET /auth/me`

Return the authenticated user's profile.

**Auth required**: Yes

**Response** (200): Same shape as register response.

---

### Update Profile

`PATCH /auth/me`

Update the authenticated user's profile. Only send fields you want to change.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | No | Updated name |
| `company` | string | No | Updated company |
| `phone` | string | No | Updated phone |

**Response** (200): Updated user object.

---

### Change Password

`POST /auth/change-password`

Change the authenticated user's password.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `current_password` | string | Yes | Current password for verification |
| `new_password` | string | Yes | New password |

**Response**: `204 No Content`

**Errors**: `400` if current password is incorrect.

---

## Domains

### Search Domains

`POST /domains/search`

Check availability and pricing for domain names.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Domain name or keyword (1-253 chars) |
| `tlds` | string[] | No | TLDs to check (e.g., `["com", "net", "io"]`). Checks defaults if omitted. |

**Response** (200):

```json
[
  {
    "domain": "example.com",
    "available": true,
    "price_cents": 1199,
    "premium": false
  },
  {
    "domain": "example.io",
    "available": true,
    "price_cents": 3999,
    "premium": false
  }
]
```

```bash
curl -X POST http://localhost:8000/api/v1/domains/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "myproject", "tlds": ["com", "dev", "io"]}'
```

---

### Register Domain

`POST /domains/register`

Register a new domain name.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `domain` | string | Yes | | Full domain name (e.g., `example.com`) |
| `period_years` | integer | No | 1 | Registration period (1-10 years) |
| `registrant_contact_id` | UUID | Yes | | Contact to use as registrant |
| `nameservers` | string[] | No | | Custom nameservers |
| `privacy_enabled` | boolean | No | true | WHOIS privacy protection |
| `auto_renew` | boolean | No | true | Automatic renewal |

**Response** (201):

```json
{
  "id": "uuid",
  "name": "example.com",
  "tld": "com",
  "status": "active",
  "owner_id": "uuid",
  "auto_renew": true,
  "privacy_enabled": true,
  "locked": false,
  "nameservers": "ns1.opendomain.dev,ns2.opendomain.dev",
  "registration_date": "2026-09-11T00:00:00Z",
  "expiry_date": "2027-09-11T00:00:00Z",
  "last_renewed": null,
  "price_cents": 1199,
  "renewal_price_cents": 1199,
  "created_at": "2026-09-11T00:00:00Z"
}
```

```bash
curl -X POST http://localhost:8000/api/v1/domains/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "registrant_contact_id": "550e8400-e29b-41d4-a716-446655440000",
    "period_years": 2,
    "privacy_enabled": true
  }'
```

---

### List Domains

`GET /domains/`

List all domains owned by the authenticated user.

**Auth required**: Yes

**Query parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `active`, `expired`, `pendingTransfer`, `suspended` |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 25, max: 100) |

**Response** (200): Array of domain objects.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/domains/?status=active&page=1&per_page=10"
```

---

### Get Domain

`GET /domains/{domain_id}`

Get detailed information about a specific domain.

**Auth required**: Yes

**Path parameters**: `domain_id` (UUID)

**Response** (200): Domain object.

**Errors**: `404` if not found or not owned by user.

---

### Update Domain

`PATCH /domains/{domain_id}`

Update domain settings. Only send fields you want to change.

**Auth required**: Yes

**Path parameters**: `domain_id` (UUID)

**Request body**:

| Field | Type | Description |
|-------|------|-------------|
| `nameservers` | string[] | Custom nameservers |
| `auto_renew` | boolean | Toggle auto-renewal |
| `privacy_enabled` | boolean | Toggle WHOIS privacy |
| `locked` | boolean | Toggle transfer lock |
| `registrant_contact_id` | UUID | Change registrant contact |
| `admin_contact_id` | UUID | Change admin contact |
| `tech_contact_id` | UUID | Change tech contact |
| `billing_contact_id` | UUID | Change billing contact |

**Response** (200): Updated domain object.

---

### Renew Domain

`POST /domains/{domain_id}/renew`

Renew a domain registration.

**Auth required**: Yes

**Path parameters**: `domain_id` (UUID)

**Request body**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `period_years` | integer | 1 | Renewal period in years |

**Response** (200): Updated domain object with new expiry date.

---

### Lock / Unlock Domain

`POST /domains/{domain_id}/lock`
`POST /domains/{domain_id}/unlock`

Enable or disable transfer lock on a domain.

**Auth required**: Yes

**Response** (200): Updated domain object.

---

### Get Auth Code

`GET /domains/{domain_id}/auth-code`

Retrieve the transfer authorization code for a domain.

**Auth required**: Yes

**Response** (200):

```json
{
  "auth_code": "xJ8k2m!@pQ"
}
```

---

### Transfer Domain In

`POST /domains/transfer`

Initiate a transfer of a domain from another registrar.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | Yes | Domain name to transfer |
| `auth_code` | string | Yes | Authorization code from current registrar |
| `registrant_contact_id` | UUID | Yes | Contact for the domain |

**Response** (201):

```json
{
  "id": "uuid",
  "domain_id": "uuid",
  "from_registrar": "Previous Registrar",
  "to_registrar": "OpenDomain",
  "status": "pending",
  "initiated_at": "2026-09-11T00:00:00Z",
  "completed_at": null
}
```

---

### Transfer Domain Out

`POST /domains/{domain_id}/transfer-out`

Initiate a transfer out to another registrar. Returns the auth code for the receiving registrar.

**Auth required**: Yes

**Response** (200):

```json
{
  "auth_code": "xJ8k2m!@pQ"
}
```

---

### Delete Domain

`DELETE /domains/{domain_id}`

Delete a domain (cancels registration).

**Auth required**: Yes

**Response**: `204 No Content`

---

## DNS

All DNS endpoints are scoped to a domain: `/domains/{domain_id}/dns/...`

### Get Zone

`GET /domains/{domain_id}/dns/`

Get the DNS zone and all records for a domain.

**Auth required**: Yes

**Response** (200):

```json
{
  "id": "uuid",
  "domain_id": "uuid",
  "zone_name": "example.com",
  "primary_ns": "ns1.opendomain.dev",
  "serial": 2026091101,
  "default_ttl": 3600,
  "dnssec_enabled": false,
  "records": [
    {
      "id": "uuid",
      "zone_id": "uuid",
      "record_type": "A",
      "name": "@",
      "content": "185.199.108.153",
      "ttl": 3600,
      "priority": null,
      "proxied": false,
      "enabled": true,
      "comment": null,
      "created_at": "2026-09-11T00:00:00Z",
      "updated_at": "2026-09-11T00:00:00Z"
    }
  ],
  "created_at": "2026-09-11T00:00:00Z",
  "updated_at": "2026-09-11T00:00:00Z"
}
```

---

### Create Record

`POST /domains/{domain_id}/dns/records`

Add a DNS record to a domain's zone.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `record_type` | string | Yes | | One of: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, PTR, ALIAS, TLSA, DS |
| `name` | string | Yes | | Record name (e.g., `@`, `www`, `mail`) |
| `content` | string | Yes | | Record value (e.g., IP address, hostname) |
| `ttl` | integer | No | 3600 | Time to live in seconds (60-86400) |
| `priority` | integer | No | | Priority (required for MX, SRV) |
| `proxied` | boolean | No | false | Whether the record is proxied |
| `comment` | string | No | | Optional note |

**Response** (201): DNS record object.

```bash
curl -X POST http://localhost:8000/api/v1/domains/$DOMAIN_ID/dns/records \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "A",
    "name": "www",
    "content": "185.199.108.153",
    "ttl": 300
  }'
```

---

### Create Records (Bulk)

`POST /domains/{domain_id}/dns/records/bulk`

Create multiple DNS records at once.

**Auth required**: Yes

**Request body**:

```json
{
  "records": [
    {"record_type": "A", "name": "@", "content": "185.199.108.153"},
    {"record_type": "CNAME", "name": "www", "content": "example.com"}
  ]
}
```

**Response** (201): Array of created DNS record objects.

---

### Update Record

`PATCH /domains/{domain_id}/dns/records/{record_id}`

Update an existing DNS record. Only send fields you want to change.

**Auth required**: Yes

**Request body**:

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | New record value |
| `ttl` | integer | New TTL |
| `priority` | integer | New priority |
| `proxied` | boolean | Toggle proxy |
| `enabled` | boolean | Enable/disable record |
| `comment` | string | Update comment |

**Response** (200): Updated DNS record object.

---

### Delete Record

`DELETE /domains/{domain_id}/dns/records/{record_id}`

Delete a DNS record.

**Auth required**: Yes

**Response**: `204 No Content`

---

### Export Zone (BIND format)

`GET /domains/{domain_id}/dns/export`

Export the DNS zone as a BIND-format zone file.

**Auth required**: Yes

**Response** (200):

```json
{
  "zone_name": "example.com",
  "zone_file": "$ORIGIN example.com.\n$TTL 3600\n@ IN SOA ns1.opendomain.dev. admin.example.com. ..."
}
```

---

### Import Zone

`POST /domains/{domain_id}/dns/import`

Import a BIND-format zone file, replacing existing records.

**Auth required**: Yes

**Request body**: `zone_file` (string) — BIND zone file contents.

**Response** (200): Updated zone object with all imported records.

---

### List Templates

`GET /domains/{domain_id}/dns/templates`

List available DNS templates.

**Auth required**: No

**Response** (200):

```json
[
  {
    "name": "github-pages",
    "description": "A records and www CNAME for GitHub Pages hosting",
    "record_count": 5,
    "params": []
  },
  {
    "name": "google-workspace",
    "description": "MX records and SPF for Google Workspace email",
    "record_count": 6,
    "params": ["verification_code"]
  }
]
```

Available templates: `github-pages`, `google-workspace`, `microsoft-365`, `vercel`, `netlify`

---

### Apply Template

`POST /domains/{domain_id}/dns/templates`

Apply a DNS template to a domain.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template` | string | Yes | Template name |
| `params` | object | No | Template parameters (e.g., `{"verification_code": "abc123"}`) |

**Response** (200): Updated zone object with template records applied.

```bash
curl -X POST http://localhost:8000/api/v1/domains/$DOMAIN_ID/dns/templates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "github-pages"}'
```

---

## Contacts

### List Contacts

`GET /contacts/`

List all WHOIS contacts for the authenticated user.

**Auth required**: Yes

**Response** (200):

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "label": "Personal",
    "first_name": "Jane",
    "last_name": "Doe",
    "organization": null,
    "email": "jane@example.com",
    "phone": "+61400000000",
    "city": "Sydney",
    "country_code": "AU",
    "created_at": "2026-09-11T00:00:00Z"
  }
]
```

---

### Create Contact

`POST /contacts/`

Create a new WHOIS contact.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Friendly name for this contact (e.g., "Personal", "Business") |
| `first_name` | string | Yes | First name |
| `last_name` | string | Yes | Last name |
| `organization` | string | No | Organization or company |
| `email` | string (email) | Yes | Contact email |
| `phone` | string | Yes | Phone number (E.164 format preferred) |
| `fax` | string | No | Fax number |
| `address_line1` | string | Yes | Street address |
| `address_line2` | string | No | Suite/unit |
| `city` | string | Yes | City |
| `state_province` | string | No | State or province |
| `postal_code` | string | Yes | Postal/ZIP code |
| `country_code` | string | Yes | ISO 3166-1 alpha-2 country code |

**Response** (201): Contact object.

```bash
curl -X POST http://localhost:8000/api/v1/contacts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Personal",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+61400000000",
    "address_line1": "123 Main St",
    "city": "Sydney",
    "postal_code": "2000",
    "country_code": "AU"
  }'
```

---

### Get Contact

`GET /contacts/{contact_id}`

**Auth required**: Yes

**Response** (200): Contact object.

---

### Update Contact

`PATCH /contacts/{contact_id}`

Update a contact. Only send fields you want to change.

**Auth required**: Yes

**Request body**: Same fields as create, all optional.

**Response** (200): Updated contact object.

---

### Delete Contact

`DELETE /contacts/{contact_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

## WHOIS

### WHOIS Lookup

`POST /whois/`

Perform a WHOIS/RDAP lookup on any domain.

**Auth required**: No

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_name` | string | Yes | Domain to look up |

**Response** (200):

```json
{
  "domain_name": "example.com",
  "registrar": "Example Registrar Inc.",
  "creation_date": "1995-08-14",
  "expiration_date": "2027-08-13",
  "updated_date": "2026-01-15",
  "nameservers": ["ns1.example.com", "ns2.example.com"],
  "status": ["clientTransferProhibited"],
  "dnssec": "unsigned"
}
```

```bash
curl -X POST http://localhost:8000/api/v1/whois/ \
  -H "Content-Type: application/json" \
  -d '{"domain_name": "google.com"}'
```

---

## Agent (AI Assistant)

### Chat

`POST /agent/chat`

Send a message to the AI agent. The agent can execute any platform action (register domains, manage DNS, etc.) through natural language.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Natural language message |
| `conversation_id` | string | No | Continue a previous conversation |

**Response** (200):

```json
{
  "response": "I've registered example.com for 2 years with privacy enabled. The domain is now active and set to auto-renew.",
  "conversation_id": "conv_abc123",
  "actions_taken": [
    {
      "tool": "register_domain",
      "input": {"domain": "example.com", "period_years": 2},
      "result": {"status": "success"}
    }
  ]
}
```

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for available domains with the keyword cloud"}'
```

---

### Chat (Streaming)

`POST /agent/chat/stream`

Same as chat but returns Server-Sent Events for real-time updates.

**Auth required**: Yes

**Request body**: Same as chat.

**Response**: `text/event-stream` with these event types:

| Event | Data | Description |
|-------|------|-------------|
| `thinking` | `{"status": "processing"}` | Agent is processing |
| `action` | Tool execution details | Agent executed a tool |
| `message` | `{"response": "...", "conversation_id": "..."}` | Final response |
| `done` | `{"conversation_id": "..."}` | Stream complete |

---

## Monitoring

### Create Domain Watch

`POST /monitoring/watches`

Watch an unavailable domain for availability changes.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_name` | string | Yes | Domain to watch |

**Response** (201): Domain watch object with `id`, `domain_name`, `status`, `created_at`.

---

### List Domain Watches

`GET /monitoring/watches`

**Auth required**: Yes

**Response** (200): Array of domain watch objects.

---

### Delete Domain Watch

`DELETE /monitoring/watches/{watch_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

### Create Uptime Check

`POST /monitoring/uptime`

Add an HTTP/HTTPS uptime monitor.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | URL to monitor (e.g., `https://example.com`) |
| `interval_seconds` | integer | No | Check interval (default: 300) |

**Response** (201): Uptime check object.

---

### List Uptime Checks

`GET /monitoring/uptime`

**Auth required**: Yes

**Response** (200): Array of uptime check objects with `id`, `url`, `status`, `last_checked`, `response_time_ms`.

---

### Delete Uptime Check

`DELETE /monitoring/uptime/{check_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

### Get SSL Monitor

`GET /monitoring/domains/{domain_id}/ssl`

Get SSL certificate monitoring status for a domain.

**Auth required**: Yes

**Response** (200): SSL monitor object with `issuer`, `valid_from`, `valid_to`, `days_remaining`, `chain_valid`.

---

### Refresh SSL Monitor

`POST /monitoring/domains/{domain_id}/ssl/refresh`

Force a fresh SSL check.

**Auth required**: Yes

**Response** (200): Updated SSL monitor object.

---

### Create Alert Rule

`POST /monitoring/alerts/rules`

Create a custom alert rule.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_type` | string | Yes | Alert type (e.g., `expiry`, `uptime_down`, `ssl_expiring`) |
| `threshold` | integer | No | Threshold value (e.g., days before expiry) |
| `domain_id` | UUID | No | Scope to a specific domain |

**Response** (201): Alert rule object.

---

### List Alert Rules

`GET /monitoring/alerts/rules`

**Auth required**: Yes

**Response** (200): Array of alert rule objects.

---

### List Alerts

`GET /monitoring/alerts`

List triggered alerts.

**Auth required**: Yes

**Query parameters**:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `limit` | integer | 50 | 1-200 | Number of alerts to return |

**Response** (200): Array of alert objects with `id`, `rule_id`, `message`, `severity`, `acknowledged`, `created_at`.

---

### Acknowledge Alert

`POST /monitoring/alerts/{alert_id}/acknowledge`

Mark an alert as acknowledged.

**Auth required**: Yes

**Response** (200):

```json
{
  "acknowledged": true
}
```

---

## Webhooks

### Create Webhook

`POST /webhooks/`

Subscribe to platform events via HTTP callbacks.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string (URL) | Yes | Endpoint to receive POST callbacks |
| `events` | string[] | Yes | Event types to subscribe to |

**Available events**: `DOMAIN_REGISTERED`, `DOMAIN_RENEWED`, `DOMAIN_EXPIRED`, `DOMAIN_TRANSFERRED`, `DOMAIN_DELETED`, `DNS_CHANGED`, `SSL_EXPIRING`, `UPTIME_DOWN`, `UPTIME_UP`

**Response** (201): Webhook object with `id`, `url`, `events`, `secret`, `is_active`, `failure_count`.

The `secret` field is returned only on creation. Use it to verify webhook signatures.

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["DOMAIN_REGISTERED", "DOMAIN_EXPIRED"]
  }'
```

---

### List Webhooks

`GET /webhooks/`

**Auth required**: Yes

**Response** (200): Array of webhook objects.

---

### Delete Webhook

`DELETE /webhooks/{webhook_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

### List Webhook Deliveries

`GET /webhooks/{webhook_id}/deliveries`

View delivery history for a webhook.

**Auth required**: Yes

**Query parameters**:

| Parameter | Type | Default | Range |
|-----------|------|---------|-------|
| `limit` | integer | 50 | 1-200 |

**Response** (200): Array of delivery objects with `id`, `event_type`, `payload`, `response_code`, `delivered_at`, `success`.

---

## Marketplace

### Create Listing

`POST /marketplace/listings`

List a domain for sale.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_id` | UUID | Yes | Domain to list |
| `price_cents` | integer | Yes | Asking price in cents |
| `description` | string | No | Listing description |
| `buy_now_enabled` | boolean | No | Allow instant purchase |

**Response** (201): Listing object with `id`, `domain_id`, `domain_name`, `price_cents`, `seller_id`, `status`, `created_at`.

```bash
curl -X POST http://localhost:8000/api/v1/marketplace/listings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain_id": "uuid-here", "price_cents": 500000}'
```

---

### Browse Listings

`GET /marketplace/listings`

Browse all active marketplace listings.

**Auth required**: No

**Query parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 25 | Items per page (max 100) |
| `sort` | string | `newest` | Sort order: `newest`, `price_asc`, `price_desc`, `name` |

**Response** (200): Array of listing objects.

---

### Get Listing

`GET /marketplace/listings/{listing_id}`

**Auth required**: No

**Response** (200): Listing object.

---

### Withdraw Listing

`DELETE /marketplace/listings/{listing_id}`

Remove a domain from the marketplace.

**Auth required**: Yes (must be the seller)

**Response**: `204 No Content`

---

### Create Offer

`POST /marketplace/listings/{listing_id}/offers`

Submit a purchase offer on a listing.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount_cents` | integer | Yes | Offer amount in cents |
| `message` | string | No | Message to the seller |

**Response** (201): Offer object with `id`, `listing_id`, `buyer_id`, `amount_cents`, `status`, `message`, `created_at`.

---

### List Offers on Listing

`GET /marketplace/listings/{listing_id}/offers`

View offers on a listing (only the seller can see all offers).

**Auth required**: Yes

**Response** (200): Array of offer objects.

---

### List My Offers

`GET /marketplace/offers/mine`

View all offers the authenticated user has made.

**Auth required**: Yes

**Response** (200): Array of offer objects.

---

### Accept Offer

`POST /marketplace/offers/{offer_id}/accept`

Accept a purchase offer (seller only).

**Auth required**: Yes

**Response** (200): `{"accepted": true}`

---

### Reject Offer

`POST /marketplace/offers/{offer_id}/reject`

Reject a purchase offer (seller only).

**Auth required**: Yes

**Response** (200): `{"rejected": true}`

---

## Email Forwarding

All email endpoints are scoped to a domain: `/domains/{domain_id}/email/...`

### Create Forward

`POST /domains/{domain_id}/email/`

Create an email forwarding rule.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_address` | string | Yes | Local part (e.g., `info`, `support`) or `*` for catch-all |
| `destination_email` | string (email) | Yes | Where to forward emails |

**Response** (201): Email forward object with `id`, `domain_id`, `source_address`, `destination_email`, `is_active`, `created_at`.

```bash
curl -X POST http://localhost:8000/api/v1/domains/$DOMAIN_ID/email/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_address": "info", "destination_email": "me@gmail.com"}'
```

---

### List Forwards

`GET /domains/{domain_id}/email/`

**Auth required**: Yes

**Response** (200): Array of email forward objects.

---

### Delete Forward

`DELETE /domains/{domain_id}/email/{forward_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

### Toggle Forward

`POST /domains/{domain_id}/email/{forward_id}/toggle`

Enable or disable an email forwarding rule.

**Auth required**: Yes

**Response** (200): Updated email forward object.

---

## SSL Certificates

### Request Certificate

`POST /ssl/certificates`

Request a new SSL/TLS certificate via Let's Encrypt.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_name` | string | Yes | Domain for the certificate |
| `san_domains` | string[] | No | Subject Alternative Names |

**Response** (201): Certificate object with `id`, `domain_name`, `status`, `issuer`, `valid_from`, `valid_to`, `auto_renew`, `created_at`.

```bash
curl -X POST http://localhost:8000/api/v1/ssl/certificates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain_name": "example.com"}'
```

---

### List Certificates

`GET /ssl/certificates`

**Auth required**: Yes

**Response** (200): Array of certificate objects.

---

### Get Certificate

`GET /ssl/certificates/{cert_id}`

**Auth required**: Yes

**Response** (200): Certificate object.

---

### Revoke Certificate

`POST /ssl/certificates/{cert_id}/revoke`

**Auth required**: Yes

**Response** (200): `{"revoked": true}`

---

### Renew Certificate

`POST /ssl/certificates/{cert_id}/renew`

Force-renew a certificate.

**Auth required**: Yes

**Response** (200): Updated certificate object with new validity dates.

---

## Bulk Operations

### Bulk Register

`POST /bulk/register`

Register multiple domains at once.

**Auth required**: Yes

**Request body**:

```json
{
  "domains": [
    {
      "domain": "example1.com",
      "registrant_contact_id": "uuid",
      "period_years": 1
    },
    {
      "domain": "example2.com",
      "registrant_contact_id": "uuid",
      "period_years": 2
    }
  ]
}
```

**Response** (201):

```json
{
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "results": [
    {"domain": "example1.com", "status": "success", "domain_id": "uuid"},
    {"domain": "example2.com", "status": "success", "domain_id": "uuid"}
  ]
}
```

---

### Bulk Renew

`POST /bulk/renew`

Renew multiple domains.

**Auth required**: Yes

**Request body**:

```json
{
  "domain_ids": ["uuid1", "uuid2"],
  "period_years": 1
}
```

**Response** (200): Bulk operation result.

---

### Bulk DNS Update

`POST /bulk/dns`

Apply a DNS change across multiple domains.

**Auth required**: Yes

**Request body**:

```json
{
  "domain_ids": ["uuid1", "uuid2"],
  "records": [
    {"record_type": "A", "name": "@", "content": "1.2.3.4"}
  ]
}
```

**Response** (200): Bulk operation result.

---

### Bulk Lock / Unlock

`POST /bulk/lock`
`POST /bulk/unlock`

Lock or unlock multiple domains.

**Auth required**: Yes

**Request body**:

```json
{
  "domain_ids": ["uuid1", "uuid2"]
}
```

**Response** (200): Bulk operation result.

---

## Billing

### List Invoices

`GET /billing/invoices`

**Auth required**: Yes

**Response** (200): Array of invoice objects with `id`, `user_id`, `status`, `total_cents`, `items`, `created_at`, `paid_at`.

---

### Get Invoice

`GET /billing/invoices/{invoice_id}`

**Auth required**: Yes

**Response** (200): Invoice object.

---

### Pay Invoice

`POST /billing/invoices/{invoice_id}/pay`

Pay an outstanding invoice using the default payment method.

**Auth required**: Yes

**Response** (200): `{"paid": true}`

---

### List Transactions

`GET /billing/transactions`

**Auth required**: Yes

**Query parameters**:

| Parameter | Type | Default | Range |
|-----------|------|---------|-------|
| `limit` | integer | 50 | 1-200 |

**Response** (200): Array of transaction objects with `id`, `user_id`, `type`, `amount_cents`, `description`, `created_at`.

---

### Add Payment Method

`POST /billing/payment-methods`

Store a new payment method.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Payment type (e.g., `card`, `paypal`) |
| `token` | string | Yes | Payment processor token |
| `label` | string | No | Display name (e.g., "Visa ending 4242") |

**Response** (201): Payment method object.

---

### List Payment Methods

`GET /billing/payment-methods`

**Auth required**: Yes

**Response** (200): Array of payment method objects with `id`, `type`, `label`, `is_default`, `created_at`.

---

### Delete Payment Method

`DELETE /billing/payment-methods/{method_id}`

**Auth required**: Yes

**Response**: `204 No Content`

---

### Set Default Payment Method

`POST /billing/payment-methods/{method_id}/default`

Set a payment method as the default for automatic payments.

**Auth required**: Yes

**Response** (200): `{"default": true}`

---

## API Keys

### Create API Key

`POST /api-keys/`

Create a new API key for programmatic access.

**Auth required**: Yes

**Request body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Descriptive name for the key |
| `scopes` | string[] | No | Permitted scopes (empty = full access) |
| `expires_in_days` | integer | No | Days until expiry (null = never) |

**Response** (201):

```json
{
  "id": "uuid",
  "name": "CI/CD Pipeline",
  "key": "od_live_abc123xyz789...",
  "prefix": "od_live_abc1",
  "scopes": [],
  "expires_at": null,
  "created_at": "2026-09-11T00:00:00Z"
}
```

The `key` field is returned **only on creation**. Store it securely — it cannot be retrieved again.

```bash
curl -X POST http://localhost:8000/api/v1/api-keys/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "CI/CD Pipeline"}'
```

---

### List API Keys

`GET /api-keys/`

**Auth required**: Yes

**Response** (200): Array of API key objects (without the full key — only `prefix` is shown).

```json
[
  {
    "id": "uuid",
    "name": "CI/CD Pipeline",
    "prefix": "od_live_abc1",
    "scopes": [],
    "last_used": "2026-09-10T12:00:00Z",
    "expires_at": null,
    "created_at": "2026-09-01T00:00:00Z"
  }
]
```

---

### Revoke API Key

`DELETE /api-keys/{key_id}`

Permanently revoke an API key.

**Auth required**: Yes

**Response**: `204 No Content`

---

## AI Agent Tools Reference

The AI agent has access to 21 tools that map to platform operations. When you send a message to the agent, it can use any combination of these tools to fulfil your request:

| Tool | Description |
|------|-------------|
| `search_domains` | Search for available domain names across TLDs |
| `register_domain` | Register a new domain |
| `list_domains` | List all owned domains |
| `get_domain_details` | Get details for a specific domain |
| `update_domain` | Update domain settings |
| `renew_domain` | Renew a domain registration |
| `manage_dns_records` | Create, update, delete, or list DNS records |
| `apply_dns_template` | Apply a pre-built DNS template |
| `whois_lookup` | Perform WHOIS lookup on any domain |
| `transfer_domain_in` | Transfer a domain from another registrar |
| `manage_contacts` | CRUD operations on WHOIS contacts |
| `export_dns_zone` | Export DNS zone as BIND file |
| `manage_monitoring` | Domain watches, uptime checks, alerts |
| `manage_webhooks` | Create and manage webhook subscriptions |
| `manage_marketplace` | List domains, browse, make offers |
| `manage_email_forwards` | Email forwarding rules |
| `manage_ssl` | SSL certificate lifecycle |
| `manage_billing` | Invoices, transactions, payment methods |
| `manage_api_keys` | API key management |
| `bulk_operations` | Batch domain operations |
| `manage_dnssec` | DNSSEC enable/disable/key rotation |
