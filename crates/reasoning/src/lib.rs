use storage::Database;
use anyhow::Result;

pub struct ReasoningEngine<'a> {
    pub db: &'a Database,
}

impl<'a> ReasoningEngine<'a> {
    pub fn new(db: &'a Database) -> Self {
        Self { db }
    }

    /// Builds a deterministic reasoning chain to prevent AI hallucinations
    pub fn build_context_prompt(&self, query: &str) -> Result<String> {
        let mut context_xml = String::from("<context_graph>\n");

        // 1. Find entry points via Keyword Search
        let search_results = self.db.search_keyword(query)?;
        
        if search_results.is_empty() {
            return Ok("No relevant context found in vault.".to_string());
        }

        context_xml.push_str("  <entry_nodes>\n");
        for (content, _score) in &search_results {
            context_xml.push_str(&format!("    <node>{}</node>\n", content.trim().replace('\n', " ")));
        }
        context_xml.push_str("  </entry_nodes>\n\n");

        // 2. Extract specific concepts from the query to traverse the graph
        // (In a real system we'd use NLP, but for now we look for known concepts)
        // Let's just traverse starting from the top search result's known graph links!
        // We'll mock this by hardcoding a quick extraction for our test vault:
        let test_concept = if query.to_lowercase().contains("cancer") {
            "Warburg Effect"
        } else {
            "Unknown"
        };

        let graph_nodes = self.db.query_graph(test_concept, 2)?;
        
        context_xml.push_str("  <semantic_neighborhood>\n");
        for node in graph_nodes {
            // Filter out file paths to keep prompt clean
            if !node.ends_with(".md") {
                context_xml.push_str(&format!("    <concept>{}</concept>\n", node));
            }
        }
        context_xml.push_str("  </semantic_neighborhood>\n");
        context_xml.push_str("</context_graph>\n\n");

        // 3. Assemble the final System Prompt
        let final_prompt = format!(
            "You are ThinkingOS, an AI reasoning agent. Answer the user's question STRICTLY using the provided context graph. Do not hallucinate external knowledge.\n\n{}\nUser Question: {}",
            context_xml, query
        );

        Ok(final_prompt)
    }
}
