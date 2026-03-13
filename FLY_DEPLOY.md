# Blue Plaques - Fly.io Deployment

## Prerequisites
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login
```

## Deploy

### 1. Create volume for database
```bash
flyctl volumes create blue_plaques_data --region jnb --size 1
```

### 2. Set secrets
```bash
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)
flyctl secrets set ADMIN_EMAIL=admin@blueplaques.co.za
flyctl secrets set ADMIN_PASSWORD=your-secure-password
```

### 3. Deploy
```bash
flyctl deploy
```

### 4. Open app
```bash
flyctl open
```

## Update deployment
```bash
flyctl deploy
```

## View logs
```bash
flyctl logs
```

## SSH into machine
```bash
flyctl ssh console
```

## Scale (if needed)
```bash
# Increase memory
flyctl scale memory 512

# Add more machines
flyctl scale count 2
```

## Cost
- Free tier: 3 shared-cpu VMs (256MB each)
- 3GB persistent storage included
- **This app uses 1 VM + 1GB storage = FREE**

## Custom domain (optional)
```bash
flyctl certs add blueplaques.co.za
# Add DNS: CNAME @ -> blue-plaques.fly.dev
```
