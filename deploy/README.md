## Deployment (Docker Compose)

### Prereqs (server)
- Docker + Docker Compose plugin installed
- A domain and TLS termination (recommended: Caddy or Nginx)

### Steps
1) Copy production env template:
   - Copy `.env.production.example` → `.env`
   - Fill real values (Supabase/Cloudinary/CORS + public URLs)

2) Deploy:

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### Reverse proxy templates
- **Caddy**: `deploy/reverse-proxy/Caddyfile`
- **Nginx**: `deploy/reverse-proxy/nginx.conf`

Notes:
- Keep Docker Compose at **4 services**; reverse proxy runs outside compose (system package or separate machine).
- Ensure WebSocket upgrade is enabled for `realtime-service`.

