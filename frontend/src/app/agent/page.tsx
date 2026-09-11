"use client";

import { useState } from "react";
import { Bot, Send, Clock, Sparkles, Brain, Zap, Maximize2, Minus, X } from "lucide-react";

const mockMessages = [
  {
    id: 1,
    role: "assistant",
    content: "Welcome to the OpenDomain AI Agent. I can help you search for domains, manage DNS, check WHOIS, set up monitoring, and handle transfers. What would you like to do today?",
    timestamp: "2 minutes ago",
  },
  {
    id: 2,
    role: "user",
    content: "Register opendomain.dev for 2 years with privacy protection",
    timestamp: "1 minute ago",
  },
  {
    id: 3,
    role: "assistant",
    content: "Great! I'll help you register opendomain.dev for 2 years with WHOIS privacy protection enabled. Let me check availability first... ✅ Domain is available. Price: $39.98/year ($79.96 total with privacy included). Should I proceed?",
    timestamp: "Just now",
  },
];

const quickActions = [
  { label: "Search Domains", description: "Find available domains" },
  { label: "WHOIS Lookup", description: "Check domain details" },
  { label: "DNS Configuration", description: "Set up records" },
  { label: "Transfer Domain", description: "Bring existing domains" },
  { label: "Renew Domain", description: "Extend registration" },
  { label: "Marketplace Search", description: "Find premium domains" },
];

export default function AgentPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(mockMessages);

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessage = {
      id: messages.length + 1,
      role: "user",
      content: input,
      timestamp: "Just now",
    };

    setMessages([...messages, newMessage]);
    setInput("");

    // Simulate AI response after delay
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        role: "assistant",
        content: "I received your message: \"" + input + "\". I'm processing that now...",
        timestamp: "Just now",
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const handleQuickAction = (action: string) => {
    const actionText = `Help me with ${action.toLowerCase()}`;
    setInput(actionText);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-gradient-to-br from-primary to-accent p-2.5 border border-border">
            <Bot className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground font-heading">
              AI Agent
            </h1>
            <p className="text-muted-foreground mt-1 font-body text-sm">
              Natural language control for domain management • 21 pending tasks
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Terminal Card */}
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-background via-background to-background/80 border border-border rounded-2xl p-8 shadow-xl backdrop-blur-sm">
            <div className="space-y-6">
              {/* Terminal Header */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1.5">
                  <div className="w-3 h-3 rounded-full bg-destructive"></div>
                  <div className="w-3 h-3 rounded-full bg-warning"></div>
                  <div className="w-3 h-3 rounded-full bg-success"></div>
                </div>
                <div className="flex-1 text-center">
                  <span className="font-mono text-xs text-muted-foreground">
                    AI Agent Terminal • Type commands below
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <button className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-border/50 transition-colors border border-border">
                    <Minus className="h-3 w-3" />
                  </button>
                  <button className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-border/50 transition-colors border border-border">
                    <Maximize2 className="h-3 w-3" />
                  </button>
                  <button className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-destructive/20 transition-colors border border-border">
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </div>

              {/* Terminal Body */}
              <div className="bg-[hsl(262_25%_5%)] border border-border rounded-lg font-mono text-sm">
                {/* Terminal Header */}
                <div className="flex items-center px-4 py-3 border-b border-border bg-[hsl(262_25%_8%)]">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-3.5 w-3.5 text-accent" />
                    <span className="text-accent font-medium">ai-agent@opendomain:~</span>
                  </div>
                  <div className="flex-1"></div>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>Last updated: Just now</span>
                  </div>
                </div>

                {/* Terminal Content */}
                <div className="p-4 overflow-auto max-h-[400px]">
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 font-mono text-sm ${
                            message.role === "user"
                              ? "bg-accent text-accent-foreground border border-accent/30"
                              : "bg-sidebar-background/30 border border-border"
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1.5 text-xs">
                            {message.role === "assistant" && (
                              <div className="w-1.5 h-1.5 rounded-full bg-accent"></div>
                            )}
                            <span className={`${message.role === "user" ? "text-accent-foreground/80" : "text-muted-foreground"}`}>
                              {message.role === "user" ? "❯ user@" : "❯ ai-agent@"}
                              <span className="font-semibold">opendomain</span>
                              :~$ {message.timestamp}
                            </span>
                          </div>
                          <p className={`leading-relaxed ${message.role === "user" ? "text-white" : "text-foreground"}`}>
                            {message.content}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Input Area */}
                  <div className="mt-6">
                    <div className="relative flex items-center">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
                        <span className="text-accent font-medium">❯</span>
                        <span className="text-foreground font-semibold">user@opendomain:~$</span>
                      </div>
                      <input
                        type="text"
                        placeholder="Type your command here..."
                        className="bg-sidebar-background/50 rounded-lg px-3 py-2 border border-border flex-1 ml-2 font-mono text-sm text-foreground focus:outline-none focus:border-accent/50 transition-colors"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                      />
                      <button
                        onClick={handleSend}
                        className="font-medium text-sm px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200 shadow-sm hover:shadow-md ml-2"
                      >
                        <Send className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground font-mono">
                      <Sparkles className="h-3 w-3" />
                      <span>Press Enter to execute command • Tab for suggestions</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Command Hints */}
              <div className="border border-border rounded-lg p-4 bg-background/50">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="h-4 w-4 text-warning" />
                  <span className="font-medium text-sm text-foreground">Quick Commands</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {quickActions.map((action) => (
                    <button
                      key={action.label}
                      onClick={() => handleQuickAction(action.label)}
                      className="font-medium text-sm px-3 py-2 rounded-lg border border-border hover:border-border/60 bg-background hover:bg-sidebar-background/50 transition-all duration-200 text-left font-mono text-xs"
                    >
                      <span className="text-accent">$</span> {action.label.toLowerCase()}
                      <div className="text-xs text-muted-foreground mt-0.5">{action.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="rounded-xl border border-surface-border bg-surface text-text-primary shadow-sm">
            <div className="absolute top-0 left-6 -translate-y-1/2 bg-background px-4 py-1.5 rounded-full border border-border">
              <span className="font-medium text-xs text-foreground">System Status</span>
            </div>
            <div className="p-6 pt-8">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-success"></div>
                    <span className="text-sm font-medium text-foreground">AI Agent</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-success/10 text-success">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-success"></div>
                    <span className="text-sm font-medium text-foreground">EPP Connection</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-success/10 text-success">Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-success"></div>
                    <span className="text-sm font-medium text-foreground">DNS Service</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-success/10 text-success">Running</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-warning"></div>
                    <span className="text-sm font-medium text-foreground">Database</span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-warning/10 text-warning">Moderate Load</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Tasks */}
          <div className="rounded-xl border border-surface-border bg-surface text-text-primary shadow-sm">
            <div className="absolute top-0 left-6 -translate-y-1/2 bg-background px-4 py-1.5 rounded-full border border-border">
              <span className="font-medium text-xs text-foreground">Recent Tasks</span>
            </div>
            <div className="p-6 pt-8">
              <div className="space-y-3">
                {[
                  { name: "Register opendomain.dev", status: "✅ Completed", time: "2 min ago" },
                  { name: "WHOIS lookup for cloudapp.io", status: "✅ Completed", time: "5 min ago" },
                  { name: "Renew example.com", status: "🔄 In progress", time: "Now" },
                  { name: "Setup monitoring for 5 domains", status: "⏳ Pending", time: "10 min ago" },
                ].map((task, index) => (
                  <div key={index} className="flex items-center justify-between group">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                        {task.name}
                      </div>
                      <div className="text-xs text-muted-foreground">{task.status}</div>
                    </div>
                    <div className="text-xs text-muted-foreground">{task.time}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Agent Stats */}
          <div className="rounded-xl border border-surface-border bg-surface text-text-primary shadow-sm">
            <div className="absolute top-0 left-6 -translate-y-1/2 bg-background px-4 py-1.5 rounded-full border border-border">
              <span className="font-medium text-xs text-foreground">Agent Stats</span>
            </div>
            <div className="p-6 pt-8">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">287</div>
                  <div className="text-xs text-muted-foreground">Commands Today</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-success">99.8%</div>
                  <div className="text-xs text-muted-foreground">Success Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">3.2s</div>
                  <div className="text-xs text-muted-foreground">Avg. Response Time</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent">42</div>
                  <div className="text-xs text-muted-foreground">Active Processes</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}