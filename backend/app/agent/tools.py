"""
Tool definitions for the OpenDomain AI agent.

Each tool maps to a platform action the agent can execute on behalf of the user.
Tools are defined as JSON schemas for Claude's tool-use API.
"""

TOOLS = [
    {
        "name": "search_domains",
        "description": "Search for available domain names. Checks availability across multiple TLDs and returns pricing. Use when the user wants to find or check domain availability.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The domain name or keyword to search for (e.g., 'myproject' or 'myproject.com')",
                },
                "tlds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of TLDs to check (e.g., ['com', 'io', 'dev']). Defaults to popular TLDs.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "register_domain",
        "description": "Register a new domain name. Requires a domain name and contact information. Use when the user wants to purchase/register a domain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Full domain name to register (e.g., 'example.com')"},
                "period_years": {"type": "integer", "description": "Registration period in years (1-10)", "default": 1},
                "contact_id": {"type": "string", "description": "UUID of the registrant contact to use"},
                "privacy_enabled": {"type": "boolean", "description": "Enable WHOIS privacy", "default": True},
                "auto_renew": {"type": "boolean", "description": "Enable auto-renewal", "default": True},
            },
            "required": ["domain", "contact_id"],
        },
    },
    {
        "name": "list_domains",
        "description": "List all domains owned by the current user. Returns domain names, statuses, and expiry dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "expired", "pendingTransfer", "suspended"],
                    "description": "Filter by domain status",
                },
            },
        },
    },
    {
        "name": "get_domain_details",
        "description": "Get detailed information about a specific domain including DNS, contacts, and configuration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "The domain name to look up"},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "update_domain",
        "description": "Update domain settings like nameservers, auto-renew, privacy, or transfer lock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "The domain name to update"},
                "nameservers": {"type": "array", "items": {"type": "string"}, "description": "New nameserver list"},
                "auto_renew": {"type": "boolean", "description": "Enable or disable auto-renewal"},
                "privacy_enabled": {"type": "boolean", "description": "Enable or disable WHOIS privacy"},
                "locked": {"type": "boolean", "description": "Enable or disable transfer lock"},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "renew_domain",
        "description": "Renew a domain registration for additional years.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "The domain name to renew"},
                "years": {"type": "integer", "description": "Number of years to renew for (1-10)", "default": 1},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "manage_dns_records",
        "description": "Create, update, or delete DNS records for a domain. Supports A, AAAA, CNAME, MX, TXT, NS, SRV, and CAA records.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "The domain name to manage DNS for"},
                "action": {
                    "type": "string",
                    "enum": ["create", "update", "delete", "list"],
                    "description": "The DNS action to perform",
                },
                "record_type": {
                    "type": "string",
                    "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"],
                    "description": "DNS record type",
                },
                "name": {"type": "string", "description": "Record name (e.g., '@' for root, 'www', 'mail')"},
                "content": {"type": "string", "description": "Record content/value"},
                "ttl": {"type": "integer", "description": "Time to live in seconds", "default": 3600},
                "priority": {"type": "integer", "description": "Priority (for MX and SRV records)"},
                "record_id": {"type": "string", "description": "UUID of existing record (for update/delete)"},
            },
            "required": ["domain_name", "action"],
        },
    },
    {
        "name": "apply_dns_template",
        "description": "Apply a pre-built DNS template for common services like GitHub Pages, Google Workspace, Vercel, Netlify, or Microsoft 365.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "The domain to apply the template to"},
                "template": {
                    "type": "string",
                    "enum": ["github-pages", "google-workspace", "microsoft-365", "vercel", "netlify"],
                    "description": "Template name to apply",
                },
                "params": {
                    "type": "object",
                    "description": "Template parameters (e.g., {'user': 'myname'} for GitHub Pages)",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["domain_name", "template"],
        },
    },
    {
        "name": "whois_lookup",
        "description": "Perform a WHOIS/RDAP lookup on any domain to see registration details, registrar, expiry, and nameservers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "Domain name to look up"},
            },
            "required": ["domain_name"],
        },
    },
    {
        "name": "transfer_domain_in",
        "description": "Initiate a domain transfer into OpenDomain from another registrar. Requires the domain's authorization/EPP code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "Domain name to transfer"},
                "auth_code": {"type": "string", "description": "Authorization/EPP code from the current registrar"},
                "contact_id": {"type": "string", "description": "UUID of the registrant contact"},
            },
            "required": ["domain_name", "auth_code", "contact_id"],
        },
    },
    {
        "name": "manage_contacts",
        "description": "Create, update, list, or delete WHOIS contacts used for domain registration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "update", "list", "delete"],
                    "description": "Contact action to perform",
                },
                "contact_id": {"type": "string", "description": "UUID of existing contact (for update/delete)"},
                "label": {"type": "string", "description": "Friendly name for the contact"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "organization": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "address_line1": {"type": "string"},
                "city": {"type": "string"},
                "state_province": {"type": "string"},
                "postal_code": {"type": "string"},
                "country_code": {"type": "string", "description": "Two-letter country code (e.g., 'US', 'AU')"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "export_dns_zone",
        "description": "Export a domain's DNS zone as a BIND-format zone file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string", "description": "Domain name to export"},
            },
            "required": ["domain_name"],
        },
    },
]
