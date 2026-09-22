# DOCX style convergence checkpoint — 2026-09-22

## Exact start

Refresh current `main` and re-prove the unchanged style candidate before any further styling work.

Current main at branch cut:
`6c6d40e32c204a496e472f88a4bf9f81c16824ff`

The prior style MIP control began at:
`d295d8af67d513bd13cbbf05dd8ce11d1958dd92`

There are 18 intervening commits. They include changes to the data-rich render workflow and its test surface, so a fresh exact-current proof is justified even though the style tokens themselves have not changed.

## Frozen authority

Accepted user-approved baseline remains:
- DOCX: `e936ffcb89eb7da13b8be8d447c8453b5b4499a4907390816846f5c8ec94a6b9`
- PDF: `654e74630861b5b398ab577d55da5f692bf4549b0af480498822428109353b02`

Candidate:
`QPS_TECH_GRAPHITE_TEAL_COPPER_V1`

## Convergence rule

If current-head CI is green, do not open another repair wave. Close proof freshness and return to `USER_STYLE_REVIEW`.

If an executed step fails, repair only that exact current first-red.

Zero-step queue/admission states do not authorize code repair.

authority_transfer=false
formal_credit_delta=0
