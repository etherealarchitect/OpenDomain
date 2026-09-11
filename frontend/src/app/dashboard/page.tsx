"use client";

import { Globe, Server, Wallet, Eye, MessageSquare, ArrowUpRight, Cpu, Shield, Terminal, TrendingUp, AlertCircle } from "lucide-react";

const stats = [
  { label: "Active Domains", value: "21", change: "+3 this month", icon: Globe, trend: "up" },
  { label: "DNS Zones", value: "8", change: "+2 this month", icon: Server, trend: "up" },
  { label: "Monthly Spend", value: "$149.00", change: "-$12.00", icon: Wallet, trend: "down" },
  { label: "Uptime", value: "99.8%", change: "+0.2%", icon: Eye, trend: "up" },
];

const recentActivity = [
  { id: 1, action: "Registered opendomain.dev", time: "2 hours ago", user: "Scott", type: "success" },
  { id: 2, action: "Updated DNS records for example.com", time: "4 hours ago", user: "AI Agent", type: "info" },
  { id: 3, action: "Renewed cloudapp.io for 1 year", time: "1 day ago", user: "Scott", type: "success" },
  { id: 4, action: "Transfer pending: web3tools.org", time: "2 days ago", user: "AI Agent", type: "warning" },
];

const agentSuggestions = [
  { id: 1, text: "Register opendomain.dev for 2 years with WHOIS privacy enabled", priority: "high" },
  { id: 2, text: "Set up email forwarding for all domains to main inbox", priority: "medium" },
  { id: 3, text: "Create DNS template for new SaaS projects", priority: "low" },
  { id: 4, text: "Monitor SSL certificate expiration for 5 critical domains", priority: "high" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI-powered domain management • Last updated 12 minutes ago
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 rounded-lg border border-border bg-background hover:bg-sidebar-background/50 transition-colors text-sm font-medium">
            Export Report
          </button>
          <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-sm font-medium shadow-sm">
            AI Assistant
          </button>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="relative bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-xl p-5 hover:border-primary/30 transition-colors group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-sm text-muted-foreground font-medium">{stat.label}</div>
                  <div className="text-2xl font-bold text-foreground mt-2">{stat.value}</div>
                  <div className="flex items-center gap-1 mt-2">
                    {stat.trend === "up" ? (
                      <TrendingUp className="h-3.5 w-3.5 text-green-500" />
                    ) : (
                      <TrendingUp className="h-3.5 w-3.5 rotate-180 text-red-500" />
                    )}
                    <span className={`text-xs font-medium ${stat.trend === "up" ? "text-green-500" : "text-red-500"}`}>
                      {stat.change}
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <div className="absolute -inset-2 bg-gradient-to-r from-primary/10 to-accent/10 blur-lg opacity-0 group-hover:opacityPre-100 transition-opacity"></div>
                  <div className="relative h-10 w-10 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-heading font-bold text-foreground">Quick Actions</h2>
              <span className="text-xs font-mono px-2 py-1 rounded-lg border border-border bg-sidebar-background/50 text-muted-foreground">
                ⌘K to open
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { title: "WHOIS Lookup", desc: "Check domain availability", icon: Globe },
                { title: "Add Domain", desc: "Register or transfer", icon: Globe },
                { title: "DNS Zone", desc: "Create new zone", icon: Server },
                { title: "SSL Cert", desc: "Generate certificate", icon: Shield },
              ].map((action) => (
                <button
                  key={action.title}
                  className="group flex items-center justify-between rounded-lg border border-border p-4 text-left hover:border-primary/30 hover:bg-sidebar-background/30 transition-all duration-200"
                >
                  <div>
                    <div className="font-medium text-foreground">{action.title}</div>
                    <div className="text-xs text-muted-foreground mt-1">{action.desc}</div>
                  </div>
                  <div className="relative">
                    <div className="absolute -inset-2 bg-gradient-to-r from-primary/10 to-accent/10 blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <action.icon className="relative h-5 w-5 text-primary group-hover:text-accent transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Agent Suggestions */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-6">
              <MessageSquare className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-heading font-bold text-foreground">Agent Suggestions</h2>
            </div>
            <div className="space-y-4">
              {agentSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="group rounded-lg border border-border p-4 hover:border-primary/30 hover:bg-sidebar-background/30 transition-all duration-200 cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="text-sm text-foreground leading-relaxed">{suggestion.text}</div>
                    <div className={`h-2 w-2 rounded-full mt-1 ${
                      suggestion.priority === "high" ? "bg-red-500" :
                      suggestion.priority === "medium" ? "bg-yellow-500" :
                      "bg-green-500"
                    }`}></div>
                  </div>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-muted-foreground">Ask AI Agent →</span>
                    <span className="text-xs font-mono px-2 py-1 rounded-lg border border-border bg-sidebar-background/50">
                      {suggestion.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity & Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-heading font-bold text-foreground">Recent Activity</h2>
              <span className="text-xs font-mono px-2 py-1 rounded-lg border border-border bg-sidebar-background/50 text-muted-foreground">
                Live feed
              </span>
            </div>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between border-b border-border/30 pb-4 last:border-0 last:pb-0 group"
                >
                  <div className="flex items-center gap-3">
                    <div className={`relative h-8 w-8 rounded-lg flex items-center justify-center ${
                      activity.type === "success" ? "bg-green-500/10" :
                      activity.type === "warning" ? "bg-yellow-500/10" :
                      "bg-blue-500/10"
                    }`}>
                      {activity.type === "success" && <div className="h-2 w-2 rounded-full bg-green-500"></div>}
                      {activity.type === "warning" && <div className="h-2 w-2 rounded-full bg-yellow-500"></div>}
                      {activity.type === "info" && <div className="h-2 w-2 rounded-full bg-blue-500"></div>}
                    </div>
                    <div>
                      <div className="font-medium text-foreground">{activity.action}</div>
                      <div className="text-xs text-muted-foreground">by {activity.user}</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                    {activity.time}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-6">
              <Cpu className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-heading font-bold text-foreground">System Status</h2>
            </div>
            <div className="space-y-4">
              {[
                { service: "API Backend", status: "operational", uptime: "99.9%" },
                { service: "DNS Resolver", status: "operational", uptime: "99.8%" },
                { service: "Database", status: "operational", uptime: "100%" },
                { service: "Redis Cache", status: "degraded", uptime: "98.5%" },
              ].map((service) => (
                <div key={service.service} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-2 w-2 rounded-full ${
                      service.status === "operational" ? "bg-green-500" :
                      service.status === "degraded" ? "bg-yellow-500" :
                      "bg-red-500"
                    }`}></div>
                    <div>
                      <div className="text-sm font-medium text-foreground">{service.service}</div>
                      <div className="text-xs text-muted-foreground">{service.status}</div>
                    </div>
                  </div>
                  <div className="text-sm font-mono text-muted-foreground">{service.uptime}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}