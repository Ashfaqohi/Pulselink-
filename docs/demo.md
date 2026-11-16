# Deployment demo

The repository includes a reproducible container demo. With Docker Desktop or
another Docker daemon running, execute from the repository root:

```bash
./scripts/demo.sh
```

The script builds and starts the frontend, API, persistent database volume,
Prometheus, Alertmanager, and Grafana; creates a demo short URL through the
frontend-facing API; and verifies the redirect response. Open the printed
frontend URL to inspect the UI. Stop the demo with:

```bash
docker compose down
```

For a public deployment, configure the AWS/GitHub secrets described in
[deployment.md](deployment.md), run the protected `Deploy` workflow, and set
`HEALTHCHECK_URL` to the resulting public application URL. The repository does
not claim a public URL until that workflow has actually completed its health
and user-impact checks.
