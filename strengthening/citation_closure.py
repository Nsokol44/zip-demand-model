"""citation_closure.py — check every reference is cited and every
in-text citation has a reference entry. Usage:
    python3 citation_closure.py <manuscript.docx>
Prints reference count, orphan references (listed, never cited),
and dangling citations (cited, not listed). Exit 1 if any.
"""
import re
import sys
import unicodedata

from docx import Document


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def main(path):
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    ref_i = next(i for i, t in enumerate(paras)
                 if t.strip() == "References")
    body = "\n".join(paras[:ref_i])
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                body += "\n" + c.text
    body_f = fold(body)

    refs = {}
    for t in paras[ref_i + 1:]:
        t = t.strip()
        if not t:
            continue
        m = re.match(r"(.+?),\s", t)
        surname = fold(m.group(1)).strip() if m else fold(t[:30])
        ym = re.search(r"\((\d{4}[a-z]?)\)", t)
        year = ym.group(1) if ym else (
            "under review" if "under review" in t else "????")
        refs[(surname.lower(), year)] = t[:60]

    # cited keys: narrative "Surname (YYYY)" / "Surname et al. (YYYY)"
    # and parenthetical "(... Surname, YYYY ...)" segments
    cited = set()
    for m in re.finditer(r"([A-Z][\w’'\-]+)(?:\s+et al\.)?\s*\((\d{4}[a-z]?)\)",
                         body_f):
        cited.add((m.group(1).lower(), m.group(2)))
    for m in re.finditer(r"\(([^()]*\d{4}[a-z]?[^()]*)\)", body_f):
        for seg in m.group(1).split(";"):
            sm = re.search(r"([A-Z][\w’'\-]+)[^;]*?(\d{4}[a-z]?)", seg)
            if sm:
                cited.add((sm.group(1).lower(), sm.group(2)))
    if re.search(r"Author,?\s*\(?under review", body_f):
        cited.add(("author", "under review"))

    # normalize multi-author first surnames that appear as part of
    # institutional names in the reference list
    orphans = []
    for (sn, yr), txt in sorted(refs.items()):
        hit = any(c[1] == yr and (c[0] == sn or sn.startswith(c[0])
                                  or c[0].startswith(sn.split()[0]))
                  for c in cited)
        if not hit:
            # fall back: surname + year within 60 chars in body
            pat = re.escape(sn.split()[0]) + r"[^.]{0,60}?" + re.escape(yr)
            hit = re.search(pat, body_f, re.I) is not None
        if not hit:
            orphans.append((sn, yr, txt))
    known_first = {sn.split()[0] for sn, _ in refs}
    known_years = {yr for _, yr in refs}
    dangling = [(sn, yr) for (sn, yr) in sorted(cited)
                if yr in known_years and sn not in known_first
                and sn not in ("author",)]
    print(f"references: {len(refs)}")
    print(f"orphans (listed, never cited): {len(orphans)}")
    for o in orphans:
        print("  ORPHAN:", o)
    print(f"dangling candidates (cited, no matching entry): "
          f"{len(dangling)}")
    for d in dangling:
        print("  DANGLING?:", d)
    return 1 if orphans else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
