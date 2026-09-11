const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  company: string | null;
  phone: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  two_factor_enabled: boolean;
  onboarding_state: "email_verification_required" | "mfa_enrollment_required" | "complete";
  created_at: string;
}

export interface AuthChallengeResponse {
  challenge_id: string;
  next_step: "mfa" | "mfa_enrollment";
  expires_in_seconds: number;
}

export interface MfaEnrollmentResponse extends AuthChallengeResponse {
  qr_data_uri: string;
  secret: string;
}

export interface MfaVerificationResponse {
  user: UserResponse;
  backup_codes: string[] | null;
}

class ApiClient {
  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
      method,
      headers,
      credentials: "include",
      body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new ApiError(
        typeof data.detail === "string" ? data.detail : `Request failed: ${res.status}`,
        res.status,
      );
    }
    if (res.status === 204) return {} as T;
    return res.json() as Promise<T>;
  }

  get<T>(path: string) { return this.request<T>("GET", path); }
  post<T>(path: string, body?: unknown) { return this.request<T>("POST", path, body); }
  patch<T>(path: string, body?: unknown) { return this.request<T>("PATCH", path, body); }
  delete<T>(path: string) { return this.request<T>("DELETE", path); }

  register(email: string, password: string, fullName: string) {
    return this.post<{ message: string; email: string; verification_required: boolean }>("/auth/register", {
      email, password, full_name: fullName,
    });
  }
  login(email: string, password: string) {
    return this.post<AuthChallengeResponse>("/auth/login", { email, password });
  }
  verifyEmail(token: string) {
    return this.post<AuthChallengeResponse>("/auth/verify-email", { token });
  }
  resendVerification(email: string) {
    return this.post<{ message: string }>("/auth/resend-verification", { email });
  }
  startMfaEnrollment(challengeId: string) {
    return this.post<MfaEnrollmentResponse>("/auth/mfa/enrollment", { challenge_id: challengeId });
  }
  verifyMfa(challengeId: string, code: string) {
    return this.post<MfaVerificationResponse>("/auth/mfa/verify", { challenge_id: challengeId, code });
  }
  forgotPassword(email: string) { return this.post<{ message: string }>("/auth/forgot-password", { email }); }
  resetPassword(token: string, newPassword: string) {
    return this.post<{ message: string }>("/auth/reset-password", { token, new_password: newPassword });
  }
  getCurrentUser() { return this.get<UserResponse>("/auth/me"); }
  updateCurrentUser(data: Partial<Pick<UserResponse, "full_name" | "company" | "phone">>) {
    return this.patch<UserResponse>("/auth/me", data);
  }
  changePassword(currentPassword: string, newPassword: string) {
    return this.post<void>("/auth/change-password", { current_password: currentPassword, new_password: newPassword });
  }
  logout() { return this.post<void>("/auth/logout"); }

  // Domains
  searchDomains(query: string, tlds?: string[]) { return this.post<DomainSearchResult[]>("/domains/search", { query, tlds }); }
  listDomains(status?: string) { return this.get<DomainResponse[]>(`/domains/${status ? `?status=${status}` : ""}`); }
  getDomain(id: string) { return this.get<DomainResponse>(`/domains/${id}`); }
  registerDomain(data: RegisterDomainRequest) { return this.post<DomainResponse>("/domains/register", data); }
  updateDomain(id: string, data: UpdateDomainRequest) { return this.patch<DomainResponse>(`/domains/${id}`, data); }
  renewDomain(id: string, years: number) { return this.post<DomainResponse>(`/domains/${id}/renew`, { period_years: years }); }
  lockDomain(id: string) { return this.post<DomainResponse>(`/domains/${id}/lock`); }
  unlockDomain(id: string) { return this.post<DomainResponse>(`/domains/${id}/unlock`); }
  getAuthCode(id: string) { return this.get<{ auth_code: string }>(`/domains/${id}/auth-code`); }
  deleteDomain(id: string) { return this.delete(`/domains/${id}`); }
  transferDomainIn(data: TransferInRequest) { return this.post<DomainTransferResponse>("/domains/transfer", data); }

  // DNS
  getDnsZone(domainId: string) { return this.get<DnsZoneResponse>(`/domains/${domainId}/dns/`); }
  createDnsRecord(domainId: string, data: DnsRecordCreate) { return this.post<DnsRecordResponse>(`/domains/${domainId}/dns/records`, data); }
  updateDnsRecord(domainId: string, recordId: string, data: DnsRecordUpdate) { return this.patch<DnsRecordResponse>(`/domains/${domainId}/dns/records/${recordId}`, data); }
  deleteDnsRecord(domainId: string, recordId: string) { return this.delete(`/domains/${domainId}/dns/records/${recordId}`); }
  getDnsTemplates(domainId: string) { return this.get<DnsTemplate[]>(`/domains/${domainId}/dns/templates`); }
  applyDnsTemplate(domainId: string, template: string, params?: Record<string, string>) { return this.post<DnsZoneResponse>(`/domains/${domainId}/dns/templates`, { template, params: params ?? {} }); }

  // Contacts
  listContacts() { return this.get<ContactResponse[]>("/contacts/"); }
  createContact(data: ContactCreate) { return this.post<ContactResponse>("/contacts/", data); }
  updateContact(id: string, data: Partial<ContactCreate>) { return this.patch<ContactResponse>(`/contacts/${id}`, data); }
  deleteContact(id: string) { return this.delete(`/contacts/${id}`); }

  // AI and lookup
  agentChat(message: string, conversationId?: string) { return this.post<AgentResponse>("/agent/chat", { message, conversation_id: conversationId }); }
  whoisLookup(domainName: string) { return this.post<WhoisResult>("/whois/", { domain_name: domainName }); }

  // Monitoring
  listAlerts() { return this.get<AlertResponse[]>("/monitoring/alerts"); }
  acknowledgeAlert(id: string) { return this.post<{ acknowledged: boolean }>(`/monitoring/alerts/${id}/acknowledge`); }
  listUptimeChecks() { return this.get<UptimeCheckResponse[]>("/monitoring/uptime"); }
  createUptimeCheck(data: { domain_id: string; url: string; check_interval_seconds?: number }) { return this.post<UptimeCheckResponse>("/monitoring/uptime", data); }
  deleteUptimeCheck(id: string) { return this.delete(`/monitoring/uptime/${id}`); }
  listDomainWatches() { return this.get<DomainWatchResponse[]>("/monitoring/watches"); }
  createDomainWatch(domainName: string) { return this.post<DomainWatchResponse>("/monitoring/watches", { domain_name: domainName }); }
  deleteDomainWatch(id: string) { return this.delete(`/monitoring/watches/${id}`); }

  // Marketplace
  browseListings() { return this.get<MarketplaceListingResponse[]>("/marketplace/listings"); }
  createListing(data: { domain_id: string; asking_price_cents: number; description?: string }) { return this.post<MarketplaceListingResponse>("/marketplace/listings", data); }
  createOffer(listingId: string, amountCents: number, message?: string) { return this.post<OfferResponse>(`/marketplace/listings/${listingId}/offers`, { amount_cents: amountCents, message }); }
  withdrawListing(id: string) { return this.delete(`/marketplace/listings/${id}`); }

  // Billing
  listInvoices() { return this.get<InvoiceResponse[]>("/billing/invoices"); }
  listTransactions() { return this.get<TransactionResponse[]>("/billing/transactions"); }
  listPaymentMethods() { return this.get<PaymentMethodResponse[]>("/billing/payment-methods"); }
  payInvoice(id: string) { return this.post<{ paid: boolean }>(`/billing/invoices/${id}/pay`); }

  // Webhooks and API keys
  listWebhooks() { return this.get<WebhookResponse[]>("/webhooks/"); }
  createWebhook(url: string, events: string[]) { return this.post<WebhookResponse>("/webhooks/", { url, events }); }
  deleteWebhook(id: string) { return this.delete(`/webhooks/${id}`); }
  listApiKeys() { return this.get<ApiKeyResponse[]>("/api-keys/"); }
  createApiKey(name: string, scopes?: string[]) { return this.post<ApiKeyCreatedResponse>("/api-keys/", { name, scopes }); }
  revokeApiKey(id: string) { return this.delete(`/api-keys/${id}`); }
}

export const api = new ApiClient();

export interface DomainSearchResult { domain: string; available: boolean; price_cents: number | null; premium: boolean; }
export interface RegisterDomainRequest { domain: string; period_years: number; registrant_contact_id: string; nameservers?: string[]; privacy_enabled?: boolean; auto_renew?: boolean; }
export interface UpdateDomainRequest { nameservers?: string[]; auto_renew?: boolean; privacy_enabled?: boolean; locked?: boolean; registrant_contact_id?: string; }
export interface DomainResponse { id: string; name: string; tld: string; status: string; owner_id: string; auto_renew: boolean; privacy_enabled: boolean; locked: boolean; nameservers: string | null; registration_date: string; expiry_date: string; last_renewed: string | null; price_cents: number; renewal_price_cents: number; created_at: string; }
export interface TransferInRequest { domain: string; auth_code: string; registrant_contact_id: string; }
export interface DomainTransferResponse { id: string; domain_id: string; status: string; initiated_at: string; completed_at: string | null; }
export interface DnsRecordCreate { record_type: string; name: string; content: string; ttl?: number; priority?: number; proxied?: boolean; comment?: string; }
export interface DnsRecordUpdate { name?: string; content?: string; ttl?: number; priority?: number; proxied?: boolean; comment?: string; enabled?: boolean; }
export interface DnsRecordResponse { id: string; zone_id: string; record_type: string; name: string; content: string; ttl: number; priority: number | null; proxied: boolean; enabled: boolean; comment: string | null; created_at: string; updated_at: string; }
export interface DnsZoneResponse { id: string; domain_id: string; zone_name: string; primary_ns: string; serial: number; default_ttl: number; dnssec_enabled: boolean; records: DnsRecordResponse[]; created_at: string; updated_at: string; }
export interface DnsTemplate { name: string; description: string; record_count: number; params: string[]; }
export interface ContactCreate { label: string; first_name: string; last_name: string; organization?: string; email: string; phone: string; fax?: string; address_line1: string; address_line2?: string; city: string; state_province?: string; postal_code: string; country_code: string; }
export interface ContactResponse { id: string; user_id: string; label: string; first_name: string; last_name: string; organization: string | null; email: string; phone: string; city: string; country_code: string; created_at: string; }
export interface AgentResponse { response: string; conversation_id: string; actions_taken?: Array<Record<string, unknown>>; }
export interface WhoisResult { domain_name: string; registrar: string | null; creation_date: string | null; expiration_date: string | null; updated_date: string | null; nameservers: string[]; status: string[]; dnssec: string | null; }
export interface DomainWatchResponse { id: string; domain_name: string; is_available: boolean; active: boolean; last_checked: string | null; created_at: string; }
export interface UptimeCheckResponse { id: string; domain_id: string; url: string; check_interval_seconds: number; status: string; last_checked: string | null; response_time_ms: number | null; active: boolean; created_at: string; }
export interface AlertResponse { id: string; title: string; message: string; alert_type: string; status: string; domain_id: string | null; created_at: string; acknowledged_at: string | null; }
export interface MarketplaceListingResponse { id: string; domain_id: string; domain_name: string; asking_price_cents: number; currency: string; description: string | null; status: string; featured: boolean; created_at: string; }
export interface OfferResponse { id: string; listing_id: string; buyer_id: string; amount_cents: number; currency: string; message: string | null; status: string; created_at: string; }
export interface InvoiceResponse { id: string; invoice_number: string; status: string; subtotal_cents: number; tax_cents: number; total_cents: number; currency: string; due_date: string | null; paid_at: string | null; created_at: string; }
export interface TransactionResponse { id: string; transaction_type: string; amount_cents: number; currency: string; description: string; created_at: string; }
export interface PaymentMethodResponse { id: string; method_type: string; last_four: string | null; label: string; is_default: boolean; created_at: string; }
export interface WebhookResponse { id: string; url: string; events: string; active: boolean; failure_count: number; created_at: string; }
export interface ApiKeyResponse { id: string; name: string; prefix: string; scopes: string | null; last_used: string | null; expires_at: string | null; created_at: string; }
export interface ApiKeyCreatedResponse extends ApiKeyResponse { key: string; }
