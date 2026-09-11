"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Globe, Server, Wallet, Eye, MessageSquare, ArrowUpRight } from "lucide-react";

const stats = [
  { label: "Active Domains", value: "21", change: "+3 this month", icon: Globe },
  { label: "DNS Zones", value: "8", change: "+2 this month", icon: Server },
  { label: "Monthly Spend", value: "$149.00", change: "-$12.00 vs last", icon: Wallet },
  { label: "Uptime", value: "99.8%", change: "+0.2%", icon: Eye },
];

const recentActivity = [
  { id: 1, action: "Registered opendomain.dev", time: "2 hours ago", user: "Scott" },
  { id: 2, action: "Updated DNS records for example.com", time: "4 hours ago", user: "AI Agent" },
  { id: 3, action: "Renewed cloudapp.io for 1 year", time: "1 day ago", user: "Scott" },
  { id: 4, action: "Transferred web3tools.org inbound", time: "2 days ago", user: "AI Agent" },
];

const agentSuggestions = [
  "Register opendomain.dev for 2 years with WHOIS privacy enabled",
  "Set up email forwarding for all my domains to my main inbox",
  "Create a DNS template for new SaaS projects with A, MX, TXT records",
  "Monitor SSL certificate expiration for 5 critical domains",
  "Find available .ai domains related to 'machine learning'",
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Welcome back, Scott</h1>
        <p className="text-text-tertiary mt-1">
          Your domain management dashboard • Last updated 12 minutes ago
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="hover:border-primary-400/30 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-text-tertiary">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    <p className="text-xs text-text-tertiary mt-1">{stat.change}</p>
                  </div>
                  <div className="rounded-lg bg-primary-500/10 p-2">
                    <Icon className="h-5 w-5 text-primary-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Quick actions */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            <button className="flex items-center justify-between rounded-lg border border-surface-border p-4 text-left hover:border-primary-400/30 hover:bg-surface-raised transition-colors">
              <div>
                <div className="font-medium">WHOIS Lookup</div>
                <div className="text-xs text-text-tertiary mt-1">Check domain availability</div>
              </div>
              <ArrowUpRight className="h-4 w-4 text-text-tertiary" />
            </button>
            <button className="flex items-center justify-between rounded-lg border border-surface-border p1-4 text-left hover:border-primary-400/30 hover:bg-surface-raised transition-colors">
              <div>
                <div className="font-medium">Add Domain</div>
                <div className="text-xs text-text-tertiary mt-1">Register or transfer</div>
              </div>
              <ArrowUpRight className="h-4 w-4 text-text-tertiary" />
            </button>
            <button className="flex items-center justify-between rounded-lg border border-surface-border p-4 text-left hover:border-primary-400/30 hover:bg-surface-raised transition-colors">
              <div>
                <div className="font-medium">DNS Zone</div>
                <div className="text-xs text-text-tertiary mt-1">Create new zone</div>
              </div>
              <ArrowUpRight className="h-4 w-4 text-text-tertiary" />
            </button>
            <button className="flex items-center justify-between rounded-lg border border-surface-border p-4 text-left hover:border-primary-400/30 hover:bg-surface-raised transition-colors">
              <div>
                <div className="font-medium">Invoice</div>
                <div className="text-xs text-text-tertiary mt-1">View recent bills</div>
              </div>
              <ArrowUpRight className="h-4 w-4 text-text-tertiary" />
            </button>
          </CardContent>
        </Card>

        {/* AI Agent suggestions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              AI Agent Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {agentSuggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-surface-border p-3 hover:border-primary-400/30 hover:bg-surface-raised transition-colors cursor-pointer"
                >
                  <div className="text-sm">{suggestion}</div>
                  <div className="text-xs text-primary-400 mt-2 font-medium">Ask Agent →</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between border-b border-surface-border pb-4 last:border-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary-500/10 flex items-center justify-center">
                    <div className="h-2 w-2 rounded-full bg-primary-400" />
                  </div>
                  <div>
                    <div className="font-medium">{activity.action}</div>
                    <div className="text-xs text-text-tertiary">by {activity.user}</div>
                  </div>
                </div>
                <div className="text-sm text-text-tertiary">{activity.time}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}