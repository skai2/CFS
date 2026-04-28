# Entities

What qualifies as an entity and how to determine which entity an item belongs to.

---

## What is an entity

An entity is anything with an independent administrative life — it can own records regardless of who currently manages it. Entities are the primary organizers for Archive and Projects.

## Independence test

Does this thing have administrative continuity that persists independently? Two questions:

1. **Can this record exist without entity X?** If the record is tied to a thing and would follow it to a new owner, it belongs to that thing's entity.
2. **Can entity X exist without entity Y?** If yes, they are separate entities.

### Passes (independent entities)

| Entity type | Example | Why it passes |
|---|---|---|
| Person | John Doe | Has identity, finances, health, career — all independent |
| Organization | Acme Corp | Tax obligations, contracts, expenses persist regardless of who owns it |
| Family | The Smiths | Shared expenses and records exist independent of individual members |
| Property | Riverside Apt | Utility bills, tax records, maintenance transfer with the property |
| Vehicle | A car | Registration, insurance, maintenance follow the vehicle across owners |

### Fails (not independent — belongs to a person's entity)

| Thing | Why it fails | Where it goes |
|---|---|---|
| Bank account | Ceases when closed — no independent life | Account holder's entity (Assets) |
| Digital subscription | Ceases when cancelled | Subscriber's entity (Assets) |
| Purchased item | A toothbrush receipt is the buyer's record | Buyer's entity (Finance) |
| Email account | Ceases without the user | User's entity (Assets) |

## Determining the entity

When filing an item:

1. **Ask: who or what is this record for?** Not who created, sent, or paid for it. A business tax payment belongs to the business even if paid from a personal account. A property utility bill belongs to the property even if the owner paid it.

2. **Check the filesystem for existing entities.** Before creating a new entity, inspect all configured locations for the class (see `refs/storage/routing.md` multi-location awareness). Match the item to an existing entity where possible — avoid creating duplicates or near-matches (e.g., "John" when "John Doe" already exists).

3. **Apply the independence test if uncertain.** When you're unsure whether something is its own entity or belongs to an existing one, apply the two questions above.

## Entity naming

Entities are named by identity, not by relationship. Use the shortest unambiguous name — `John` not `My Brother`, `Riverside` not `My Apartment`. Add detail only for disambiguation. See `refs/storage/naming.md` for full naming conventions.
