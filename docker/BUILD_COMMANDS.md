# Push ke Docker Hub Private Repository

Repository: **irfan33/koperasi-webshop** (PRIVATE)

---

## Quick Start (Menggunakan Script)

```bash
# Jalankan script otomatis
cd /Users/irfanafifi/Developments/frappe_docker/development/frappe-bench/apps/webshop/docker
./build-and-push.sh
```

Script akan otomatis:

1. Login ke Docker Hub
2. Build image dengan 3 tags (latest, version, git SHA)
3. Push semua tags ke Docker Hub

---

## Manual Commands

### 1. Login Docker Hub (Required untuk Private Repo)

```bash
docker login

# Enter credentials:
# Username: irfan33
# Password: [your Docker Hub password]
```

### 2. Build Image

```bash
cd /Users/irfanafifi/Developments/frappe_docker/development/frappe-bench/apps/webshop/docker

# Build dengan multiple tags
docker build \
  -f Containerfile \
  -t irfan33/koperasi-webshop:latest \
  -t irfan33/koperasi-webshop:v1.0.0 \
  .
```

### 3. Push ke Docker Hub

```bash
# Push semua tags sekaligus
docker push irfan33/koperasi-webshop --all-tags

# Atau satu per satu
docker push irfan33/koperasi-webshop:latest
docker push irfan33/koperasi-webshop:v1.0.0
```

---

## GitHub Actions Setup (Auto Build & Push)

### Required Secrets

Di GitHub repository settings, tambahkan:

**Settings → Secrets and variables → Actions → New repository secret**

| Secret Name       | Value                        |
| ----------------- | ---------------------------- |
| `DOCKERHUB_TOKEN` | Access token dari Docker Hub |

> **Note:** Username `irfan33` sudah hardcoded di workflow, jadi hanya perlu token.

### Create Docker Hub Access Token

1. Login ke https://hub.docker.com
2. Account Settings → Security
3. Click "New Access Token"
4. Description: `GitHub Actions - webshop`
5. Access permissions: **Read, Write, Delete**
6. Generate
7. **Copy token** (ditampilkan sekali saja!)
8. Add ke GitHub Secrets dengan nama `DOCKERHUB_TOKEN`

### Trigger Auto Build

```bash
# Push ke main atau dev akan trigger auto build
git add .
git commit -m "feat: docker setup complete"
git push origin main
```

Check progress di: **GitHub → Actions tab**

---

## Pull dari Docker Hub (Production/Staging)

### Login di Server Production

```bash
# Login dengan credentials yang sama
docker login

# Pull image
docker pull irfan33/koperasi-webshop:latest
```

### Update docker-compose.yml

```yaml
services:
  backend:
    image: irfan33/koperasi-webshop:latest
    # ... rest of config
```

### Run

```bash
docker-compose pull
docker-compose up -d
```

---

## Verify

### Check local images

```bash
docker images | grep koperasi-webshop
```

### Check Docker Hub

```bash
# Via CLI
docker search irfan33/koperasi-webshop

# Via Web
https://hub.docker.com/r/irfan33/koperasi-webshop
```

### Test run

```bash
docker run --rm irfan33/koperasi-webshop:latest bench --version
```

---

## Troubleshooting

### "unauthorized: authentication required"

**Solution:** Login dulu

```bash
docker login
# Enter username: irfan33
# Enter password: [your password]
```

### "denied: requested access to the resource is denied"

**Cause:** Repository private, belum login atau credentials salah

**Solution:**

1. Pastikan sudah `docker login`
2. Check username/password benar
3. Pastikan punya akses ke `irfan33/koperasi-webshop`

### GitHub Actions failed: "unauthorized"

**Cause:** `DOCKERHUB_TOKEN` tidak valid atau expired

**Solution:**

1. Generate token baru di Docker Hub
2. Update GitHub Secret `DOCKERHUB_TOKEN`
3. Re-run workflow

---

## Tags yang Akan Dibuat

| Tag          | Description                   | Example                                 |
| ------------ | ----------------------------- | --------------------------------------- |
| `latest`     | Latest dari branch main       | `irfan33/koperasi-webshop:latest`       |
| `main-<sha>` | Main branch dengan commit SHA | `irfan33/koperasi-webshop:main-a1b2c3d` |
| `dev`        | Latest dari branch dev        | `irfan33/koperasi-webshop:dev`          |
| `dev-<sha>`  | Dev branch dengan commit SHA  | `irfan33/koperasi-webshop:dev-a1b2c3d`  |

---

## Quick Reference

```bash
# Login
docker login

# Build
cd docker/
docker build -f Containerfile -t irfan33/koperasi-webshop:latest .

# Push
docker push irfan33/koperasi-webshop:latest

# Pull (di server lain)
docker pull irfan33/koperasi-webshop:latest
```
