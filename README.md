# Fitness Center Management System

## Quick Start

```bash
# Start all services
docker-compose up -d --build

# Seed test data
cd operations-service
python seed_data.py
```

## Access

- **App**: http://localhost:3002
- **Operations API Docs**: http://localhost:8080/docs
- **Grafana**: http://localhost:3000 (admin/admin)