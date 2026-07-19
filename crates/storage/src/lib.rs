use rusqlite::{params, Connection, Result};
use semantic_ir::{Node, Edge};
use std::path::Path;

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new<P: AsRef<Path>>(db_path: P) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        conn.execute_batch(
            "PRAGMA journal_mode = WAL;
             PRAGMA foreign_keys = ON;"
        )?;
        let db = Self { conn };
        db.init_schema()?;
        Ok(db)
    }

    fn init_schema(&self) -> Result<()> {
        self.conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY, node_type TEXT NOT NULL, content TEXT NOT NULL,
                file_path TEXT NOT NULL, line_start INTEGER NOT NULL, line_end INTEGER NOT NULL,
                metadata TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_nodes_file ON nodes(file_path);

            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY, source_id TEXT NOT NULL, target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL, weight REAL DEFAULT 1.0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
            
            CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
                id UNINDEXED, content
            );

            CREATE TRIGGER IF NOT EXISTS after_node_insert AFTER INSERT ON nodes BEGIN
                INSERT INTO nodes_fts (id, content) VALUES (new.id, new.content);
            END;

            CREATE TRIGGER IF NOT EXISTS after_node_update AFTER UPDATE ON nodes BEGIN
                UPDATE nodes_fts SET content = new.content WHERE id = new.id;
            END;

            CREATE TRIGGER IF NOT EXISTS after_node_delete AFTER DELETE ON nodes BEGIN
                DELETE FROM nodes_fts WHERE id = old.id;
            END;"
        )?;
        Ok(())
    }

    pub fn insert_node(&self, node: &Node) -> Result<()> {
        let metadata_json = serde_json::to_string(&node.metadata).unwrap();
        let node_type_str = serde_json::to_string(&node.node_type).unwrap().replace('\"', "");

        self.conn.execute(
            "INSERT INTO nodes (id, node_type, content, file_path, line_start, line_end, metadata)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
             ON CONFLICT(id) DO UPDATE SET content=excluded.content, metadata=excluded.metadata, updated_at=CURRENT_TIMESTAMP;",
            params![node.id, node_type_str, node.content, node.file_path, node.line_start, node.line_end, metadata_json],
        )?;
        Ok(())
    }

    pub fn insert_edge(&self, edge: &Edge) -> Result<()> {
        let edge_type_str = serde_json::to_string(&edge.edge_type).unwrap().replace('\"', "");
        self.conn.execute(
            "INSERT INTO edges (id, source_id, target_id, edge_type, weight)
             VALUES (?1, ?2, ?3, ?4, ?5)
             ON CONFLICT(id) DO UPDATE SET weight=excluded.weight, created_at=CURRENT_TIMESTAMP;",
            params![edge.id, edge.source_id, edge.target_id, edge_type_str, edge.weight],
        )?;
        Ok(())
    }

    pub fn query_graph(&self, start_concept: &str, depth: u32) -> Result<Vec<String>> {
        let sql = r#"
            WITH RECURSIVE traversal(id, depth) AS (
                SELECT id, 0 FROM nodes WHERE content = ?1
                UNION ALL
                SELECT CASE WHEN edges.source_id = t.id THEN edges.target_id ELSE edges.source_id END, t.depth + 1
                FROM edges JOIN traversal t ON (edges.source_id = t.id OR edges.target_id = t.id)
                WHERE t.depth < ?2
            )
            SELECT DISTINCT nodes.content FROM nodes JOIN traversal t ON nodes.id = t.id;
        "#;
        let mut stmt = self.conn.prepare(sql)?;
        let rows = stmt.query_map(params![start_concept, depth], |row| row.get::<_, String>(0))?;
        let mut results = Vec::new();
        for name in rows { results.push(name?); }
        Ok(results)
    }

    pub fn search_keyword(&self, query: &str) -> Result<Vec<(String, f64)>> {
        let clean_query: String = query.chars()
            .filter(|c| c.is_alphanumeric() || c.is_whitespace())
            .collect();
            
        // FIX: Convert "Why is cancer" -> "Why OR is OR cancer"
        let or_query = clean_query.split_whitespace().collect::<Vec<&str>>().join(" OR ");

        let sql = "SELECT content, rank FROM nodes_fts WHERE nodes_fts MATCH ?1 ORDER BY rank LIMIT 10;";
        let mut stmt = self.conn.prepare(sql)?;
        
        let rows = stmt.query_map([or_query], |row| {
            let content: String = row.get(0)?;
            let rank: f64 = row.get(1)?;
            Ok((content, rank))
        })?;
        
        let mut results = Vec::new();
        for r in rows { results.push(r?); }
        Ok(results)
    }
}
