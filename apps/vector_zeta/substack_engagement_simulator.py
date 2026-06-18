import argparse
from typing import List, Dict, Any

class CommentNode:
    def __init__(self, content: str, depth: int = 0):
        self.content = content
        self.depth = depth
        self.replies: List['CommentNode'] = []

    def add_reply(self, content: str) -> 'CommentNode':
        child = CommentNode(content, self.depth + 1)
        self.replies.append(child)
        return child

def build_tree_from_spec(spec: List[Dict[str, Any]]) -> List[CommentNode]:
    def build_node(node_spec: Dict[str, Any], depth: int = 0) -> CommentNode:
        node = CommentNode(node_spec["content"], depth)
        for r_spec in node_spec.get("replies", []):
            node.replies.append(build_node(r_spec, depth + 1))
        return node
    return [build_node(s) for s in spec]

def calculate_exergy(nodes: List[CommentNode], is_post: bool, reply_decay: float = 0.5) -> Dict[str, float]:
    """
    Calcula la exergía y anergía total de un árbol de comentarios en Substack.
    
    En Posts (Foro Privado):
      - Nivel 0 (Comentario directo): 1.0 exergía
      - Nivel n (Respuesta): reply_decay ^ n exergía (decaimiento marginal por profundidad)
      
    En Notas (Plaza Pública):
      - Nivel 0 (Comentario directo): 1.0 exergía
      - Nivel n (Respuesta): 0.0 exergía (el algoritmo de Notes de Substack ignora el ruido profundo)
    """
    total_raw_energy = 0.0
    total_exergy = 0.0

    def traverse(node: CommentNode):
        nonlocal total_raw_energy, total_exergy
        total_raw_energy += 1.0
        
        if node.depth == 0:
            total_exergy += 1.0
        else:
            if is_post:
                total_exergy += (reply_decay ** node.depth)
            else:
                total_exergy += 0.0

        for reply in node.replies:
            traverse(reply)

    for node in nodes:
        traverse(node)

    efficiency = total_exergy / total_raw_energy if total_raw_energy > 0 else 0.0
    anergy = total_raw_energy - total_exergy

    return {
        "raw_energy": total_raw_energy,
        "exergy": total_exergy,
        "anergy": anergy,
        "efficiency": efficiency
    }

def run_simulation(decay: float):
    # Estrategia A: Hilo de discusión profundo (1 comentario inicial + 3 niveles de respuestas consecutivas)
    spec_thread = [
        {
            "content": "Comentario inicial",
            "replies": [
                {
                    "content": "Respuesta Nivel 1",
                    "replies": [
                        {
                            "content": "Respuesta Nivel 2",
                            "replies": [
                                {
                                    "content": "Respuesta Nivel 3"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    # Estrategia B: Blast plano (4 comentarios directos independientes, p. ej., la estrategia de 4 comments en una Nota)
    spec_flat = [
        {"content": "Comentario 1"},
        {"content": "Comentario 2"},
        {"content": "Comentario 3"},
        {"content": "Comentario 4"}
    ]

    tree_thread = build_tree_from_spec(spec_thread)
    tree_flat = build_tree_from_spec(spec_flat)

    # Simulaciones
    post_thread = calculate_exergy(tree_thread, is_post=True, reply_decay=decay)
    post_flat = calculate_exergy(tree_flat, is_post=True, reply_decay=decay)
    note_thread = calculate_exergy(tree_thread, is_post=False, reply_decay=decay)
    note_flat = calculate_exergy(tree_flat, is_post=False, reply_decay=decay)

    print("=" * 80)
    print(f" SUBSTACK ALGORITHMIC EXERGY SIMULATOR (C5-REAL) | Decay Factor: {decay}")
    print("=" * 80)
    print(f"{'Platform / Strategy':<30} | {'Raw Cost':<10} | {'Exergy (X)':<10} | {'Anergy (A)':<10} | {'Efficiency':<10}")
    print("-" * 80)
    print(f"{'POST - Deep Thread (1+3 replies)':<30} | {post_thread['raw_energy']:<10.1f} | {post_thread['exergy']:<10.2f} | {post_thread['anergy']:<10.2f} | {post_thread['efficiency']:<10.2%}")
    print(f"{'POST - Flat Blast (4 direct)':<30} | {post_flat['raw_energy']:<10.1f} | {post_flat['exergy']:<10.2f} | {post_flat['anergy']:<10.2f} | {post_flat['efficiency']:<10.2%}")
    print(f"{'NOTE - Deep Thread (1+3 replies)':<30} | {note_thread['raw_energy']:<10.1f} | {note_thread['exergy']:<10.2f} | {note_thread['anergy']:<10.2f} | {note_thread['efficiency']:<10.2%}")
    print(f"{'NOTE - Flat Blast (4 direct)':<30} | {note_flat['raw_energy']:<10.1f} | {note_flat['exergy']:<10.2f} | {note_flat['anergy']:<10.2f} | {note_flat['efficiency']:<10.2%}")
    print("=" * 80)
    print("Conclusiones Termodinámicas de la Invariante:")
    print("1. En Notas, toda interacción profunda se disipa en forma de anergía algorítmica pura.")
    print("2. La 'falsa viralidad' se mitiga en la Plaza Pública ignorando las ramas del grafo.")
    print("3. La única forma de inyectar exergía a una nota es ensanchando la base (Flat Blast).")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Substack Comment Exergy Simulator")
    parser.add_argument("--decay", type=float, default=0.5, help="Decay factor for replies in Posts (0.0 to 1.0)")
    args = parser.parse_args()
    run_simulation(args.decay)
