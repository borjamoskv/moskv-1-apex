use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use dashmap::DashMap;
use sha2::{Sha256, Digest};
use std::sync::Arc;
use std::thread;
use crossbeam_channel::{unbounded, Sender};
use rusqlite::{params, Connection};

/// The pure State Node in the Causal Graph (Base 60)
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

/// The Zero-Latency Deterministic Causal Graph with Async WAL Persistence
#[pyclass]
pub struct CausalGraph {
    // Sharded hash map for massive lock-free concurrency. Resolves Thermodynamic Deadlocks.
    nodes: Arc<DashMap<String, MutationNode>>,
    // Async channel to the Ledger Sentinel
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
            
            // Regla Global R10: Cumplimiento de WAL mode y busy_timeout
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
            flusher_tx: tx,
        }
    }

    /// Injects a mutation into the graph. Validates entropy cryptographically.
    /// Fails instantly on mismatch (C5-REAL Death Protocol enforced at RAM level).
    fn inject_mutation(&self, payload: String, target: String, expected_hash: String) -> PyResult<String> {
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        let computed_hash = format!("{:x}", hasher.finalize());

        // Validate hash prefix (allowing standard 12-char hashes)
        if !computed_hash.starts_with(&expected_hash) {
            return Err(PyValueError::new_err(format!(
                "[DEATH PROTOCOL] Hash mismatch. Computed: {}, Expected: {}",
                &computed_hash[..12], expected_hash
            )));
        }

        let node_id = expected_hash.clone();
        
        let node = MutationNode {
            hash: node_id.clone(),
            payload,
            target,
        };

        // Lock-free insertion en RAM. Latencia Cero.
        self.nodes.insert(node_id.clone(), node.clone());
        
        // Despacho asíncrono hacia SQLite WAL. No bloquea a Python.
        let _ = self.flusher_tx.send(node);

        Ok(node_id)
    }

    /// Resolves the current state size without blocking the Swarm.
    fn state_size(&self) -> usize {
        self.nodes.len()
    }
}

/// A Python module implemented in Rust using PyO3.
#[pymodule]
fn moskv_dag_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MutationNode>()?;
    m.add_class::<CausalGraph>()?;
    Ok(())
}
