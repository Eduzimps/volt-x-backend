"""Generate source/module/dependency inventories without importing application code."""
import ast
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
docs=root/'docs'
docs.mkdir(exist_ok=True)
modules=[]
for p in sorted(root.rglob('*.py')):
    if any(part.startswith('.') or part in {'__pycache__','build','dist','audit-evidence','profiles','test-results'} for part in p.relative_to(root).parts):continue
    tree=ast.parse(p.read_bytes(),filename=str(p))
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):imports.extend(n.name for n in node.names)
        elif isinstance(node,ast.ImportFrom):imports.append('.'*node.level+(node.module or ''))
    definitions=[]
    def walk(nodes,parent=''):
        for node in nodes:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                name=parent+node.name
                definitions.append({'name':name,'kind':'class' if isinstance(node,ast.ClassDef) else 'function','line':node.lineno,'doc':ast.get_docstring(node) or ''})
                walk(node.body,name+'.')
    walk(tree.body)
    modules.append({'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'imports':sorted(set(imports)),'definitions':definitions})
(docs/'INVENTARIO.json').write_text(json.dumps(modules,indent=2,ensure_ascii=False))
lines=['# Módulos, classes, funções e dependências','', 'Inventário gerado da árvore final de fontes, sem executar os módulos. Nomes e linhas estão em `INVENTARIO.json`.','']
for m in modules:
    lines.extend(['## '+m['path'],'','Imports: '+', '.join(m['imports']),''])
    lines.extend(f"- `{n['name']}` ({n['kind']}, linha {n['line']})" for n in m['definitions'])
    lines.append('')
(docs/'MODULOS.md').write_text('\n'.join(lines))
routes=[]
tree=ast.parse((root/'webui/app.py').read_bytes())
for node in ast.walk(tree):
    if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
    for decorator in node.decorator_list:
        if isinstance(decorator,ast.Call) and isinstance(decorator.func,ast.Attribute) and decorator.func.attr in {'get','post','put','delete','patch'} and decorator.args:
            routes.append({'method':decorator.func.attr.upper(),'path':ast.literal_eval(decorator.args[0]),'handler':node.name,'line':node.lineno})
(docs/'ROTAS-LOCAIS.json').write_text(json.dumps(routes,indent=2))
tree_lines=['# Estrutura de pastas','','```text']
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if any(part.startswith('.') or part in {'__pycache__','build','dist','audit-evidence','profiles','test-results'} for part in rel.parts):continue
    if p.is_dir() or len(rel.parts)<=2:
        tree_lines.append('  '*(len(rel.parts)-1)+p.name+('/' if p.is_dir() else ''))
tree_lines.extend(['```','','Os arquivos individuais de ícones em api/assets foram omitidos desta listagem resumida; estão incluídos na entrega.'])
(docs/'ESTRUTURA.md').write_text('\n'.join(tree_lines))
print(f'Inventoried {len(modules)} Python files and {len(routes)} local routes.')
