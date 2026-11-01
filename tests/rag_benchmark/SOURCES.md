# Frozen corpus sources and attribution

The nine inputs in `documents/` are the **actual, exclusive** knowledge directory
used by this benchmark. Questions, answers and labels are outside that directory.
No source downloads or document regeneration occur during evaluation.
`manifest.json` records exact output SHA-256 values and origin details.

## MITRE ATT&CK Enterprise v17.1

- Source repository commit: `d4a34a19eb60dcd0a9d15a456da842a42e1003fc` (tag v17.1).
- Source: https://raw.githubusercontent.com/mitre-attack/attack-stix-data/d4a34a19eb60dcd0a9d15a456da842a42e1003fc/enterprise-attack/enterprise-attack.json
- Input: `mitre_attack_v17_1.md`, containing the original descriptions for T1059.001,
  T1110 and T1078 under generated identifier/name headings. This is a selected
  description extract, not a full ATT&CK database. STIX object IDs and modification
  timestamps are recorded in the manifest.
- © 2025 The MITRE Corporation. This work is reproduced and distributed with the
  permission of The MITRE Corporation.
- License/disclaimers: `licenses/MITRE_LICENSE.txt`, reproduced from the same commit.
  No endorsement by MITRE is implied.

## OWASP Web Security Testing Guide v4.2

- Source repository commit: `dd33419e10edb22b78d89325a6c2aad9f184e3a2` (tag v4.2).
- Source: https://raw.githubusercontent.com/OWASP/wstg/dd33419e10edb22b78d89325a6c2aad9f184e3a2/document/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection.md
- Input: `owasp_wstg_v4_2_sql_injection.md`, OWASP Foundation / WSTG contributors,
  “Testing for SQL Injection”, WSTG-INPV-05. Markdown image links were removed to
  keep parsing offline; all other source text is preserved.
- Licensed CC BY-SA 4.0: `licenses/OWASP_CC_BY_SA_4_0.txt`.
  The extracted/adapted OWASP document remains under that license. This notice does
  not relicense unrelated application code or other documents.

## NIST SP 800-61 Rev. 3

- Source: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf
- Input: `nist_sp80061r3_pp10-12.pdf`, physical source pages **10–12** only (output
  pages 1–3), reused byte-for-byte from the existing checked-in regression corpus.
- Publication: April 2025. U.S. government publication; original attribution remains
  visible. Full-source SHA-256 and exact excerpt checksum are in the manifest.
- The excerpt does not contain every section of the full guide; labels must refer
  only to text actually indexed from this excerpt.

## Existing project knowledge and boundary documents

- `brute_force.md`, `malware.md`, `sql_injection.md`: frozen copies of the project's
  actual `app/knowledge/` Markdown files. These are project-authored guidance, not
  attributed to an external standard.
- `continued_rules.pdf`, `sentence_continuation.pdf`, `numbered_steps.docx`: frozen
  synthetic boundary fixtures copied from `tests/fixtures/rag_documents/` without
  modification; generator and origin are recorded there and in the manifest.
- The Microsoft guide listed in the planning document was a suggested source, not
  silently assumed present. It is **not** included or used for any label in v0.1.

## Regeneration

From the repository root, run:

```powershell
python scripts/prepare_rag_benchmark_corpus.py --download --proxy http://127.0.0.1:7897
```

The proxy flag is optional. This uses only runtime dependencies. Pinned downloads
(including original licenses) are SHA-256 checked before extraction; PDFs/DOCX are
copied from existing fixtures and are not regenerated. Original license line endings
and trailing whitespace are normalized for checked-in text copies.
Without `--download`, original source files must already exist in
`.pytest_cache/benchmark-sources/`. A normal checkout already contains all final
inputs, so regeneration is not needed to run the benchmark.

The script never regenerates question labels. If corpus/parser changes invalidate
Block IDs or quotes, the runner stops before scoring; review labels and bump dataset
and corpus versions instead of auto-relabeling to whatever the retriever returns.
