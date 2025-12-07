from collections import defaultdict

def inspect_docs(docs):
    print("Total chunks:", len(docs))
    by_source = defaultdict(set)
    for d in docs:
        src = d.metadata.get("source", "unknown")
        try:
            p = int(d.metadata.get("page"))
        except Exception:
            p = None
        if p is not None:
            by_source[src].add(p)
    for src, pages in by_source.items():
        pages_sorted = sorted(pages)
        print(f"{src}: {len(pages_sorted)} páginas (min..max): {pages_sorted[:3]} ... {pages_sorted[-3:]}")
