export function registerN8nTools(server) {
  server.tool(
    "n8n_placeholder",
    "Public sanitized placeholder tool. Production implementation is intentionally excluded.",
    {},
    async () => {
      return {
        content: [
          {
            type: "text",
            text: "This is a public sanitized placeholder. Production tool implementation is not included."
          }
        ]
      };
    }
  );
}
