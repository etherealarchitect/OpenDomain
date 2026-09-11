"""
Tool definitions for the OpenDomain AI agent.

Each tool maps to a platform action the agent can execute on behalf of the user.
Tools are defined as JSON schemas for Claude's tool-use API.
"""

TOOLS = [
    {
        "name": "search_domains",
        "description": "Search for available domain names. Checks availability across multiple TLDs and returns pricing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Domain name or keyword to search"},
                "tlds": {"type": "array", "items": {"type": "string"}, "description": "Optional TLDs to check"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "register_domain",
        "description": "Register a new domain name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Full domain name to register"},
                "period_years": {"type": "integer", "description": "Registration period in years (1-10)", "default": 1},
                "contact_id": {"type": "string", "description": "UUID of the registrant contact"},
                "privacy_enabled": {"type": "boolean", "default": True},
                "auto_renew": {"type": "boolean", "default": True},
            },
            "required": ["domain", "contact_id"],
        },
    },
    {
        "name": "list_domains",
        "description": "List all domains owned by the current user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "expired", "pendingTransfer", "suspended"]},
            },
        },
    },
    {
        "name": "get_domain_details",
        "description": "Get detailed information about a specific domain.",
        "input_schema": {
            "type": "object",
            "properties": {"domain_name": {"type": "string"}},
            "required": ["domain_name"],
        },
    },
    {
        "name": "update_domain",
        "description": "Update domain settings like nameservers, auto-renew, privacy, or transfer lock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "nameservers": {"type": "array", "items": {"type": "string"}},
                "auto_renew": {"type": "boolean"},
                "privacy_enabled": {"type": "boolean"},
                "locked": {"type": "boolean"},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "renew_domain",
        "description": "Renew a domain registration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "years": {"type": "integer", "default": 1},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "manage_dns_records",
        "description": "Create, update, delete, or list DNS records for a domain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "action": {"type": "string", "enum": ["create", "update", "delete", "list"]},
                "record_type": {"type": "string", "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"]},
                "name": {"type": "string"},
                "content": {"type": "string"},
                "ttl": {"type": "integer", "default": 3600},
                "priority": {"type": "integer"},
                "record_id": {"type": "string"},
            },
            "required": ["domain_name", "action"],
        },
    },
    {
        "name": "apply_dns_template",
        "description": "Apply a DNS template for services like GitHub Pages, Google Workspace, Vercel, Netlify, or Microsoft 365.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "template": {"type": "string", "enum": ["github-pages", "google-workspace", "microsoft-365", "vercel", "netlify"]},
                "params": {"type": "object", "additionalProperties": {"type": "string"}},
            },
            "required": ["domain_name", "template"],
        },
    },
    {
        "name": "whois_lookup",
        "description": "Perform a WHOIS/RDAP lookup on any domain.",
        "input_schema": {
            "type": "object",
            "properties": {"domain_name": {"type": "string"}},
            "required": ["domain_name"],
        },
    },
    {
        "name": "transfer_domain_in",
        "description": "Initiate a domain transfer into OpenDomain from another registrar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "auth_code": {"type": "string"},
                "contact_id": {"type": "string"},
            },
            "required": ["domain_name", "auth_code", "contact_id"],
        },
    },
    {
        "name": "manage_contacts",
        "description": "Create, update, list, or delete WHOIS contacts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "update", "list", "delete"]},
                "contact_id": {"type": "string"},
                "label": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "organization": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "address_line1": {"type": "string"},
                "city": {"type": "string"},
                "state_province": {"type": "string"},
                "postal_code": {"type": "string"},
                "country_code": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "export_dns_zone",
        "description": "Export a domain's DNS zone as a BIND-format zone file.",
        "input_schema": {
            "type": "object",
            "properties": {"domain_name": {"type": "string"}},
            "required": ["domain_name"],
        },
    },
    {
        "name": "manage_monitoring",
        "description": "Manage domain monitoring: expiry alerts, uptime checks, domain availability watches, SSL certificate tracking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create_watch", "list_watches", "create_uptime", "list_uptime", "list_alerts", "acknowledge_alert"]},
                "domain_name": {"type": "string", "description": "Domain to monitor/watch"},
                "url": {"type": "string", "description": "URL for uptime check"},
                "alert_id": {"type": "string", "description": "Alert ID to acknowledge"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_webhooks",
        "description": "Create, list, or delete webhook endpoints for event notifications.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "delete"]},
                "url": {"type": "string", "description": "Webhook endpoint URL"},
                "events": {"type": "array", "items": {"type": "string"}, "description": "Event types to subscribe to"},
                "webhook_id": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_marketplace",
        "description": "List domains for sale, browse listings, make offers, manage offers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["browse", "create_listing", "my_listings", "make_offer", "my_offers"]},
                "domain_name": {"type": "string", "description": "Domain to list for sale"},
                "price_cents": {"type": "integer", "description": "Asking price in cents"},
                "listing_id": {"type": "string"},
                "offer_amount_cents": {"type": "integer"},
                "message": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_email_forwards",
        "description": "Create, list, or delete email forwarding rules for a domain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "delete"]},
                "domain_name": {"type": "string"},
                "source_address": {"type": "string", "description": "Local part of email (e.g., 'info') or '*' for catch-all"},
                "destination_email": {"type": "string"},
                "forward_id": {"type": "string"},
            },
            "required": ["action", "domain_name"],
        },
    },
    {
        "name": "manage_ssl",
        "description": "Request, list, revoke, or renew SSL/TLS certificates via Let's Encrypt.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["request", "list", "revoke", "renew"]},
                "domain_name": {"type": "string"},
                "cert_id": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_billing",
        "description": "View invoices, transactions, and payment methods.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list_invoices", "list_transactions", "list_payment_methods"]},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_api_keys",
        "description": "Create, list, or revoke API keys for programmatic access.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "revoke"]},
                "name": {"type": "string", "description": "Key name (for create)"},
                "scopes": {"type": "array", "items": {"type": "string"}},
                "key_id": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "bulk_operations",
        "description": "Perform bulk operations: register multiple domains, bulk renew, bulk DNS update, bulk lock/unlock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["register", "renew", "lock", "unlock"]},
                "domains": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of domain objects for bulk register [{domain, contact_id, period_years}]",
                },
                "domain_names": {"type": "array", "items": {"type": "string"}, "description": "Domain names for bulk renew/lock/unlock"},
                "years": {"type": "integer", "default": 1},
            },
            "required": ["action"],
        },
    },
    {
        "name": "manage_dnssec",
        "description": "Enable, disable, or manage DNSSEC for a domain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["enable", "disable", "get_ds", "rotate_keys"]},
                "domain_name": {"type": "string"},
                "algorithm": {"type": "string", "default": "ECDSAP256SHA256"},
            },
            "required": ["action", "domain_name"],
        },
    },
]
