# Scripted protocol-client result

This is deterministic rendering of real MCP responses, not a model conversation.

Disposition: **blocked**
Service: legacy-runner; scope: production/eu; planned: 2026-10-17T12:00:00+00:00.
Known at: 2026-10-17T12:00:00+00:00; revision: `17d8e0c78e34cf797b2dc15c161e49f6c4b3da2b771f3982c642eb5dd8f7a0dd`.
No disposition authorizes shutdown.

## affected_workflows

```json
[
  "monthly-billing",
  "monthly-reporting"
]
```

## dependency_paths

```json
[
  {
    "consumer_id": "invoice-export",
    "assertion_ids": [
      "run-invoice-legacy"
    ],
    "fresh": true
  },
  {
    "consumer_id": "report-job",
    "assertion_ids": [
      "run-report-legacy"
    ],
    "fresh": false
  },
  {
    "consumer_id": "monthly-billing",
    "assertion_ids": [
      "requires-billing-invoice",
      "run-invoice-legacy"
    ],
    "fresh": true
  },
  {
    "consumer_id": "monthly-reporting",
    "assertion_ids": [
      "requires-reporting-report",
      "run-report-legacy"
    ],
    "fresh": false
  }
]
```

## blockers

```json
[
  {
    "kind": "active_dependency",
    "assertion_ids": [
      "requires-billing-invoice"
    ],
    "entity_id": "monthly-billing"
  },
  {
    "kind": "active_dependency",
    "assertion_ids": [
      "run-invoice-legacy"
    ],
    "entity_id": "invoice-export",
    "permissions": [
      {
        "decision_id": "temporary-exception",
        "assertion_id": "permits-invoice",
        "until": "2026-11-01T00:00:00+00:00"
      }
    ]
  },
  {
    "kind": "migration_prerequisite",
    "entity_id": "invoice-migration",
    "assertion_ids": [
      "status-migration-claimed-complete",
      "status-migration-open"
    ]
  },
  {
    "kind": "migration_prerequisite",
    "entity_id": "network-approval",
    "assertion_ids": [
      "status-network-open"
    ]
  }
]
```

## conflicts

```json
[
  {
    "kind": "task_status_conflict",
    "entity_id": "invoice-migration",
    "assertion_ids": [
      "status-migration-claimed-complete",
      "status-migration-open"
    ]
  },
  {
    "kind": "completion_vs_usage",
    "entity_id": "invoice-export",
    "assertion_ids": [
      "status-migration-claimed-complete",
      "run-invoice-legacy"
    ]
  }
]
```

## owners

```json
[
  {
    "entity_id": "invoice-export",
    "owner_id": "data-platform",
    "assertion_id": "owns-invoice"
  },
  {
    "entity_id": "network-approval",
    "owner_id": "security",
    "assertion_id": "owns-network"
  },
  {
    "entity_id": "report-job",
    "owner_id": "data-platform",
    "assertion_id": "owns-report"
  }
]
```

## decisions

```json
[
  {
    "decision_id": "temporary-exception",
    "assertion_id": "permits-invoice",
    "permits_consumer_id": "invoice-export",
    "effective_until": "2026-11-01T00:00:00+00:00"
  }
]
```

## coverage

```json
{
  "gaps": [
    "stale dependency evidence: report-job",
    "stale dependency evidence: monthly-reporting",
    "current owner missing: invoice-migration",
    "consumer verification missing or stale: report-job",
    "conflicting evidence requires verification"
  ],
  "truncated": false,
  "inventory_source": "inventory-initial@1",
  "declared_consumer_count": 2
}
```

## Exact evidence citations

- `blocked-network` — `source-blocked-network@1` / span `blocked-network`: "invoice-migration is blocked by network-approval in production/eu."
- `owns-invoice` — `source-owns-invoice@1` / span `owns-invoice`: "The approved roster assigns invoice-export to data-platform in production/eu."
- `owns-network` — `source-owns-network@1` / span `owns-network`: "The approved roster assigns network-approval to security in production/eu."
- `owns-report` — `source-owns-report@1` / span `owns-report`: "The approved roster assigns report-job to data-platform in production/eu."
- `permits-invoice` — `source-permits-invoice@1` / span `permits-invoice`: "Decision effective 2026-10-01T00:00:00Z through 2026-11-01T00:00:00Z: temporary-exception permits continued use by invoice-export in production/eu."
- `requires-billing-invoice` — `source-requires-billing-invoice@1` / span `requires-billing-invoice`: "Monthly billing requires invoice-export in production/eu."
- `requires-reporting-report` — `source-requires-reporting-report@1` / span `requires-reporting-report`: "Monthly reporting requires report-job in production/eu."
- `run-invoice-legacy` — `source-run-invoice-legacy@1` / span `run-invoice-legacy`: "Configuration observation 2026-10-17T09:00:00Z: invoice-export runs on legacy-runner in production/eu."
- `run-report-legacy` — `source-run-report-legacy@1` / span `run-report-legacy`: "Configuration observation 2026-09-01T09:00:00Z: report-job runs on legacy-runner in production/eu."
- `status-migration-claimed-complete` — `source-status-migration-claimed-complete@1` / span `status-migration-claimed-complete`: "Ticket invoice-migration claims complete in production/eu as of 2026-10-16T12:00:00Z. This ticket is not a runtime verification."
- `status-migration-open` — `source-status-migration-open@1` / span `status-migration-open`: "Ticket invoice-migration is open in production/eu."
- `status-network-open` — `source-status-network-open@1` / span `status-network-open`: "Ticket network-approval is open in production/eu."
- `tracks-invoice-migration` — `source-tracks-invoice-migration@1` / span `tracks-invoice-migration`: "invoice-export migration is tracked by invoice-migration in production/eu."
