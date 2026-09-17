# Hermes maintenance review

Mobile-first, public-safe summary of the 2026-09-17 audit and subsequent authorized cleanup.

- `report.json`: manually reviewed, redacted findings and completion boundaries
- `build.py`: dependency-free static HTML generator
- `index.html`: generated page

Build with `python3 build.py`.

Reviewed source/patch and knowledge changes were installed and independently tested. After the user restarted the Gateway, the new worker identity was verified, real Telegram text/SRT round trips passed, and the existing cron job completed a read-only delivery test. The user completed the official service refresh; the parent verified the regenerated and loaded launchd definition, fresh worker identity and Telegram connectivity. The stale-service and pending-restart warnings are no longer present.

Raw configuration, logs, credentials, account identifiers and private evidence remain excluded. This is a point-in-time report, not a live dashboard or a guarantee of zero regressions. See the final section for unperformed work and known limitations.

## Follow-up: browser and dependency audit

`browser-dependencies/` is a separate mobile-first public summary of the subsequent read-only audit. The root page preserves the earlier accepted cleanup history; its completion status does not apply to this follow-up.

- `browser-dependencies/report.json`: manually selected and redacted public data, public advisory URLs, and explicit state fields.
- `browser-dependencies/build.py`: dependency-free deterministic generator; reads only its public data, never the private audit evidence.
- `browser-dependencies/index.html`: generated subpage, with expandable package details and source links.

Build with `python3 browser-dependencies/build.py`, then `python3 build.py` for the root navigation. Package/advisory totals are derived from the public dataset. The browser and scan counts are point-in-time observations from the private audit, not a live inventory.

Current follow-up state: **audit complete; staged compatibility tests and parent offline reproduction passed (207 passed, 3 skipped); dependency remediation not deployed, pending an external maintenance window; 13 ended-lineage disconnected daemons stopped individually, 110 retained**. No dependency upgrade is represented as deployed. Retained browser/control processes were read back; RSS accounting is not a physical-memory recovery measurement. Update the subpage's `state` data together with the evidence and copy when work advances; state labels in the hero, next-steps section and footer derive from that data.

Both pages request `noindex,nofollow`. They remain public: **noindex is not access control**. Do not publish raw audit Markdown, scanner output, local paths, account/session identifiers, environment, commands, configuration or logs. Private QA artifacts stay in the ignored `private/` directory. Local build/QA does not publish the subpage; public payload review and commit/push are a separate step.
