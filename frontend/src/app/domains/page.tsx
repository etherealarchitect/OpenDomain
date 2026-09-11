"use client";

import { useState } from "react";
import { Globe, Calendar, Lock, ArrowUpRight, Plus, Search } from "lucide-react";

const domains = [
  {
    id: 1,
    name: "opendomain.dev",
    status: "Active",
    expires: "2026-12-15",
    registrar: "OpenSRS",
    dns: "Managed",
    privacy: true,
    renewal: "$19.99",
  },
  {
    id: 2,
    name: "cloudapp.io",
    status: "Active",
    expires: "2027-03-22",
    registrar: "Cloudflare",
    dns: "Managed",
    privacy: true,
    renewal: "$89.00",
  },
  {
    id: 3,
    name: "example.com",
    status: "Active",
    expires: "2026-11-30",
    registrar: "OpenSRS",
    dns: "External",
    privacy: false,
    renewal: "$14.99",
  },
  {
    id: 4,
    name: "web3tools.org",
    status: "Pending Transfer",
    expires: "2027-08-10",
    registrar: "GoDaddy",
    dns: "Managed",
    privacy: true,
    renewal: "$18.50",
  },
  {
    id: 5,
    name: "saasplatform.ai",
    status: "Active",
    expires: "2028-01-05",
    registrar: "OpenSRS",
    dns: "Managed",
    privacy: true,
    renewal: "$249.00",
  },
  {
    id: 6,
    name: "testlab.xyz",
    status: "Expiring Soon",
    expires: "2026-10-01",
    registrar: "Namecheap",
    dns: "External",
    privacy: false,
    renewal: "$9.99",
  },
];

export default function DomainsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<string>("all");

  const filteredDomains = domains.filter((domain) => {
    const matchesSearch = domain.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filter === "all" ||
      (filter === "active" && domain.status === "Active") ||
      (filter === "expiring" && domain.status === "Expiring Soon") ||
      (filter === "transfer" && domain.status === "Pending Transfer");

    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-success/10 text-success";
      case "Expiring Soon":
        return "bg-warning/10 text-warning";
      case "Pending Transfer":
        return "bg-accent/10 text-accent";
      default:
        return "bg-border/10 text-foreground";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-foreground font-heading">
            Domains
          </h1>
          <p className="text-muted-foreground text-sm font-body">
            Manage your domain portfolio • {domains.length} domains
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-br from-primary to-accent px-4 py-2.5 text-sm font-medium text-primary-foreground hover:from-primary/90 hover:to-accent/90 transition-colors shadow-base44 hover:shadow-base44-lg pressable">
          <Plus className="h-4 w-4" />
          Add Domain
        </button>
      </div>

      {/* Stats Cards with Base44 cards.default */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-6 shadow-base44 hover-shadow-base44-lg transition-shadow hover-lift">
          <div className="flex items-center justify-between space-y-1">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground font-body">
                Total Domains
              </p>
              <p className="text-2xl font-bold text-foreground font-heading">
                {domains.length}
              </p>
            </div>
            <div className="rounded-lg bg-primary/10 p-2">
              <Globe className="h-5 w-5 text-primary" />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 shadow-base44 hover-shadow-base44-lg transition-shadow hover-lift">
          <div className="flex items-center justify-between space-y-1">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground font-body">
                Expiring Soon
              </p>
              <p className="text-2xl font-bold text-foreground font-heading">
                1
              </p>
            </div>
            <div className="rounded-lg bg-warning/10 p-2">
              <Calendar className="h-5 w-5 text-warning" />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 shadow-base44 hover-shadow-base44-lg transition-shadow hover-lift">
          <div className="flex items-center justify-between space-y-1">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground font-body">
                Privacy Protected
              </p>
              <p className="text-2xl font-bold text-foreground font-heading">
                4
              </p>
            </div>
            <div className="rounded-lg bg-success/10 p-2">
              <Lock className="h-5 w-5 text-success" />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 shadow-base44 hover-shadow-base44-lg transition-shadow hover-lift">
          <div className="flex items-center justify-between space-y-1">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground font-body">
                Monthly Spend
              </p>
              <p className="text-2xl font-bold text-foreground font-heading">
                $49.85
              </p>
            </div>
            <div className="rounded-lg bg-primary/10 p-2">
              <div className="text-primary text-lg font-bold">$</div>
            </div>
          </div>
        </div>
      </div>

      {/* Terminal-style Search Interface */}
      <div className="terminal rounded-2xl border border-border shadow-base44-lg backdrop-blur-sm">
        {/* Terminal Header */}
        <div className="terminal-header">
          <div className="flex gap-2">
            <div className="terminal-dot bg-destructive"></div>
            <div className="terminal-dot bg-warning"></div>
            <div className="terminal-dot bg-success"></div>
          </div>
          <div className="ml-4 font-mono text-xs text-muted-foreground">
            domain-search — bash
          </div>
        </div>

        {/* Terminal Body */}
        <div className="terminal-content p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <span className="text-success font-mono">$</span>
            <div className="flex-1 flex items-center bg-sidebar/50 rounded-lg px-4 py-3 border border-border">
              <Search className="h-4 w-4 text-muted-foreground mr-3" />
              <input
                type="search"
                placeholder="grep 'opendomain' | filter:all"
                className="w-full bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none font-mono text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-2 flex-wrap items-center">
            <button
              onClick={() => setFilter("all")}
              className={`font-medium text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 font-mono ${
                filter === "all"
                  ? "bg-gradient-to-r from-primary/10 to-accent/5 border border-primary/20 text-primary shadow-sm"
                  : "border border-border text-foreground hover:border-border/60 hover:bg-sidebar/50 pressable"
              }`}
            >
              --all
            </button>
            <button
              onClick={() => setFilter("active")}
              className={`font-medium text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 font-mono ${
                filter === "active"
                  ? "bg-gradient-to-r from-primary/10 to-accent/5 border border-primary/20 text-primary shadow-sm"
                  : "border border-border text-foreground hover:border-border/60 hover:bg-sidebar/50 pressable"
              }`}
            >
              --active
            </button>
            <button
              onClick={() => setFilter("expiring")}
              className={`font-medium text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 font-mono ${
                filter === "expiring"
                  ? "bg-gradient-to-r from-warning/10 to-warning/5 border border-warning/20 text-warning shadow-sm"
                  : "border border-border text-foreground hover:border-border/60 hover:bg-sidebar/50 pressable"
              }`}
            >
              --expiring
            </button>
            <button
              onClick={() => setFilter("transfer")}
              className={`font-medium text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 font-mono ${
                filter === "transfer"
                  ? "bg-gradient-to-r from-accent/10 to-accent/5 border border-accent/20 text-accent shadow-sm"
                  : "border border-border text-foreground hover:border-border/60 hover:bg-sidebar/50 pressable"
              }`}
            >
              --transfer
            </button>
            <span className="text-muted-foreground font-mono text-sm ml-auto">
              {filteredDomains.length} domains found
            </span>
          </div>
        </div>
      </div>

      {/* Domain Cards using Base44 cards.default */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground font-heading">
            Domain List
          </h2>
          <div className="text-sm text-muted-foreground font-body">
            Showing {filteredDomains.length} of {domains.length} domains
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card overflow-hidden shadow-base44">
          {/* Table Header */}
          <div className="grid grid-cols-8 border-b border-border p-6 bg-muted/50 font-body">
            <div className="text-sm font-medium text-muted-foreground">Domain</div>
            <div className="text-sm font-medium text-muted-foreground">Status</div>
            <div className="text-sm font-medium text-muted-foreground">Expires</div>
            <div className="text-sm font-medium text-muted-foreground">Registrar</div>
            <div className="text-sm font-medium text-muted-foreground">DNS</div>
            <div className="text-sm font-medium text-muted-foreground">Privacy</div>
            <div className="text-sm font-medium text-muted-foreground">Renewal</div>
            <div className="text-sm font-medium text-muted-foreground"></div>
          </div>

          {/* Domain Rows */}
          <div className="divide-y divide-border">
            {filteredDomains.map((domain) => (
              <div
                key={domain.id}
                className="grid grid-cols-8 p-6 hover:bg-muted/30 transition-colors font-body"
              >
                <div className="flex items-center gap-4">
                  <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Globe className="h-4 w-4 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <div className="font-medium text-foreground">{domain.name}</div>
                    <div className="text-xs text-muted-foreground">ID: {domain.id}</div>
                  </div>
                </div>
                <div>
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${getStatusColor(domain.status)}`}>
                    {domain.status}
                  </span>
                </div>
                <div className="text-sm text-foreground">{domain.expires}</div>
                <div className="text-sm text-foreground">{domain.registrar}</div>
                <div>
                  <span className={`text-xs font-medium ${domain.dns === "Managed" ? "text-primary" : "text-muted-foreground"}`}>
                    {domain.dns}
                  </span>
                </div>
                <div>
                  {domain.privacy ? (
                    <div className="inline-flex items-center gap-1.5 rounded-full bg-success/10 px-3 py-1 text-xs font-medium text-success">
                      <Lock className="h-2.5 w-2.5" /> On
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">Off</span>
                  )}
                </div>
                <div className="text-sm font-medium text-foreground">{domain.renewal}</div>
                <div>
                  <button className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-border/50 transition-colors border border-border pressable">
                    <ArrowUpRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}