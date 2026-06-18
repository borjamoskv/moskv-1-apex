import re
import sys
import hashlib
from pathlib import Path

def parse_pytest_output(output):
    """Extrae las rutas y errores de pytest."""
    errors = []
    # Busca patrones como: E   ModuleNotFoundError: No module named 'kernel'
    # y la línea de traceback que tiene el archivo fallido
    lines = output.split('\n')
    current_file = None
    for i, line in enumerate(lines):
        # Detectar el archivo que falla en el traceback
        # format: path/to/file.py:line: in <module>
        file_match = re.match(r'^([^:]+\.py):(\d+): in .*', line)
        if file_match:
            current_file = file_match.group(1)
        
        # Detectar el error
        err_match = re.match(r'^E\s+([A-Za-z]+Error): (.*)', line)
        if err_match and current_file:
            err_type = err_match.group(1)
            err_msg = err_match.group(2)
            errors.append({
                'file': current_file,
                'type': err_type,
                'message': err_msg
            })
            current_file = None
    return errors

def self_heal(errors):
    """Aplica curación a los errores conocidos."""
    healed_count = 0
    for err in errors:
        if err['type'] == 'ModuleNotFoundError' and 'kernel' in err['message']:
            print(f"[Error Sensor] -> Curando {err['type']} en {err['file']}...")
            # Solución: el archivo intenta hacer "from kernel..." pero `kernel` no está en sys.path.
            # Inyectamos una cura en el propio archivo o sugerimos curar ouroboros_loop.py.
            # Para una cura C5-REAL directa en el archivo que falla, inyectamos sys.path.insert:
            p = Path(err['file'])
            if p.exists():
                with open(p, 'r') as f:
                    content = f.read()
                
                # Inyección de curación
                cure_injection = "\nimport sys, os\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
                if cure_injection not in content:
                    content = cure_injection + content
                    with open(p, 'w') as f:
                        f.write(content)
                    print(f"[Error Sensor] ✓ {err['file']} auto-curado.")
                    healed_count += 1
                else:
                    print(f"[Error Sensor] {err['file']} ya estaba curado.")
        elif err['type'] == 'ModuleNotFoundError' and 'moskv_1' in err['message']:
            print(f"[Error Sensor] -> Curando {err['type']} en {err['file']}...")
            p = Path(err['file'])
            if p.exists():
                with open(p, 'r') as f:
                    content = f.read()
                cure_injection = "\nimport sys, os\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))\n"
                if cure_injection not in content:
                    content = cure_injection + content
                    with open(p, 'w') as f:
                        f.write(content)
                    print(f"[Error Sensor] ✓ {err['file']} auto-curado.")
                    healed_count += 1
    return healed_count

if __name__ == '__main__':
    print("[Error Sensor] Escaneando STDIN...")
    output = sys.stdin.read()
    errors = parse_pytest_output(output)
    if not errors:
        print("[Error Sensor] No se detectaron patrones de error curables.")
    else:
        print(f"[Error Sensor] Detectados {len(errors)} errores de entropía.")
        healed = self_heal(errors)
        if healed > 0:
            print(f"[Error Sensor] Auto-curación completada. {healed} mutaciones inyectadas.")
            sys.exit(0)
        else:
            print("[Error Sensor] Fallo al auto-curar. Requiere intervención manual.")
            sys.exit(1)
