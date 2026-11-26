"""Single source of truth for law identity: id prefix, expected Article sequence, cross-check counts.

parse/versioning/validation/graph used to hardcode "BLDS2015" and the expected-article/per-count tables. That breaks the
moment a second corpus (Labour Code 45/2019/QH14, then Decree 152/2020 & 219/2025 as amend docs)
arrives. Stages now resolve identity from the source-file stem via this registry instead.

A law with no pinned article list still ingests — the strict article-sequence check is simply skipped.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Law:
    key: str
    prefix: str
    title: str
    articles: dict = field(default_factory=dict)   # stem -> list[int]; absent = don't pin the sequence
    expected: dict = field(default_factory=dict)   # stem -> {"units": int, "dieu": int, "graph": {...}}
    so_hieu: str | None = None                     # số hiệu văn bản gốc, dùng cho nút van_ban ở A7
    ngay_ban_hanh: str | None = None
    hieu_luc: str | None = None


LAWS = {
    "blds2015": Law(
        "blds2015", "BLDS2015", "Bộ luật Dân sự số 91/2015/QH13",
        articles={
            "blds2015_5dieu": [621, 626, 644, 650, 651],
            "blds2015_p4": list(range(609, 663)),
        },
        expected={
            "blds2015_5dieu": {"units": 35, "dieu": 5, "graph": {"nodes": 35, "edges": 64, "dup": 0}},
            "blds2015_p4": {"units": 215, "dieu": 54, "graph": {"nodes": 220, "edges": 364, "dup": 4}},
        },
        so_hieu="91/2015/QH13", ngay_ban_hanh="2015-11-24", hieu_luc="2017-01-01",
    ),
    # Base law d0 of the paper. Prefix "LLD2019" (Bộ luật Lao động) = our convention, not spec-canonical.
    # No article list pinned yet: ingest permissively; counts get backfilled once the corpus lands.
    "lld2019": Law("lld2019", "LLD2019", "Bộ luật Lao động số 45/2019/QH14",
                   so_hieu="45/2019/QH14", ngay_ban_hanh="2019-11-20", hieu_luc="2021-01-01"),
}


def law_for(stem):
    if stem in LAWS:
        return LAWS[stem]
    head = stem.split("_")[0]
    if head in LAWS:
        return LAWS[head]
    return LAWS["blds2015"]  # unknown stems keep the historical default; re-register instead of guessing


def prefix_for(stem):
    return law_for(stem).prefix


def articles_for(stem):
    return law_for(stem).articles.get(stem)


def expected_for(stem):
    return law_for(stem).expected.get(stem)