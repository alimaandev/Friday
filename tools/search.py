import glob
import os
import re


def search_files(pattern: str, path: str = ".") -> dict:
    try:
        matches = glob.glob(os.path.join(path, pattern), recursive=True)
        matches = [m.replace("\\", "/") for m in matches]
        return {"matches": matches, "count": len(matches), "error": None}
    except Exception as e:
        return {"matches": [], "count": 0, "error": str(e)}


def grep_files(pattern: str, path: str = ".", include: str = None) -> dict:
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        results = []
        for root, _dirs, files in os.walk(path):
            for fname in files:
                if include and not glob.fnmatch.fnmatch(fname, include):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if compiled.search(line):
                                results.append({
                                    "file": fpath.replace("\\", "/"),
                                    "line": i,
                                    "text": line.strip()[:200],
                                })
                except Exception:
                    pass
        return {"results": results, "count": len(results), "error": None}
    except Exception as e:
        return {"results": [], "count": 0, "error": str(e)}
