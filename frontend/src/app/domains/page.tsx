"use client";

import { useState } from "react";
import { Globe, Calendar, Lock, ArrowUpRight, Plus, Search, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Domains</h1>
          <p className="text-text-tertiary mt-1">
            Manage your domain portfolio • {domains.length} domains
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 px-4 py-2.5 text-sm font-medium text-white hover:from-primary-700 hover:to-primary-900 transition-colors">
          <Plus className="h-4 w-4" />
          Add Domain
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="hover:border-primary-400/30 transition-colors">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-tertiary">Total Domains</p>
                <p className="text-2xl font-bold mt-1">{domains.length}</p>
              </div>
              <div className="rounded-lg bg-primary-500/10 p-2">
                <Globe className="h-5 w-5 text-primary-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary-400/30 transition-colors">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-tertiary">Expiring Soon</p>
                <p className="text-2xl font-bold mt-1">1</p>
              </div>
              <div className="rounded-lg bg-orange-500/10 p-2">
                <Calendar className="h-5 w-5 text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary-400/30 transition-colors">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-tertiary">Privacy Protected</p>
                <p className="text-2xl font-bold mt-1">4</p>
              </div>
              <div className="rounded-lg bg-green-500/10 p-2">
                <Lock className="h-5 w-5 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary-400/30 transition-colors">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-tertiary">Monthly Spend</p>
                <p className="text-2xl font-bold mt-1">$49.85</p>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-2">
                <div className="text-blue-400 text-lg font-bold">$</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
              <input
                type="search"
                placeholder="Search domains..."
                className="w-full rounded-md border border-surface-border bg-surface-raised py-2 pl-9 pr-4 text-sm placeholder:text-text-tertiary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setFilter("all")}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  filter === "all"
                    ? "bg-primary-600 text-white"
                    : "text-text-secondary hover:bg-surface-raised"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter("active")}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  filter === "active"
                    ? "bg-primary-600 text-white"
                    : "text-text-secondary hover:bg-surface-raised"
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setFilter("expiring")}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  filter === "expiring"
                    ? "bg-orange-600 text-white"
                    : "text-text-secondary hover:bg-surface-raised"
                }`}
              >
                Expiring
              </button>
              <button
                onClick={() => setFilter("transfer")}
                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  filter === "transfer"
                    ? "bg-purple-600 text-white"
                    : "text-text-secondary hover:bg-surface-raised"
                }`}
              >
                Transfers
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Domain table */}
      <Card>
        <CardHeader>
          <CardTitle>Domain List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-border">
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Domain</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Status</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Expires</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Registrar</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">DNS</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Privacy</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary">Renewal</th>
                  <th className="py-3 text-left text-sm font-medium text-text-tertiary"></th>
                </tr>
              </thead>
              <tbody>
                {filteredDomains.map((domain) => (
                  <tr key={domain.id} className="border-b border-surface-border last:border-0 hover:bg-surface-raised/50 transition-colors">
                    <td className="py-4">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-primary-500/10 flex items-center justify-center">
                          <Globe className="h-4 w-4 text-primary-400" />
                        </div>
                        <div>
                          <div className="font-medium">{domain.name}</div>
                          <div className="text-xs text-text-tertiary">ID: {domain.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        domain.status === "Active"
                          ? "bg-green-500/10 text-green-400"
                          : domain.status === "Expiring Soon"
                          ? "bg-orange-500/10 text-orange-400"
                          : "bg-purple-500/10 text-purple-400"
                      }`}>
                        {domain.status}
                      </span>
                    </td>
                    <td className="py-4 text-sm">{domain.expires}</td>
                    <td className="py-4 text-sm">{domain.registrar}</td>
                    <td className="py-4">
                      <span className={`text-xs font-medium ${
                        domain.dns === "Managed"
                          ? "text-primary-400"
                          : "text-text-tertiary"
                      }`}>
                        {domain.dns}
                      </span>
                    </td>
                    <td className="py-4">
                      {domain.privacy ? (
                        <div className="inline-flex items-center gap-1 rounded-full bg-green-500/10 px-2.5 py-0.5 text-xs font-medium text-green-400">
                          <Lock className="h-2 w-2" /> On
                        </div>
                      ) : (
                        <span className="text-xs text-text-tertiary">Off</span>
                      )}
                    </td>
                    <td className="py-4 text-sm font-medium">{domain.renewal}</td>
                    <td className="py-4">
                      <button className="text-text-tertiary hover:text-primary-400 transition-colors">
                        <ArrowUpRight className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}