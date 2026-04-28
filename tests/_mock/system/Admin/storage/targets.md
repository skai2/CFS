# Targets

Location-scoped naming and structural patterns for filing destinations.

---

## Format

Each target specifies the path it applies to and the pattern to follow.

Targets are a user-only artifact. Only the user can create, modify, or remove targets.

Each target includes `created` and `updated` dates for orientation.

---

## Targets

### Archive/*/Finance

- All receipts are filed flat into a `Receipts/` folder. No sub-grouping. (created: 2026-04-10, updated: 2026-04-10)

- Receipt naming format (created: 2026-04-10, updated: 2026-04-10):

  `YYYY-MM-DD - [Beneficiary] - [Payee] - [Currency][Amount] - (Ref YYYY-MM) [Detail].[ext]`

  All fields mandatory except Ref. Use shortest identifiable names.

  - **Beneficiary** — who benefits.
  - **Payee** — who received payment.
  - **Amount** — currency symbol prefix, period as decimal.
  - **Detail** — what the transaction was for.

### Archive/*/Career

- Institution-based groupings are exempt from the 5-item collection threshold. (created: 2026-04-10, updated: 2026-04-10)
