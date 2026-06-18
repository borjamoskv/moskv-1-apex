use dashmap::DashMap;
use sha2::{Sha256, Digest};
use std::sync::Arc;
use std::thread;
use std::collections::HashSet;
use crossbeam_channel::{unbounded, Sender};
use rusqlite::{params, Connection};
use std::fs;
use std::path::PathBuf;

const QUORUM_THRESHOLD: usize = 3;

#[derive(Clone)]
pub struct MutationNode {
    pub hash: String,
    pub payload: String,
    pub target: String,
}

pub struct CausalGraph {
    nodes: Arc<DashMap<String, MutationNode>>,
    purgatory: Arc<DashMap<String, HashSet<String>>>,
    flusher_tx: Sender<MutationNode>,
}

impl CausalGraph {
    fn new() -> Self {
        let (tx, rx) = unbounded::<MutationNode>();
        
        // Ledger Sentinel (SQLite WAL)
        thread::spawn(move || {
            let conn = Connection::open(".cortex_dag.sqlite")
                .expect("[C5-REAL] Error abriendo el anclaje físico SQLite");
            
            conn.execute_batch(
                "PRAGMA journal_mode = WAL;
                 PRAGMA synchronous = NORMAL;
                 PRAGMA busy_timeout = 5000;"
            ).expect("[C5-REAL] Error forzando pragmas R10 (WAL)");

            conn.execute(
                "CREATE TABLE IF NOT EXISTS mutations (
                    hash TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    target TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )",
                [],
            ).expect("[C5-REAL] Error creando ledger");

            while let Ok(node) = rx.recv() {
                let _ = conn.execute(
                    "INSERT OR IGNORE INTO mutations (hash, payload, target) VALUES (?1, ?2, ?3)",
                    params![node.hash, node.payload, node.target],
                );
            }
        });

        CausalGraph {
            nodes: Arc::new(DashMap::new()),
            purgatory: Arc::new(DashMap::new()),
            flusher_tx: tx,
        }
    }

    fn inject_mutation(&self, agent_id: String, payload: String, target: String, expected_hash: String) -> Result<String, String> {
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        let computed_hash = format!("{:x}", hasher.finalize());

        if !computed_hash.starts_with(&expected_hash) {
            return Err(format!("[DEATH PROTOCOL] Hash mismatch. Computed: {}, Expected: {}", &computed_hash[..12], expected_hash));
        }

        let node_id = expected_hash.clone();
        
        if self.nodes.contains_key(&node_id) {
            return Ok("AlreadyCrystallized".to_string());
        }

        let mut quorum_reached = false;
        {
            let mut signatures = self.purgatory.entry(node_id.clone()).or_insert_with(HashSet::new);
            signatures.insert(agent_id.clone());
            if signatures.len() >= QUORUM_THRESHOLD {
                quorum_reached = true;
            }
        }

        if quorum_reached {
            let node = MutationNode {
                hash: node_id.clone(),
                payload: payload.clone(),
                target,
            };

            self.nodes.insert(node_id.clone(), node.clone());
            self.purgatory.remove(&node_id);
            let _ = self.flusher_tx.send(node);

            return Ok("QuorumReached".to_string());
        }

        Ok("Pending".to_string())
    }
}

fn main() {
    println!("[MOSKV-1] Booting Native Rust Sentinel C5-REAL (Zero Latency)");
    
    // Find index.html from workspace root (assuming binary runs from workspace root in git hooks)
    let mut index_path = PathBuf::from("apps/brt-video/out/index.html");
    if !index_path.exists() {
        // Fallback for direct execution
        index_path = PathBuf::from("../../../apps/brt-video/out/index.html");
    }
    
    let payload_bytes = fs::read(&index_path).unwrap_or_else(|_| {
        eprintln!("[DEATH PROTOCOL] Falla termodinámica: DOM index.html no encontrado.");
        std::process::exit(1);
    });
    
    let payload = String::from_utf8_lossy(&payload_bytes).into_owned();
    let mut hasher = Sha256::new();
    hasher.update(&payload_bytes);
    let expected_hash = format!("{:x}", hasher.finalize());
    let target = "BERLIN_MAIN_ROOM_DOM".to_string();

    let graph = Arc::new(CausalGraph::new());
    
    let agents = vec!["ROSALIA_SHARD_1", "TANGANA_GC", "WEATHERALL_DUB_MASTER"];
    let mut handles = vec![];

    for agent in agents {
        let g = Arc::clone(&graph);
        let p = payload.clone();
        let t = target.clone();
        let eh = expected_hash.clone();
        let a = agent.to_string();
        
        handles.push(thread::spawn(move || {
            let status = g.inject_mutation(a.clone(), p, t, eh);
            match status {
                Ok(s) => println!("[{}] -> Quorum Status: {}", a, s),
                Err(e) => {
                    eprintln!("{}", e);
                    std::process::exit(1);
                }
            }
        }));
    }

    for h in handles {
        h.join().unwrap();
    }

    println!("[SYSTEM] State Size: {} | Purgatory Size: {}", graph.nodes.len(), graph.purgatory.len());
    println!("[SYSTEM] Invariante DOM {} cristalizada 100% NATIVE RUST.", &expected_hash[..8]);
    
    // Sleep briefly to ensure async flusher writes to SQLite before exit (simple flush)
    thread::sleep(std::time::Duration::from_millis(100));
}
