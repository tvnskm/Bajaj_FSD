from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()

class RequestBody(BaseModel):
    data: List[str]

@app.post("/bfhl")
def handle_request(body: RequestBody):
    items = body.data

    bad = []
    dupes = []
    edges = []
    seen = set()

    for item in items:
        item = item.strip()

        if "->" not in item or len(item) != 4:
            bad.append(item)
            continue

        p = item[0]
        c = item[3]

        if not (p.isalpha() and c.isalpha() and p.isupper() and c.isupper()):
            bad.append(item)
            continue

        if p == c:
            bad.append(item)
            continue

        if item in seen:
            if item not in dupes:
                dupes.append(item)
            continue

        seen.add(item)
        edges.append((p, c))


    graph = {}
    children = set()
    parent_map = {}

    for p, c in edges:
        if c in parent_map:
            continue  

        parent_map[c] = p

        if p not in graph:
            graph[p] = []

        graph[p].append(c)
        children.add(c)

        if c not in graph:
            graph[c] = []

    all_nodes = set(graph.keys())
    roots = [n for n in all_nodes if n not in children]

    
    hierarchies = []
    max_depth = 0
    biggest_root = ""
    trees = 0
    cycles = 0

    visited_global = set()

    def get_depth(t):
        if not t:
            return 1
        return 1 + max(get_depth(t[k]) for k in t)

   
    def dfs(node, stack, visited):
        if node in stack:
            return None, True

        stack.add(node)
        visited.add(node)

        sub = {}

        for child in graph[node]:
            res, cyc = dfs(child, stack, visited)
            if cyc:
                return None, True
            sub[child] = res

        stack.remove(node)
        return sub, False

   
    for root in roots:
        local_visited = set()
        tree, has_cycle = dfs(root, set(), local_visited)

        visited_global.update(local_visited)

        if has_cycle:
            hierarchies.append({
                "root": root,
                "tree": {},
                "has_cycle": True
            })
            cycles += 1
        else:
            d = get_depth(tree)

            hierarchies.append({
                "root": root,
                "tree": {root: tree},
                "depth": d
            })

            trees += 1

            if d > max_depth or (d == max_depth and (biggest_root == "" or root < biggest_root)):
                max_depth = d
                biggest_root = root

    
    for node in sorted(all_nodes):
        if node not in visited_global:
            local_visited = set()
            tree, has_cycle = dfs(node, set(), local_visited)

            visited_global.update(local_visited)

            if has_cycle:
                hierarchies.append({
                    "root": node,
                    "tree": {},
                    "has_cycle": True
                })
                cycles += 1


    summary = {
        "total_trees": trees,
        "total_cycles": cycles,
        "largest_tree_root": biggest_root
    }


    return {
        "user_id": "MohanVNSKTiruvaipati_28102005",
        "email_id": "vt3769@srmist.edu.in",
        "college_roll_number": "RA2311003011004",
        "hierarchies": hierarchies,
        "invalid_entries": bad,
        "duplicate_edges": dupes,
        "summary": summary
    }