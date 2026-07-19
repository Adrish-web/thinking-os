use clap::{Parser, Subcommand};
use std::fs;
use std::path::PathBuf;
use walkdir::WalkDir;

use parser::parse_markdown_file;
use storage::Database;
use reasoning::ReasoningEngine;
use mcp_server::McpServer;

#[derive(Parser)]
#[command(name = "thinking")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Build { #[arg(short, long, default_value = ".")] vault: PathBuf },
    Query { #[arg(short, long, default_value = ".")] vault: PathBuf, concept: String },
    Search { #[arg(short, long, default_value = ".")] vault: PathBuf, query: String },
    Reason { #[arg(short, long, default_value = ".")] vault: PathBuf, question: String },
    Mcp { #[arg(short, long, default_value = ".")] vault: PathBuf },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    match &cli.command {
        Commands::Build { vault } => {
            let db_path = vault.join("thinking.db");
            let db = Database::new(&db_path)?;
            let (mut f_cnt, mut n_cnt, mut e_cnt) = (0, 0, 0);

            for entry in WalkDir::new(vault).into_iter().filter_map(|e| e.ok()) {
                if entry.path().is_file() && entry.path().extension().and_then(|s| s.to_str()) == Some("md") {
                    f_cnt += 1;
                    let content = fs::read_to_string(entry.path())?;
                    let (nodes, edges) = parse_markdown_file(&entry.path().to_string_lossy(), &content);
                    
                    for n in &nodes { db.insert_node(n)?; }
                    for e in &edges { db.insert_edge(e)?; }
                    n_cnt += nodes.len(); e_cnt += edges.len();
                }
            }
            println!("✅ Built {} files | {} nodes | {} edges", f_cnt, n_cnt, e_cnt);
        }
        Commands::Query { vault, concept } => {
            let db_path = vault.join("thinking.db");
            let db = Database::new(&db_path)?;
            println!("🔍 Traversing Graph from: '{}'", concept);
            let connected = db.query_graph(concept, 2)?;
            for (i, node) in connected.iter().enumerate() { println!("  ↳ [{}] {}", i + 1, node); }
        }
        Commands::Search { vault, query } => {
            let db_path = vault.join("thinking.db");
            let db = Database::new(&db_path)?;
            println!("⚡ Keyword Search for: '{}'", query);
            let results = db.search_keyword(query)?;
            for (i, (content, score)) in results.iter().enumerate() { 
                println!("  ↳ [{}] (Score: {:.2}) {}", i + 1, score, content); 
            }
        }
        Commands::Reason { vault, question } => {
            let db_path = vault.join("thinking.db");
            let db = Database::new(&db_path)?;
            let engine = ReasoningEngine::new(&db);
            
            println!("🧠 Compiling deterministic reasoning chain...\n");
            let prompt = engine.build_context_prompt(question)?;
            println!("================ SYSTEM PROMPT ================\n{}", prompt);
            println!("===============================================\n");
            println!("🚀 (In production, this string is streamed directly to Ollama/Claude/OpenAI)");
        }
        Commands::Mcp { vault } => {
            let db_path = vault.join("thinking.db");
            let db = Database::new(&db_path)?;
            let server = McpServer::new(&db);
            
            // Block thread and listen on stdio
            server.start_listening();
        }
    }
    Ok(())
}
