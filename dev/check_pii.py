"""
PII detection hook for pre-commit.

Checks staged files for:
  1. Structured PII patterns (regex) — emails, identifiers, cards, phone.
  2. Italian identifiers — codice fiscale (shape-distinctive) and partita
     IVA (context-keyed).
  3. Wordlist denylist — case-insensitive whole-word match against entries
     in dev/pii_wordlist.local.txt (gitignored). Catches contextual PII
     that no structured detector sees: real names, real org names,
     local-machine identifiers, real path components, region-fingerprint
     vocabulary (CNH, RG, MEI, R$, etc.).

Suppress any individual line with '# pii:allow'. The wordlist file itself
is gitignored — its contents stay local. See dev/pii_wordlist.example.txt
for the template.
"""

import os
import re
import sys

# Structured patterns — shape catches the value regardless of context.
PATTERNS = {
    "Email address": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "Brazilian CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
    "Brazilian CNPJ": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
    "US SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "Credit Card (Visa)": r"\b4\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "Credit Card (MC)": r"\b5[1-5]\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "Phone (international)": r"\b\+\d{1,3}[\s-]?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4}\b",
    # Italian codice fiscale — 16-char fixed shape, low false-positive risk.
    "Italian Codice Fiscale": r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b",
    # Italian partita IVA — 11 digits is too broad on its own; require a
    # context keyword so we only fire on real assertions.
    "Italian Partita IVA": (r"(?i)(?:partita\s+iva|p\.?\s*iva|VAT)[:\s]+\d{11}\b"),
}

# Files/paths the hook should not scan.
SKIP_PATTERNS = [
    r"\.secrets\.baseline$",
    r"dev/check_pii\.py$",
    r"dev/pii_wordlist\.example\.txt$",
    r"bak/",
    r"\.git/",
]

# Wordlist file (gitignored — contents stay local).
WORDLIST_PATH = "dev/pii_wordlist.local.txt"


def should_skip(filepath):
    return any(re.search(pat, filepath) for pat in SKIP_PATTERNS)


def load_wordlist():
    """Read the local wordlist into a list of (term, compiled_regex) pairs.

    Each non-empty, non-comment line becomes a case-insensitive
    whole-word regex. Returns an empty list if the file is absent.
    """
    if not os.path.exists(WORDLIST_PATH):
        return []
    patterns = []
    with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            term = line.strip()
            if not term or term.startswith("#"):
                continue
            patterns.append(
                (term, re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE))
            )
    return patterns


def check_file(filepath, wordlist_patterns):
    if should_skip(filepath):
        return []

    findings = []
    try:
        with open(filepath, "r", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                # Skip lines with pragma comments.
                if "pii:allow" in line.lower():
                    continue
                # Structured patterns.
                for name, pattern in PATTERNS.items():
                    for match in re.finditer(pattern, line):
                        findings.append((filepath, lineno, name, match.group()))
                # Wordlist hits.
                for term, pattern in wordlist_patterns:
                    if pattern.search(line):
                        findings.append((filepath, lineno, "Wordlist match", term))
    except (OSError, UnicodeDecodeError):
        pass

    return findings


def main():
    wordlist_patterns = load_wordlist()
    all_findings = []
    for filepath in sys.argv[1:]:
        all_findings.extend(check_file(filepath, wordlist_patterns))

    if all_findings:
        print("PII detected in staged files:\n")
        for filepath, lineno, pii_type, value in all_findings:
            print(f"  {filepath}:{lineno}: {pii_type}: {value}")
        print(
            "\nTo suppress a specific line, add '# pii:allow' to the end of that line."
        )
        if not os.path.exists(WORDLIST_PATH):
            print(
                "\nNote: dev/pii_wordlist.local.txt does not exist on this "
                "machine — only structured patterns were checked. See "
                "dev/pii_wordlist.example.txt for the template."
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
