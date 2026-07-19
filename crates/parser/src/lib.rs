use lazy_static::lazy_static;
use regex::Regex;
use semantic_ir::{Edge, EdgeType, Node, NodeType};
use sha2::{Digest, Sha256};

lazy_static! {
    static ref WIKILINK_RE: Regex = Regex::new(r"\[\[(.*?)\]\]").unwrap();
    static ref RELATION_RE: Regex = Regex::new(r"(?i)([a-z_]+)::\s*\[\[(.*?)\]\]").unwrap();
}

pub fn generate_id(prefix: &str, seed: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(seed.as_bytes());
    format!("{}_{}", prefix, hex::encode(hasher.finalize()))
}

pub fn parse_markdown_file(file_path: &str, content: &str) -> (Vec<Node>, Vec<Edge>) {
    let mut nodes = Vec::new();
    let mut edges = Vec::new();

    let doc_id = generate_id("doc", file_path);
    
    // FIX: Set the content to `content.to_string()` instead of `file_path.to_string()`!
    nodes.push(Node::new(doc_id.clone(), NodeType::Document, content.to_string(), file_path.to_string(), 0, 0));

    // Extract Wikilinks
    for cap in WIKILINK_RE.captures_iter(content) {
        let concept_name = cap[1].trim().to_string();
        let concept_id = generate_id("concept", &concept_name);
        nodes.push(Node::new(concept_id.clone(), NodeType::Concept, concept_name, file_path.to_string(), 0, 0));
        edges.push(Edge {
            id: generate_id("edge", &format!("{}{}", doc_id, concept_id)),
            source_id: doc_id.clone(), target_id: concept_id, edge_type: EdgeType::Contains, weight: 1.0,
        });
    }

    // Extract Typed Relations
    for cap in RELATION_RE.captures_iter(content) {
        let relation_str = cap[1].to_lowercase();
        let target_name = cap[2].trim().to_string();
        let target_id = generate_id("concept", &target_name);
        
        let edge_type = match relation_str.as_str() {
            "causes" => EdgeType::Causes, "supports" => EdgeType::Supports, "answers" => EdgeType::Answers,
            _ => EdgeType::RelatedTo,
        };

        edges.push(Edge {
            id: generate_id("edge_rel", &format!("{}{}{:?}", doc_id, target_id, edge_type)),
            source_id: doc_id.clone(), target_id, edge_type, weight: 1.0,
        });
    }

    nodes.dedup_by(|a, b| a.id == b.id);
    edges.dedup_by(|a, b| a.id == b.id);
    (nodes, edges)
}
