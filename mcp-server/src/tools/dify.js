export function registerDifyTools(server) {
  server.tool(
    "dify_placeholder",
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
