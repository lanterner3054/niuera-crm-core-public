# Public Architecture Overview

NIUERA CRM Core is a lightweight CRM automation system for EV charging infrastructure export workflows.

Public architecture:

- Feishu Bitable: business data source
- n8n: workflow automation
- Dify: AI workflows and email generation
- MCP server: read-only operational context bridge for controlled internal use
- GitHub: source control and AI handoff documentation

This public repository intentionally excludes production identifiers, credentials, customer records, and private workflow exports.
