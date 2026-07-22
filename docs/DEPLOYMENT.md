# Universal Media Downloader - Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Option 1: GitHub Pages (Free, Static Only)](#option-1-github-pages-free-static-only)
- [Option 2: Vercel (Free Tier Available)](#option-2-vercel-free-tier-available)
- [Option 3: Railway (Free Tier Available)](#option-3-railway-free-tier-available)
- [Option 4: Render (Free Tier Available)](#option-4-render-free-tier-available)
- [Option 5: DigitalOcean App Platform](#option-5-digitalocean-app-platform)
- [Option 6: AWS/GCP/Azure](#option-6-awsgcpazure)
- [Custom Domain Setup](#custom-domain-setup)
- [Environment Variables](#environment-variables)
- [Post-Deployment Checklist](#post-deployment-checklist)

## Overview

To get a custom domain like `universalmediadownloader.com`, you need to:

1. **Purchase a domain** from a registrar (Namecheap, GoDaddy, Google Domains, etc.)
2. **Deploy your application** to a hosting service
3. **Configure DNS** to point your domain to the hosting service
4. **Set up SSL** for HTTPS

**Estimated Costs:**
- Domain: ~$10-15/year
- Hosting: Free (with limitations) to $5-20/month

---

## Option 1: GitHub Pages (Free, Static Only)

**Limitation:** GitHub Pages only hosts static sites. Since this is a Python/FastAPI app, this option won't work for the full application.

**Alternative:** Host only the frontend on GitHub Pages and deploy the backend separately.

---

## Option 2: Vercel (Free Tier Available)

### Step 1: Prepare Your Project

Create a `vercel.json` file in your project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Step 2: Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd c:\Users\Omart\OneDrive\Desktop\wensite\universal-media-downloader
   vercel
   ```

3. **Follow the prompts:**
   - Set up and deploy? Yes
   - Which scope? Your account
   - Link to existing project? No
   - Project name? universal-media-downloader
   - Directory? ./
   - Override settings? No

4. **Your app will be live at:** `https://universal-media-downloader.vercel.app`

### Step 3: Add Custom Domain

1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Domains
4. Add your domain: `universalmediadownloader.com`
5. Vercel will show you DNS records to add

### Step 4: Configure DNS at Your Registrar

Add these records at your domain registrar:

```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

---

## Option 3: Railway (Free Tier Available)

### Step 1: Prepare Your Project

Create a `railway.toml` file:

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

Create a `nixpacks.toml` file:

```toml
[phases.setup]
nixPkgs = ["python310", "ffmpeg"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python main.py"
```

### Step 2: Deploy to Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   cd c:\Users\Omart\OneDrive\Desktop\wensite\universal-media-downloader
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Your app will be live at:** `https://universal-media-downloader.up.railway.app`

### Step 3: Add Custom Domain

1. Go to Railway dashboard
2. Select your project
3. Go to Settings → Domains
4. Add your custom domain
5. Railway will provide DNS records

### Step 4: Configure DNS

```
Type: CNAME
Name: @
Value: your-project.up.railway.app

Type: CNAME
Name: www
Value: your-project.up.railway.app
```

---

## Option 4: Render (Free Tier Available)

### Step 1: Prepare Your Project

Create a `render.yaml` file:

```yaml
services:
  - type: web
    name: universal-media-downloader
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    healthCheckPath: /api/v1/health
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 8000
```

### Step 2: Deploy to Render

1. **Push your code to GitHub** (already done!)
2. **Go to:** https://dashboard.render.com
3. **Click "New +"** → "Web Service"
4. **Connect your GitHub repository**
5. **Configure:**
   - Name: `universal-media-downloader`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
6. **Click "Create Web Service"**

7. **Your app will be live at:** `https://universal-media-downloader.onrender.com`

### Step 3: Add Custom Domain

1. Go to Render dashboard
2. Select your service
3. Go to Settings → Custom Domains
4. Add your domain
5. Render will show DNS records

### Step 4: Configure DNS

```
Type: CNAME
Name: @
Value: universal-media-downloader.onrender.com

Type: CNAME
Name: www
Value: universal-media-downloader.onrender.com
```

---

## Option 5: DigitalOcean App Platform

### Step 1: Deploy to DigitalOcean

1. **Go to:** https://cloud.digitalocean.com/apps
2. **Click "Create App"**
3. **Connect your GitHub repository**
4. **Configure:**
   - App name: `universal-media-downloader`
   - Region: Choose closest to you
   - Plan: Basic ($5/month) or Starter (Free tier available)
   - HTTP Port: `8000`
   - Run Command: `python main.py`
5. **Click "Create Resources"**

### Step 2: Add Custom Domain

1. Go to your app in DigitalOcean
2. Go to Settings → Domains
3. Add your domain
4. DigitalOcean will provide DNS records

### Step 3: Configure DNS

```
Type: A
Name: @
Value: [DigitalOcean will provide IP]

Type: CNAME
Name: www
Value: [your-app].ondigitalocean.app
```

---

## Option 6: AWS/GCP/Azure

### AWS (Elastic Beanstalk)

**Cost:** ~$10-30/month (Free tier available for 12 months)

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize:**
   ```bash
   cd c:\Users\Omart\OneDrive\Desktop\wensite\universal-media-downloader
   eb init -p python universal-media-downloader
   ```

3. **Create environment:**
   ```bash
   eb create universal-media-downloader-env
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

### Google Cloud Platform (Cloud Run)

**Cost:** Free tier available, then ~$5/month

1. **Install gcloud CLI**
2. **Deploy:**
   ```bash
   gcloud run deploy universal-media-downloader \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

## Custom Domain Setup

### Step 1: Purchase a Domain

**Recommended Registrars:**
- **Namecheap** (https://www.namecheap.com) - ~$9/year
- **GoDaddy** (https://www.godaddy.com) - ~$12/year
- **Google Domains** (https://domains.google.com) - ~$12/year
- **Cloudflare Registrar** (https://www.cloudflare.com/products/registrar/) - Cost price

**Search for your domain:**
- `universalmediadownloader.com`
- `universal-media-downloader.com`
- `mediadownloader.app`
- `umdl.app`

### Step 2: Configure DNS

After purchasing, go to your registrar's DNS management and add records based on your hosting provider (see options above).

**Example for Vercel:**
```
A Record:
- Host: @
- Value: 76.76.21.21
- TTL: Automatic

CNAME Record:
- Host: www
- Value: cname.vercel-dns.com
- TTL: Automatic
```

### Step 3: Enable HTTPS

Most hosting providers (Vercel, Railway, Render) automatically provide SSL certificates. If not:

**Using Let's Encrypt (Free):**
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d universalmediadownloader.com -d www.universalmediadownloader.com
```

---

## Environment Variables

Create a `.env` file for production:

```env
# Application
APP_NAME=Universal Media Downloader
APP_VERSION=1.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# CORS (update with your domain)
CORS_ORIGINS=https://universalmediadownloader.com,https://www.universalmediadownloader.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Download
DOWNLOAD_PATH=./downloads
MAX_FILE_SIZE_MB=500
DOWNLOAD_TIMEOUT=300

# yt-dlp
YTDLP_PATH=yt-dlp
FFMPEG_PATH=ffmpeg
```

---

## Post-Deployment Checklist

- [ ] **Test the live website** - Visit your domain
- [ ] **Test API endpoints** - Check `/docs` and `/api/v1/health`
- [ ] **Test downloads** - Try downloading a video
- [ ] **Enable HTTPS** - Ensure SSL is working
- [ ] **Set up monitoring** - Add uptime monitoring (UptimeRobot, Pingdom)
- [ ] **Configure backups** - If using a database
- [ ] **Set up logging** - Monitor errors and performance
- [ ] **Add analytics** - Google Analytics or similar
- [ ] **Test on mobile** - Ensure responsive design works
- [ ] **Performance test** - Use Lighthouse or PageSpeed Insights

---

## Recommended Stack for Production

**Best Option for Your Project:**

1. **Hosting:** Railway or Render (free tier, easy deployment)
2. **Domain:** Namecheap (~$9/year)
3. **SSL:** Automatic (provided by hosting)
4. **CDN:** Automatic (provided by hosting)
5. **Monitoring:** UptimeRobot (free)

**Total Cost:** ~$9/year (domain only)

---

## Quick Start - Recommended Path

### 1. Deploy to Railway (5 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd c:\Users\Omart\OneDrive\Desktop\wensite\universal-media-downloader
railway init
railway up
```

### 2. Buy Domain (5 minutes)

1. Go to https://www.namecheap.com
2. Search for `universalmediadownloader.com`
3. Add to cart and checkout
4. Complete purchase

### 3. Connect Domain (5 minutes)

1. In Railway dashboard, go to Settings → Domains
2. Add `universalmediadownloader.com`
3. Copy DNS records
4. Go to Namecheap → Domain List → Manage → Advanced DNS
5. Add the DNS records provided by Railway
6. Wait 5-10 minutes for propagation

### 4. Test

Visit: https://universalmediadownloader.com

---

## Troubleshooting

### Domain Not Working

- **Wait 24-48 hours** for DNS propagation
- Check DNS records are correct
- Use https://dnschecker.org to verify propagation

### SSL Certificate Issues

- Most hosts provide automatic SSL
- If not, use Cloudflare (free SSL)
- Ensure port 443 is open

### Application Errors

- Check logs in hosting dashboard
- Ensure all environment variables are set
- Verify yt-dlp and ffmpeg are installed (if needed)

---

## Support

If you need help with deployment:
- Check the hosting provider's documentation
- Open an issue on GitHub: https://github.com/Sindbad-bee/Universal-Media-Downloader/issues

---

**Last Updated:** 2024
**Maintained By:** Universal Media Downloader Contributors