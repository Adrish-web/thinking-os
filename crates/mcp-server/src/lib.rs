use storage::Database;
use serde_json::{json, Value};
use std::io::{self, BufRead, Write};

pub struct McpServer<'a> {
    db: &'a Database,
}

impl<'a> McpServer<'a> {
    pub fn new(db: &'a Database) -> Self {
        Self { db }
    }

    pub fn start_listening(&self) {
        let stdin = io::stdin();
        let mut stdout = io::stdout();

        for line in stdin.lock().lines() {
            let line = match line {
                Ok(l) => l,
                Err(_) => break,
            };

            if let Ok(req) = serde_json::from_str::<Value>(&line) {
                if let Some(id) = req.get("id") {
                    let method = req.get("method").and_then(|m| m.as_str()).unwrap_or("");
                    
                    let result = match method {
                        "initialize" => self.handle_initialize(),
                        "tools/list" => self.handle_tools_list(),
                        "tools/call" => self.handle_tools_call(&req["params"]),
                        _ => json!({"error": "Method not found"}),
                    };

                    let response = json!({
                        "jsonrpc": "2.0",
                        "id": id,
                        "result": result
                    });

                    writeln!(stdout, "{}", response.to_string()).unwrap();
                    stdout.flush().unwrap();
                }
            }
        }
    }

    fn handle_initialize(&self) -> Value {
        json!({
            "protocolVersion": "2024-11-05",
            "capabilities": { "tools": {} },
            "serverInfo": { "name": "ThinkingOS", "version": "0.1.0" }
        })
    }

    fn handle_tools_list(&self) -> Value {
        json!({
            "tools": [
                {
                    "name": "search_vault",
                    "description": "Performs a full-text hybrid search across the user's markdown notes.",
                    "inputSchema": {
                        "type": "object",
                        "properties": { "query": { "type": "string" } },
                        "required": ["query"]
                    }
                },
                {
                    "name": "traverse_graph",
                    "description": "Finds related concepts connected to a starting concept within the semantic graph.",
                    "inputSchema": {
                        "type": "object",
                        "properties": { "concept": { "type": "string" } },
                        "required": ["concept"]
                    }
                }
            ]
        })
    }

    fn handle_tools_call(&self, params: &Value) -> Value {
        let name = params.get("name").and_then(|n| n.as_str()).unwrap_or("");
        
        // FIX: Create the variable first so it lives long enough for the reference!
        let default_args = json!({});
        let args = params.get("arguments").unwrap_or(&default_args);

        let text_output = match name {
            "search_vault" => {
                let q = args.get("query").and_then(|q| q.as_str()).unwrap_or("");
                match self.db.search_keyword(q) {
                    Ok(res) => res.into_iter().map(|(c, _)| c).collect::<Vec<_>>().join("\n---\n"),
                    Err(_) => "Search failed.".to_string(),
                }
            }
            "traverse_graph" => {
                let c = args.get("concept").and_then(|c| c.as_str()).unwrap_or("");
                match self.db.query_graph(c, 2) {
                    Ok(res) => res.join("\n"),
                    Err(_) => "Traversal failed.".to_string(),
                }
            }
            _ => "Tool not recognized.".to_string(),
        };

        json!({
            "content": [{ "type": "text", "text": text_output }]
        })
    }
}
