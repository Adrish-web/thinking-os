use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum NodeType { Document, Concept, Claim, Evidence, Question, Source, Method }

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EdgeType { Contains, PartOf, Supports, Contradicts, Answers, DerivedFrom, RelatedTo, Causes, Uses }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    pub id: String,
    pub node_type: NodeType,
    pub content: String,
    pub file_path: String,
    pub line_start: u32,
    pub line_end: u32,
    pub metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Edge {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub edge_type: EdgeType,
    pub weight: f32,
}

impl Node {
    pub fn new(id: String, node_type: NodeType, content: String, file_path: String, line_start: u32, line_end: u32) -> Self {
        Self { id, node_type, content, file_path, line_start, line_end, metadata: HashMap::new() }
    }
}
