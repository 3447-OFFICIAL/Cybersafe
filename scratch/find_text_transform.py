import os

for root, dirs, files in os.walk('.'):
    # Skip standard virtualenv or node_modules
    if any(p in root for p in ['venv', 'env', '.git', 'node_modules', '.agents']):
        continue
    for file in files:
        if file.endswith(('.html', '.js')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'safety-spline' in content or 'spline' in content:
                        print(f"File: {path}")
                        # Print lines containing the match
                        lines = content.split('\n')
                        for idx, line in enumerate(lines, 1):
                            if 'safety-spline' in line or 'spline' in line:
                                print(f"  {idx}: {line.strip()}")
            except Exception:
                pass
