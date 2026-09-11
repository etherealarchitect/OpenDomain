"use client";

import { useState } from "react";
import { Bot, Send, Clock, Sparkles, Brain, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 p-2">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">AI Agent</h1>
            <p className="text-text-tertiary mt-1">
              Natural language control for domain management • 21 pending tasks
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Chat area */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Conversation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-xl p-4 ${
                      message.role === "user"
                        ? "bg-primary-600 text-white"
                        : "bg-surface-raised border border-surface-border"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {message.role === "assistant" && (
                        <Bot className="h-3 w-3" />
                      )}
                      <span className="text-xs opacity-70">
                        {message.role === "user" ? "You" : "AI Agent"} • {message.timestamp}
                      </span>
                    </div>
                    <p>{message.content}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="mt-6">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Ask the AI agent to do anything domain-related..."
                  className="w-full rounded-xl border border-surface-border bg-surface-raised py-3 pl-4 pr-12 text-sm placeholder:text-text-tertiary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                />
                <button
                  onClick={handleSend}
                  className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 hover:from-primary-700 hover:to-primary-900 transition-colors"
                >
                  <Send className="h-4 w-4 text-white" />
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2 text-xs text-text-tertiary">
                <Sparkles className="h-3 w-3" />
                <span>Press Enter to send, Shift+Enter for new line</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Side panel */}
        <div className="space-y-6">
          {/* Quick actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action) => (
                  <button
                    key={action.label}
                    onClick={() => handleQuickAction(action.label)}
                    className="rounded-lg border border-surface-border p-3 text-left hover:border-primary-400/30 hover:bg-surface-raised transition-colors"
                  >
                    <div className="font-medium text-sm">{action.label}</div>
                    <div className="text-xs text-text-tertiary mt-1">{action.description}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent tasks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Recent Tasks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "Register opendomain.dev", status: "✅ Completed" },
                  { name: "WHOIS lookup for cloudapp.io", status: "✅ Completed" },
                  { name: "Renew example.com", status: "🔄 In progress" },
                  { name: "Setup monitoring for 5 domains", status: "⏳ Pending" },
                ].map((task, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium">{task.name}</div>
                      <div className="text-xs text-text-tertiary">{task.status}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}