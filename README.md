# Task 2 Demo App — Docker Multi-Stage Containerization

A small FastAPI + PostgreSQL app built to practice:
- Multi-stage Dockerfiles (small, clean final image)
- Environment-variable-based config (no hardcoded secrets)
- Container port mapping (app <-> host, app <-> db)

## Project structure
```
task2-demo/
├── main.py              # FastAPI app (health + items endpoints)
├── requirements.txt      # Python dependencies
├── Dockerfile            # multi-stage build (builder + runtime)
├── docker-compose.yml    # app + postgres, wired together
├── .env.example           # copy to .env and fill in
└── .dockerignore
```

## 1. Set up environment variables
```bash
cp .env.example .env
# edit .env if you want different values — defaults work fine locally
```

## 2. Build and run
```bash
docker compose up --build
```
This builds the multi-stage image for `app` and starts both containers.

## 3. Test it
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"first item"}'
curl http://localhost:8000/items
```

## 4. Check the image size (this is your "optimization" evidence)
```bash
docker images | grep task2-demo
```
For comparison, try building a single-stage version (put everything —
gcc, libpq-dev, pip cache — in one `FROM python:3.11-slim` stage with no
second stage) and run the same command. Note the size difference — that
gap *is* the point of Task 2.

## 5. Useful commands for your report
```bash
docker compose ps                 # shows both containers running
docker images                     # image size comparison
docker inspect <container> --format='{{.Config.ExposedPorts}}'  # port config
docker compose down -v            # tear down + remove the db volume
```


