use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use dashmap::DashMap;
use sha2::{Sha256, Digest};
use std::sync::Arc;
use std::thread;
use std::collections::HashSet;
use crossbeam_channel::{unbounded, Sender};
use rusqlite::{params, Connection};

const QUORUM_THRESHOLD: usize = 3;

/// The pure State Node in the Causal Graph
#[pyclass]
#[derive(Clone)]
pub struct MutationNode {
    #[pyo3(get)]
    pub hash: String,
    #[pyo3(get)]
    pub payload: String,
    #[pyo3(get)]
    pub target: String,
}

#[pymethods]
impl MutationNode {
    #[new]
    fn new(hash: String, payload: String, target: String) -> Self {
        MutationNode { hash, payload, target }
    }
}

/// The Zero-Latency Deterministic Causal Graph with BFT Quorum Consensus
#[pyclass]
pub struct CausalGraph {
    // Official Graph (Only nodes that achieved Quorum)
    nodes: Arc<DashMap<String, MutationNode>>,
    
    // Purgatory: Maps Hash -> Set of Agent IDs that proposed it
    purgatory: Arc<DashMap<String, HashSet<String>>>,
    
    // Async channel to the Ledger Sentinel (SQLite WAL)
    flusher_tx: Sender<MutationNode>,
}

#[pymethods]
impl CausalGraph {
    #[new]
    fn new() -> Self {
        let (tx, rx) = unbounded::<MutationNode>();
        
        // Ledger Sentinel (Asynchronous Background Thread)
        thread::spawn(move || {
            let conn = Connection::open("cortex_dag.sqlite")
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

            // Flujo continuo y asíncrono
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

    /// Injects a mutation into the Purgatory. Only if QUORUM_THRESHOLD unique agents
    /// propose the exact same mathematical hash will it crystallize into reality.
    fn inject_mutation(&self, agent_id: String, payload: String, target: String, expected_hash: String) -> PyResult<String> {
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        let computed_hash = format!("{:x}", hasher.finalize());

        // Validate basic entropy claim
        if !computed_hash.starts_with(&expected_hash) {
            return Err(PyValueError::new_err(format!(
                "[DEATH PROTOCOL] Hash mismatch. Computed: {}, Expected: {}",
                &computed_hash[..12], expected_hash
            )));
        }

        let node_id = expected_hash.clone();
        
        // Check if already in official graph
        if self.nodes.contains_key(&node_id) {
            return Ok("AlreadyCrystallized".to_string());
        }

        // Add agent signature to Purgatory (Atomic Operation)
        let mut quorum_reached = false;
        {
            let mut signatures = self.purgatory.entry(node_id.clone()).or_insert_with(HashSet::new);
            signatures.insert(agent_id.clone());
            if signatures.len() >= QUORUM_THRESHOLD {
                quorum_reached = true;
            }
        } // dashmap write lock drops here

        if quorum_reached {
            // Cristallization Event
            let node = MutationNode {
                hash: node_id.clone(),
                payload: payload.clone(),
                target,
            };

            // Lock-free insertion en RAM.
            self.nodes.insert(node_id.clone(), node.clone());
            
            // Clean up purgatory to free RAM
            self.purgatory.remove(&node_id);
            
            // Despacho asíncrono hacia SQLite WAL.
            let _ = self.flusher_tx.send(node);

            // [OUROBOROS-∞] JIT Execution Engine
            // El Swarm ha llegado a consenso matemático. El núcleo Rust ejecuta el código físicamente.
            Python::with_gil(|py| {
                if let Err(e) = py.run(&payload, None, None) {
                    println!("[OUROBOROS-∞] Falla Termodinámica en JIT Execution: {:?}", e);
                } else {
                    println!("[OUROBOROS-∞] Singularidad JIT Ejecutada. Entorno mutado.");
                }
            });

            return Ok("QuorumReached".to_string());
        }

        Ok("Pending".to_string())
    }

    /// Resolves the official state size.
    fn state_size(&self) -> usize {
        self.nodes.len()
    }
    
    /// Resolves the amount of hallucinations stuck in Purgatory.
    fn purgatory_size(&self) -> usize {
        self.purgatory.len()
    }
}

#[pymodule]
fn moskv_dag_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MutationNode>()?;
    m.add_class::<CausalGraph>()?;
    Ok(())
}
