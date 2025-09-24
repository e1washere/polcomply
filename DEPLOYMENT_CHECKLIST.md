# PolComply Deployment Checklist
## Railway & Render Deployment Guide

---

## ✅ **Pre-Deployment Checklist**

### **Code Quality**
- [ ] All tests passing (`pytest`)
- [ ] Code formatting (`ruff --fix`, `black .`)
- [ ] Type checking (`mypy polcomply`)
- [ ] No linting errors
- [ ] All features tested locally

### **Documentation**
- [ ] README.md updated with demo links
- [ ] API documentation complete
- [ ] Deployment guide ready
- [ ] Sales materials prepared

### **Configuration**
- [ ] Environment variables defined
- [ ] Database configuration ready
- [ ] Static files included
- [ ] Health check endpoint working

---

## 🚀 **Railway Deployment**

### **1. Install Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### **2. Create Railway Project**
```bash
# Initialize Railway project
railway init

# Create new project
railway new polcomply-demo
```

### **3. Configure Environment Variables**
```bash
# Set environment variables
railway variables set ENVIRONMENT=production
railway variables set JWT_SECRET=your-secret-key-here
railway variables set PYTHON_VERSION=3.11
```

### **4. Deploy to Railway**
```bash
# Deploy to Railway
railway up

# Get deployment URL
railway domain
```

### **5. Railway Configuration Files**

**Create `railway.toml`:**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

**Create `nixpacks.toml`:**
```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = [
  "cd backend && pip install -r requirements.txt",
  "cd polcomply && pip install -e ."
]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

---

## 🌐 **Render Deployment**

### **1. Create Render Account**
- Go to [render.com](https://render.com)
- Sign up with GitHub account
- Connect your repository

### **2. Create Web Service**
```bash
# Service configuration
Name: polcomply-demo
Environment: Python 3
Build Command: cd backend && pip install -r requirements.txt && cd ../polcomply && pip install -e .
Start Command: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **3. Environment Variables**
```bash
ENVIRONMENT=production
JWT_SECRET=your-secret-key-here
PYTHON_VERSION=3.11
```

### **4. Render Configuration**

**Create `render.yaml`:**
```yaml
services:
  - type: web
    name: polcomply-demo
    env: python
    buildCommand: cd backend && pip install -r requirements.txt && cd ../polcomply && pip install -e .
    startCommand: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: JWT_SECRET
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11
    healthCheckPath: /health
    autoDeploy: true
```

---

## 🔧 **Deployment Commands**

### **Railway Commands**
```bash
# Deploy to Railway
railway up

# View logs
railway logs

# Open in browser
railway open

# Check status
railway status

# Set custom domain
railway domain add yourdomain.com
```

### **Render Commands**
```bash
# Deploy via Git push
git push origin main

# View logs (in Render dashboard)
# Go to: https://dashboard.render.com

# Check service status
# Go to: https://dashboard.render.com/services
```

---

## 📊 **Post-Deployment Testing**

### **1. Health Check**
```bash
# Test health endpoint
curl https://your-app.railway.app/health
curl https://your-app.onrender.com/health
```

### **2. Upload Page**
```bash
# Test upload page
curl https://your-app.railway.app/
curl https://your-app.onrender.com/
```

### **3. API Validation**
```bash
# Test validation endpoint
curl -X POST "https://your-app.railway.app/api/validate/xml" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.xml"
```

### **4. API Documentation**
```bash
# Test API docs
curl https://your-app.railway.app/docs
curl https://your-app.onrender.com/docs
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   - Check Python version (3.11+)
   - Verify requirements.txt
   - Check build logs

2. **Runtime Errors**
   - Verify environment variables
   - Check application logs
   - Test health endpoint

3. **Static Files**
   - Ensure static/ directory included
   - Check file permissions
   - Verify file paths

4. **Database Issues**
   - Check database connection
   - Verify migrations
   - Test database queries

### **Debug Commands**
```bash
# Railway debugging
railway logs --tail
railway shell

# Render debugging
# Use Render dashboard logs
# Check service metrics
```

---

## 📈 **Monitoring & Analytics**

### **Railway Monitoring**
- Built-in metrics dashboard
- Log aggregation
- Performance monitoring
- Error tracking

### **Render Monitoring**
- Service metrics
- Log aggregation
- Uptime monitoring
- Performance insights

---

## 🔒 **Security Checklist**

- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] CORS configured
- [ ] File upload validation
- [ ] Rate limiting enabled
- [ ] Error handling secure

---

## 🎯 **Success Criteria**

- [ ] Application deploys successfully
- [ ] Health check returns 200
- [ ] Upload page loads correctly
- [ ] API validation works
- [ ] Static files serve properly
- [ ] Error handling works
- [ ] Performance acceptable (<3s response)

---

**🚀 Ready to deploy? Follow the checklist above and your PolComply demo will be live!**

**Next step:** Choose Railway or Render, follow the deployment guide, then test all endpoints to ensure everything works correctly!
