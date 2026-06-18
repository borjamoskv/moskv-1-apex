use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use dashmap::DashMap;
use sha2::{Sha256, Digest};
use std::sync::Arc;

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

/// The Zero-Latency Deterministic Causal Graph
#[pyclass]
pub struct CausalGraph {
    // Sharded hash map for massive lock-free concurrency. Resolves Thermodynamic Deadlocks.
    nodes: Arc<DashMap<String, MutationNode>>,
}

#[pymethods]
impl CausalGraph {
    #[new]
    fn new() -> Self {
        CausalGraph {
            nodes: Arc::new(DashMap::new()),
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

        // Lock-free insertion. Zero friction.
        self.nodes.insert(node_id.clone(), node);

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
