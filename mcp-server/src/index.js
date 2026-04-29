import express from 'express';
import crypto from 'crypto';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { registerN8nTools } from './tools/n8n.js';
import { registerFileTools } from './tools/files.js';
import { registerDifyTools } from './tools/dify.js';
import { registerDockerTools } from './tools/docker.js';
import { registerFeishuTools } from './tools/feishu.js';
import { registerSystemTools } from './tools/system.js';

const PORT = process.env.MCP_PORT || 3001;
const API_TOKEN = process.env.MCP_API_TOKEN || '';

function createServer() {
  const server = new McpServer({
    name: 'niuera-mcp',
    version: '1.0.0',
    description: 'NIUERA CRM System MCP Server',
  });
  registerN8nTools(server);
  registerFileTools(server);
  registerDifyTools(server);
  registerDockerTools(server);
  registerFeishuTools(server);
  registerSystemTools(server);
  return server;
}

const app = express();
app.use(express.json());

const transports = {};

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', server: 'niuera-mcp', version: '1.0.0' });
});

// MCP POST endpoint
app.post('/mcp', async (req, res) => {
  try {
    const sessionId = req.headers['mcp-session-id'];
    const body = req.body;

    const isInitialize = Array.isArray(body)
      ? body.some(msg => msg.method === 'initialize')
      : body.method === 'initialize';

    if (isInitialize && !sessionId) {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => crypto.randomUUID(),
        onsessioninitialized: (sid) => {
          transports[sid] = transport;
          console.log('[MCP] Session created:', sid);
        },
      });

      transport.onclose = () => {
        const sid = transport.sessionId;
        if (sid && transports[sid]) {
          delete transports[sid];
          console.log('[MCP] Session closed:', sid);
        }
      };

      const server = createServer();
      await server.connect(transport);
      await transport.handleRequest(req, res, body);
      return;
    }

    if (sessionId && transports[sessionId]) {
      await transports[sessionId].handleRequest(req, res, body);
      return;
    }

    res.status(400).json({
      jsonrpc: '2.0',
      error: { code: -32000, message: 'Bad Request: No valid session' },
      id: null,
    });
  } catch (err) {
    console.error('[MCP] Error:', err);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: '2.0',
        error: { code: -32603, message: 'Internal error' },
        id: null,
      });
    }
  }
});

// MCP GET endpoint (SSE stream for server-to-client notifications)
app.get('/mcp', async (req, res) => {
  const sessionId = req.headers['mcp-session-id'];
  if (sessionId && transports[sessionId]) {
    await transports[sessionId].handleRequest(req, res);
    return;
  }
  res.status(400).json({ error: 'Missing session ID' });
});

// MCP DELETE endpoint (session termination)
app.delete('/mcp', async (req, res) => {
  const sessionId = req.headers['mcp-session-id'];
  if (sessionId && transports[sessionId]) {
    await transports[sessionId].handleRequest(req, res);
    delete transports[sessionId];
    return;
  }
  res.status(404).send('Session not found');
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[NIUERA MCP Server] Running on http://127.0.0.1:${PORT}/mcp`);
  console.log(`[NIUERA MCP Server] Health check: http://127.0.0.1:${PORT}/health`);
});

process.on('SIGINT', () => {
  console.log('[MCP] Shutting down...');
  Object.values(transports).forEach(t => t.close?.());
  process.exit(0);
});
