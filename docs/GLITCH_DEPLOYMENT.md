# Deploy to Glitch (100% Free, No Credit Card)

## What is Glitch?

Glitch is a free hosting platform that lets you deploy web apps instantly. It's perfect for this project because:
- ✅ 100% free (no credit card)
- ✅ Deploys directly from GitHub
- ✅ Gives you an instant public link
- ✅ Auto-updates when you push to GitHub
- ✅ 4000 hours/month free (enough for 24/7 hosting)

---

## Step-by-Step Deployment Guide

### Step 1: Go to Glitch

**Open this link in your browser:**
```
https://glitch.com
```

---

### Step 2: Sign Up (30 seconds)

1. Click **"Sign Up"** (top right)
2. Click **"Sign up with GitHub"**
3. Authorize Glitch to access your GitHub
4. **No credit card required!**

---

### Step 3: Import Your Project (1 minute)

1. After signing up, you'll see your dashboard
2. Click **"New Project"** button (top right)
3. Select **"Import from GitHub"**
4. Paste your GitHub repository URL:
   ```
   https://github.com/Sindbad-bee/Universal-Media-Downloader
   ```
5. Click **"OK"**

---

### Step 4: Wait for Import (1-2 minutes)

Glitch will:
1. Clone your repository
2. Detect it's a Python project
3. Install dependencies from requirements.txt
4. Start your app

**You'll see logs in the "Logs" panel on the right.**

---

### Step 5: Configure the Start Command

Once imported, you need to set the start command:

1. Look for a file called **`.glitch.json`** or **`package.json`**
2. If it exists, edit the `"start"` command to:
   ```json
   "start": "python main.py"
   ```

3. If it doesn't exist, create a file called **`package.json`** in the root:
   ```json
   {
     "name": "universal-media-downloader",
     "version": "1.0.0",
     "description": "Universal Media Downloader",
     "scripts": {
       "start": "python main.py"
     }
   }
   ```

4. **Save the file** (Ctrl+S)

---

### Step 6: Set Environment Variables

1. Click the **"Share"** button (top right)
2. Click **"Environment Variables"**
3. Add these variables:

   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.11.0` |
   | `PORT` | `8000` |

4. Click **"Add"** for each
5. Click **"Done"**

---

### Step 7: Start the App

1. Look at the bottom of the screen
2. You should see a **"Share"** button with a URL
3. Click **"Share"** → **"Live Site"**
4. Your app will start automatically

**If it doesn't start automatically:**
- Click the **"Tools"** button (bottom left)
- Click **"Terminal"**
- Type: `python main.py`
- Press Enter

---

### Step 8: Get Your Public Link! 🎉

Once the app is running, you'll see:

**Your live link:**
```
https://universal-media-downloader.glitch.me
```

**Or it might be:**
```
https://your-project-name.glitch.me
```

**This is your FREE, public website link!**

---

## 🎯 What to Expect:

### First Load (30-60 seconds):
- Glitch needs to "wake up" your app
- You'll see "Booting..." in the logs
- Wait for "Application started successfully"

### Subsequent Loads (instant):
- Once awake, it's fast
- Stays awake for 5 minutes of inactivity
- Sleeps after 5 minutes (wakes up on next visit)

---

## 📊 Monitoring Your App:

### View Logs:
- Click **"Logs"** button (bottom)
- See real-time application logs
- Monitor errors and requests

### View Console:
- Click **"Tools"** → **"Console"**
- Run commands if needed

### Share Your App:
- Click **"Share"** → **"Live Site"**
- Copy the URL
- Share with anyone!

---

## 🔧 Troubleshooting:

### App Won't Start:

**Check the logs:**
- Look for error messages in the "Logs" panel
- Common issues:
  - Missing dependencies → Glitch auto-installs from requirements.txt
  - Wrong start command → Make sure it's `python main.py`
  - Port issues → Make sure PORT=8000 is set

**Fix:**
1. Click **"Tools"** → **"Terminal"**
2. Run: `pip install -r requirements.txt`
3. Run: `python main.py`

### App Crashes:

**Check logs for errors:**
- Look for traceback messages
- Common issues:
  - yt-dlp not installed → Glitch should install it
  - ffmpeg not available → This is OK, app will still work

**Solution:**
The app is designed to work even if yt-dlp/ffmpeg are not available. It will show a warning but still function.

### Link Not Working:

1. Make sure app is running (check logs)
2. Wait 30 seconds for first load
3. Try refreshing the page
4. Check if you're using the correct URL

---

## 🚀 Advanced Configuration:

### Auto-Deploy from GitHub:

Glitch automatically updates when you push to GitHub:
1. Make changes to your code locally
2. Commit and push to GitHub
3. Glitch automatically pulls and redeploys
4. Your live site updates instantly!

### Custom Domain (Optional):

1. Click **"Share"** → **"Custom Domains"**
2. Add your domain (e.g., `universalmediadownloader.com`)
3. Update DNS at your domain registrar
4. **Note:** Custom domains require Glitch's paid plan ($8/month)

---

## 💡 Pro Tips:

1. **Keep your project awake:**
   - Use a service like UptimeRobot to ping your app every 5 minutes
   - This prevents it from sleeping

2. **Monitor usage:**
   - Check "Project Stats" in Glitch
   - Make sure you stay under 4000 hours/month

3. **Share your project:**
   - Click "Share" → "Code"
   - Others can see your code and remix it

4. **Backup your data:**
   - Glitch doesn't persist data permanently
   - Use external database if needed (PostgreSQL, MongoDB)

---

## 📋 Quick Checklist:

- [ ] Sign up at https://glitch.com
- [ ] Import from GitHub: `Sindbad-bee/Universal-Media-Downloader`
- [ ] Set start command: `python main.py`
- [ ] Set environment variables (PYTHON_VERSION=3.11.0, PORT=8000)
- [ ] Start the app
- [ ] Get your link: `https://universal-media-downloader.glitch.me`
- [ ] Test the link in your browser
- [ ] Share with the world! 🎉

---

## 🎉 Your Link Will Be:

```
https://universal-media-downloader.glitch.me
```

**Follow the steps above and you'll have your live website in 3 minutes!**

---

## Need Help?

- **Glitch Help:** https://glitch.com/help
- **Your GitHub Repo:** https://github.com/Sindbad-bee/Universal-Media-Downloader
- **Local Server:** http://localhost:8000

**Good luck! Your Universal Media Downloader will be live soon!** 🚀