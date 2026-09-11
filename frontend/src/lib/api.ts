const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("opendomain_token", token);
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("opendomain_token");
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("opendomain_token");
    }
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/api/v1${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401) {
      this.clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error("Session expired. Please sign in again.");
    }

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || `Request failed: ${res.status}`);
    }

    if (res.status === 204) return {} as T;
    return res.json();
  }

  get<T>(path: string) {
    return this.request<T>("GET", path);
  }
  post<T>(path: string, body?: unknown) {
    return this.request<T>("POST", path, body);
  }
  patch<T>(path: string, body?: unknown) {
    return this.request<T>("PATCH", path, body);
  }
  delete<T>(path: string) {
    return this.request<T>("DELETE", path);
  }

  // Auth
  async login(email: string, password: string) {
    const data = await this.post<{ access_token: string }>("/auth/login", {
      email,
      password,
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(email: string, password: string, fullName: string) {
    return this.post("/auth/register", {
      email,
      password,
      full_name: fullName,
    });
  }

  // Domains
  searchDomains(query: string, tlds?: string[]) {
    return this.post<DomainSearchResult[]>("/domains/search", { query, tlds });
  }

  listDomains(status?: string) {
    const qs = status ? `?status=${status}` : "";
    return this.get<DomainResponse[]>(`/domains/${qs}`);
  }

  getDomain(id: string) {
    return this.get<DomainResponse>(`/domains/${id}`);
  }

  registerDomain(data: RegisterDomainRequest) {
    return this.post<DomainResponse>("/domains/register", data);
  }

  updateDomain(id: string, data: UpdateDomainRequest) {
    return this.patch<DomainResponse>(`/domains/${id}`, data);
  }

  renewDomain(id: string, years: number) {
    return this.post<DomainResponse>(`/domains/${id}/renew`, {
      period_years: years,
    });
  }

  lockDomain(id: string) {
    return this.post<DomainResponse>(`/domains/${id}/lock`);
  }

  unlockDomain(id: string) {
    return this.post<DomainResponse>(`/domains/${id}/unlock`);
  }

  getAuthCode(id: string) {
    return this.get<{ auth_code: string }>(`/domains/${id}/auth-code`);
  }

  deleteDomain(id: string) {
    return this.delete(`/domains/${id}`);
  }

  transferDomainIn(data: TransferInRequest) {
    return this.post<DomainTransferResponse>("/domains/transfer", data);
  }

  // DNS
  getDnsZone(domainId: string) {
    return this.get<DnsZoneResponse>(`/domains/${domainId}/dns/`);
  }

  createDnsRecord(domainId: string, data: DnsRecordCreate) {
    return this.post<DnsRecordResponse>(
      `/domains/${domainId}/dns/records`,
      data,
    );
  }

  updateDnsRecord(domainId: string, recordId: string, data: DnsRecordUpdate) {
    return this.patch<DnsRecordResponse>(
      `/domains/${domainId}/dns/records/${recordId}`,
      data,
    );
  }

  deleteDnsRecord(domainId: string, recordId: string) {
    return this.delete(`/domains/${domainId}/dns/records/${recordId}`);
  }

  bulkCreateDnsRecords(domainId: string, records: DnsRecordCreate[]) {
    return this.post<DnsRecordResponse[]>(
      `/domains/${domainId}/dns/records/bulk`,
      { records },
    );
  }

  exportDnsZone(domainId: string) {
    return this.get<{ zone_name: string; zone_file: string }>(
      `/domains/${domainId}/dns/export`,
    );
  }

  applyDnsTemplate(
    domainId: string,
    template: string,
    params?: Record<string, string>,
  ) {
    return this.post<DnsZoneResponse>(`/domains/${domainId}/dns/templates`, {
      template,
      params,
    });
  }

  // Contacts
  listContacts() {
    return this.get<ContactResponse[]>("/contacts/");
  }

  createContact(data: ContactCreate) {
    return this.post<ContactResponse>("/contacts/", data);
  }

  getContact(id: string) {
    return this.get<ContactResponse>(`/contacts/${id}`);
  }

  updateContact(id: string, data: Partial<ContactCreate>) {
    return this.patch<ContactResponse>(`/contacts/${id}`, data);
  }

  deleteContact(id: string) {
    return this.delete(`/contacts/${id}`);
  }

  // Agent
  agentChat(message: string, conversationId?: string) {
    return this.post<AgentResponse>("/agent/chat", {
      message,
      conversation_id: conversationId,
    });
  }

  // User/Account
  getMe() {
    return this.get<UserResponse>("/auth/me");
  }

  updateMe(data: { full_name?: string; company?: string; phone?: string }) {
    return this.patch<UserResponse>("/auth/me", data);
  }

  changePassword(currentPassword: string, newPassword: string) {
    return this.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  // DNS Templates
  getDnsTemplates(domainId: string) {
    return this.get<DnsTemplate[]>(`/domains/${domainId}/dns/templates`);
  }

  // WHOIS
  whoisLookup(domain: string) {
    return this.post<WhoisResult>("/whois/", { domain_name: domain });
  }

  // Monitoring
  listDomainWatches() { return this.get<DomainWatchResponse[]>("/monitoring/watches"); }
  createDomainWatch(query: string, notifyEmail?: string) {
    return this.post<DomainWatchResponse>("/monitoring/watches", { query, notify_email: notifyEmail });
  }
  deleteDomainWatch(id: string) { return this.delete(`/monitoring/watches/${id}`); }
  listUptimeChecks() { return this.get<UptimeCheckResponse[]>("/monitoring/uptime"); }
  createUptimeCheck(domainId: string, url: string) {
    return this.post<UptimeCheckResponse>("/monitoring/uptime", { domain_id: domainId, url });
  }
  deleteUptimeCheck(id: string) { return this.delete(`/monitoring/uptime/${id}`); }
  getSslMonitor(domainId: string) { return this.get<SslMonitorResponse>(`/monitoring/domains/${domainId}/ssl`); }
  listAlertRules() { return this.get<AlertRuleResponse[]>("/monitoring/alerts/rules"); }
  createAlertRule(data: { domain_id?: string; alert_type: string; threshold_days?: number; webhook_url?: string; email?: string }) {
    return this.post<AlertRuleResponse>("/monitoring/alerts/rules", data);
  }
  listAlerts(limit = 50) { return this.get<AlertResponse[]>(`/monitoring/alerts?limit=${limit}`); }
  acknowledgeAlert(id: string) { return this.post(`/monitoring/alerts/${id}/acknowledge`); }

  // Webhooks
  listWebhooks() { return this.get<WebhookResponse[]>("/webhooks/"); }
  createWebhook(url: string, events: string[]) {
    return this.post<WebhookResponse>("/webhooks/", { url, events });
  }
  deleteWebhook(id: string) { return this.delete(`/webhooks/${id}`); }
  listWebhookDeliveries(webhookId: string) {
    return this.get<WebhookDeliveryResponse[]>(`/webhooks/${webhookId}/deliveries`);
  }

  // Marketplace
  listMarketplaceListings(page = 1) {
    return this.get<MarketplaceListingResponse[]>(`/marketplace/listings?page=${page}`);
  }
  getMarketplaceListing(id: string) { return this.get<MarketplaceListingResponse>(`/marketplace/listings/${id}`); }
  createListing(domainId: string, askingPriceCents: number, description?: string) {
    return this.post<MarketplaceListingResponse>("/marketplace/listings", { domain_id: domainId, asking_price_cents: askingPriceCents, description });
  }
  withdrawListing(id: string) { return this.delete(`/marketplace/listings/${id}`); }
  createOffer(listingId: string, amountCents: number, message?: string) {
    return this.post<OfferResponse>(`/marketplace/listings/${listingId}/offers`, { listing_id: listingId, amount_cents: amountCents, message });
  }
  listMyOffers() { return this.get<OfferResponse[]>("/marketplace/offers/mine"); }

  // Email Forwarding
  listEmailForwards(domainId: string) { return this.get<EmailForwardResponse[]>(`/domains/${domainId}/email/`); }
  createEmailForward(domainId: string, source: string, destination: string) {
    return this.post<EmailForwardResponse>(`/domains/${domainId}/email/`, { domain_id: domainId, source_address: source, destination_email: destination });
  }
  deleteEmailForward(domainId: string, forwardId: string) { return this.delete(`/domains/${domainId}/email/${forwardId}`); }

  // SSL Certificates
  listCertificates() { return this.get<SslCertificateResponse[]>("/ssl/certificates"); }
  requestCertificate(domainId: string, domainNames?: string[]) {
    return this.post<SslCertificateResponse>("/ssl/certificates", { domain_id: domainId, domain_names: domainNames });
  }
  revokeCertificate(id: string) { return this.post(`/ssl/certificates/${id}/revoke`); }

  // Billing
  listInvoices() { return this.get<InvoiceResponse[]>("/billing/invoices"); }
  getInvoice(id: string) { return this.get<InvoiceResponse>(`/billing/invoices/${id}`); }
  listTransactions() { return this.get<TransactionResponse[]>("/billing/transactions"); }
  listPaymentMethods() { return this.get<PaymentMethodResponse[]>("/billing/payment-methods"); }

  // API Keys
  listApiKeys() { return this.get<ApiKeyResponse[]>("/api-keys/"); }
  createApiKey(name: string, scopes?: string[]) {
    return this.post<ApiKeyCreatedResponse>("/api-keys/", { name, scopes });
  }
  revokeApiKey(id: string) { return this.delete(`/api-keys/${id}`); }

  // Bulk
  bulkRegister(domains: { domain: string; period_years?: number; contact_id: string }[]) {
    return this.post<BulkActionResponse>("/bulk/register", { domains });
  }
  bulkRenew(domainIds: string[], years = 1) {
    return this.post<BulkActionResponse>("/bulk/renew", { domain_ids: domainIds, years });
  }
}

export const api = new ApiClient();

// Types
export interface DomainSearchResult {
  domain: string;
  available: boolean;
  price_cents: number | null;
  premium: boolean;
}

export interface DomainResponse {
  id: string;
  name: string;
  tld: string;
  status: string;
  owner_id: string;
  auto_renew: boolean;
  privacy_enabled: boolean;
  locked: boolean;
  nameservers: string | null;
  registration_date: string;
  expiry_date: string;
  last_renewed: string | null;
  price_cents: number;
  renewal_price_cents: number;
  created_at: string;
}

export interface RegisterDomainRequest {
  domain: string;
  period_years?: number;
  registrant_contact_id: string;
  nameservers?: string[];
  privacy_enabled?: boolean;
  auto_renew?: boolean;
}

export interface UpdateDomainRequest {
  nameservers?: string[];
  auto_renew?: boolean;
  privacy_enabled?: boolean;
  locked?: boolean;
}

export interface TransferInRequest {
  domain: string;
  auth_code: string;
  registrant_contact_id: string;
}

export interface DomainTransferResponse {
  id: string;
  domain_id: string;
  from_registrar: string | null;
  to_registrar: string | null;
  status: string;
  initiated_at: string;
  completed_at: string | null;
}

export interface DnsZoneResponse {
  id: string;
  domain_id: string;
  zone_name: string;
  primary_ns: string;
  serial: number;
  default_ttl: number;
  dnssec_enabled: boolean;
  records: DnsRecordResponse[];
  created_at: string;
  updated_at: string;
}

export interface DnsRecordResponse {
  id: string;
  zone_id: string;
  record_type: string;
  name: string;
  content: string;
  ttl: number;
  priority: number | null;
  proxied: boolean;
  enabled: boolean;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface DnsRecordCreate {
  record_type: string;
  name: string;
  content: string;
  ttl?: number;
  priority?: number;
  comment?: string;
}

export interface DnsRecordUpdate {
  content?: string;
  ttl?: number;
  priority?: number;
  enabled?: boolean;
  comment?: string;
}

export interface ContactResponse {
  id: string;
  user_id: string;
  label: string;
  first_name: string;
  last_name: string;
  organization: string | null;
  email: string;
  phone: string;
  city: string;
  country_code: string;
  created_at: string;
}

export interface ContactCreate {
  label: string;
  first_name: string;
  last_name: string;
  organization?: string;
  email: string;
  phone: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state_province?: string;
  postal_code: string;
  country_code: string;
}

export interface AgentResponse {
  response: string;
  conversation_id: string;
  actions_taken: { tool: string; input: unknown; success: boolean }[] | null;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  company: string | null;
  phone: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface DnsTemplate {
  name: string;
  description: string;
  record_count: number;
  params: string[];
}

export interface WhoisResult { domain_name: string; registrar: string | null; creation_date: string | null; expiration_date: string | null; nameservers: string[]; status: string[]; }
export interface DomainWatchResponse { id: string; domain_name: string; is_available: boolean; last_checked: string | null; active: boolean; created_at: string; }
export interface UptimeCheckResponse { id: string; domain_id: string; url: string; status: string; last_checked: string | null; response_time_ms: number | null; active: boolean; created_at: string; }
export interface SslMonitorResponse { id: string; domain_id: string; issuer: string | null; valid_from: string | null; valid_until: string | null; last_checked: string | null; auto_renew: boolean; created_at: string; }
export interface AlertRuleResponse { id: string; alert_type: string; domain_id: string | null; threshold_days: number | null; webhook_url: string | null; email: string | null; active: boolean; created_at: string; }
export interface AlertResponse { id: string; alert_type: string; status: string; title: string; message: string; domain_id: string | null; created_at: string; acknowledged_at: string | null; }
export interface WebhookResponse { id: string; url: string; events: string; active: boolean; last_triggered: string | null; failure_count: number; created_at: string; }
export interface WebhookDeliveryResponse { id: string; webhook_id: string; event_type: string; response_status: number | null; success: boolean; attempted_at: string; }
export interface MarketplaceListingResponse { id: string; domain_id: string; seller_id: string; asking_price_cents: number; currency: string; description: string | null; status: string; views: number; created_at: string; domain_name?: string; }
export interface OfferResponse { id: string; listing_id: string; buyer_id: string; amount_cents: number; currency: string; message: string | null; status: string; created_at: string; }
export interface EmailForwardResponse { id: string; domain_id: string; source_address: string; destination_email: string; active: boolean; created_at: string; }
export interface SslCertificateResponse { id: string; domain_id: string; provider: string; status: string; domain_names: string; issued_at: string | null; expires_at: string | null; auto_renew: boolean; created_at: string; }
export interface InvoiceResponse { id: string; invoice_number: string; status: string; total_cents: number; currency: string; due_date: string | null; paid_at: string | null; created_at: string; }
export interface TransactionResponse { id: string; transaction_type: string; amount_cents: number; currency: string; description: string; created_at: string; }
export interface PaymentMethodResponse { id: string; method_type: string; label: string; last_four: string | null; is_default: boolean; created_at: string; }
export interface ApiKeyResponse { id: string; name: string; prefix: string; scopes: string | null; last_used: string | null; expires_at: string | null; active: boolean; created_at: string; }
export interface ApiKeyCreatedResponse extends ApiKeyResponse { key: string; }
export interface BulkActionResponse { total: number; succeeded: number; failed: number; results: { item: string; success: boolean; error?: string }[]; }
