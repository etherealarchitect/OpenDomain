complete -x -c opendomain -n __fish_use_subcommand -a login -d "Authenticate with OpenDomain API"
complete -x -c opendomain -n __fish_use_subcommand -a logout -d "Clear authentication"
complete -x -c opendomain -n __fish_use_subcommand -a version -d "Show version information"
complete -x -c opendomain -n __fish_use_subcommand -a domains -d "Manage domains"
complete -x -c opendomain -n __fish_use_subcommand -a dns -d "Manage DNS records"
complete -x -c opendomain -n __fish_use_subcommand -a contacts -d "Manage WHOIS contacts"
complete -x -c opendomain -n __fish_use_subcommand -a whois -d "WHOIS lookup"
complete -x -c opendomain -n __fish_use_subcommand -a agent -d "AI agent chat"
complete -x -c opendomain -n __fish_use_subcommand -a transfer -d "Domain transfer operations"
complete -x -c opendomain -n __fish_use_subcommand -a marketplace -d "Domain marketplace"
complete -x -c opendomain -n __fish_use_subcommand -a monitoring -d "Monitoring and alerts"
complete -x -c opendomain -n __fish_use_subcommand -a billing -d "Billing and payments"
complete -x -c opendomain -n __fish_use_subcommand -a api-keys -d "API key management"

# Global options
complete -x -c opendomain -l api -d "API base URL"
complete -x -c opendomain -l debug -d "Enable debug output"
complete -x -c opendomain -l version -d "Show version"
complete -x -c opendomain -l help -d "Show help"

# Login options
complete -x -c opendomain -n '__fish_seen_subcommand_from login' -l email -d "Email address"
complete -x -c opendomain -n '__fish_seen_subcommand_from login' -l password -d "Password"
complete -x -c opendomain -n '__fish_seen_subcommand_from login' -l 2fa -d "2FA code"

# Domain subcommands
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a search -d "Search for available domains"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a list -d "List your domains"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a register -d "Register a domain"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a info -d "Get domain details"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a renew -d "Renew a domain"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a lock -d "Lock domain transfers"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a unlock -d "Unlock domain transfers"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a delete -d "Delete a domain"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a transfer -d "Transfer a domain"
complete -x -c opendomain -n '__fish_seen_subcommand_from domains' -a auth-codes -d "Get transfer auth codes"

# DNS subcommands
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a list -d "List DNS records"
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a add -d "Add DNS record"
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a delete -d "Delete DNS record"
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a export -d "Export DNS zone file"
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a template -d "Apply DNS template"
complete -x -c opendomain -n '__fish_seen_subcommand_from dns' -a import -d "Import DNS zone"