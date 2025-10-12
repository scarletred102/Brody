# 🚀 Deploying Brody to Render

## Quick Deploy (Recommended)

### Option 1: Blueprint Deploy (Automated)
1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will read `render.yaml` and set everything up automatically
6. Add your `OPENROUTER_API_KEY` in the Render dashboard after creation

### Option 2: Manual Deploy

#### Step 1: Create PostgreSQL Database
1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `brody-db`
3. Region: Singapore (or nearest to you)
4. Plan: **Free**
5. Click **"Create Database"**
6. Copy the **Internal Database URL** (starts with `postgresql://`)

#### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `brody-backend`
   - **Region**: Singapore (same as database)
   - **Branch**: `Eminence`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd backend && ./start.sh
     ```
   - **Plan**: Free

#### Step 3: Environment Variables
Add these in the Render dashboard (Environment tab):

**Required:**
```
OPENROUTER_API_KEY=sk-or-v1-... (get from openrouter.ai)
DATABASE_URL=(paste Internal Database URL from Step 1)
JWT_SECRET=(click "Generate" in Render UI)
```

**Optional (with defaults):**
```
DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct:free
FALLBACK_MODEL=mistralai/mistral-7b-instruct:free
ONLY_FREE_MODELS=true
PYTHON_VERSION=3.11.0
```

#### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for build and deploy
3. Your API will be live at `https://brody-backend.onrender.com`

---

## 🔍 Troubleshooting

### Deployment Times Out
**Symptom**: "Timed Out" after 15 minutes

**Causes & Fixes:**

1. **Port Binding Issue**
   - ✅ Fixed: `start.sh` now binds to `0.0.0.0:$PORT`
   - Render injects `$PORT` environment variable

2. **Missing Health Check**
   - ✅ Fixed: `/health` endpoint exists in `main.py`
   - Render pings this endpoint to verify deployment

3. **Database Connection Fails**
   - Check `DATABASE_URL` is set correctly
   - Verify database is in same region as web service
   - Check logs: `render.com → your-service → Logs`

4. **Missing Dependencies**
   - ✅ Fixed: All deps in `requirements.txt`
   - Build logs show successful installation

### App Crashes on Startup

**Check logs in Render dashboard:**
```bash
# Look for Python errors like:
# - ImportError (missing dependency)
# - ConnectionError (database unreachable)
# - ValueError (bad environment variable)
```

**Common fixes:**
- Add missing env vars
- Check Python version (should be 3.11+)
- Verify `start.sh` has execute permissions (should be in git)

### Health Check Fails

Test locally first:
```bash
cd backend
export PORT=9000
export DATABASE_URL="sqlite:///./brody.db"
./start.sh
```

Then in another terminal:
```bash
curl http://localhost:9000/health
# Should return: {"status":"healthy"}
```

---

## 🧪 Local Testing (Before Deploy)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Create `.env` File
```bash
cp ../.env.example .env
nano .env  # Add your OPENROUTER_API_KEY
```

### 3. Initialize Database
```bash
python -c "from database import Base, engine; Base.metadata.create_all(engine)"
```

### 4. Start Server
```bash
./start.sh
# Or directly:
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 5. Test Endpoints
```bash
# Health check
curl http://localhost:9000/health

# AI status
curl http://localhost:9000/ai/status

# Mock auth
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

---

## 📊 Post-Deployment Verification

Once deployed, test these endpoints:

```bash
# Replace with your actual Render URL
API_URL="https://brody-backend.onrender.com"

# 1. Health check
curl $API_URL/health

# 2. API status
curl $API_URL/

# 3. AI service status
curl $API_URL/ai/status

# 4. Test AI (if OPENROUTER_API_KEY set)
curl $API_URL/ai/test
```

**Expected responses:**
- `/health` → `{"status":"healthy"}`
- `/` → JSON with version and status
- `/ai/status` → Shows AI configuration
- `/ai/test` → Returns AI-generated test response

---

## 🔒 Security Notes

**For Production:**
1. Set strong `JWT_SECRET` (use Render's "Generate" button)
2. Use environment-specific secrets (don't commit `.env`)
3. Enable CORS restrictions in `main.py`:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```
4. Use PostgreSQL (not SQLite)
5. Add rate limiting
6. Enable HTTPS only

---

## 📝 Render.yaml Explained

```yaml
services:
  - type: web                    # Web service (API)
    runtime: python              # Python 3.11
    buildCommand: ...            # Install dependencies
    startCommand: ./start.sh     # Run startup script
    healthCheckPath: /health     # Render pings this
    autoDeploy: true            # Deploy on git push

databases:
  - type: postgres               # PostgreSQL database
    plan: free                   # Free tier (512MB)
    region: singapore            # Same as web service
```

---

## 🆘 Still Having Issues?

1. **Check Render Logs**:
   - Dashboard → Your Service → Logs tab
   - Look for Python errors or startup failures

2. **Test Locally First**:
   - Run `./start.sh` locally
   - Verify all endpoints work
   - Check environment variables

3. **Common Environment Variables**:
   ```bash
   # Minimum required
   PORT=10000                    # Render provides this
   DATABASE_URL=postgresql://... # From Render database
   
   # Optional but recommended
   OPENROUTER_API_KEY=sk-...    # For AI features
   JWT_SECRET=random-string     # For auth
   ```

4. **Verify Build**:
   - Build should take ~2-3 minutes
   - Deploy should take ~30 seconds
   - If it times out, check logs immediately

---

## 🎯 Next Steps After Deploy

1. **Update Frontend**:
   - Point frontend to `https://your-backend.onrender.com`
   - Update CORS settings in backend

2. **Add Custom Domain** (optional):
   - Render Settings → Custom Domain
   - Add DNS records

3. **Set Up Monitoring**:
   - Render provides basic monitoring
   - Add external: UptimeRobot, Better Uptime

4. **Enable Auto-Deploy**:
   - Already enabled in `render.yaml`
   - Push to GitHub → automatic deploy

---

**Need help?** Check the [Render Docs](https://render.com/docs) or open an issue.
