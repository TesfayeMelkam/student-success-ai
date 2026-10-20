# Architecture (Phase 1)

- `config/` project settings split into base / development / production.
- `accounts/` custom `User` (one `role`), `AuditLog`, role decorator, rate-limited login, role dashboards.
- `templates/` one `base.html` with a single `content` block; shell switches between public and signed-in layout.
- `ml/` reserved for the ML package (Phase 3). It will not import Django, so it can be tested alone.

Access control: every protected view uses `@role_required(...)` (HTTP 403 otherwise). Object-level checks
(student sees only own records, teacher only own courses) arrive with the data models in Phase 2.
