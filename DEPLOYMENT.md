# PolComply Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Heroku (Recommended for Demo)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login to Heroku
heroku login

# Create new app
heroku create polcomply-demo

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set JWT_SECRET=your-secret-key-here

# Deploy
git push heroku main

# Open demo
heroku open
```

### Option 2: Docker (Local/Production)

```bash
# Build and run
docker-compose up -d

# Access application
open http://localhost:8000
```

### Option 3: Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access application
open http://localhost:8000
```

## 📋 Pre-Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Code quality checks (`ruff`, `black`, `mypy`)
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files included
- [ ] Health check endpoint working

## 🔧 Environment Variables

```bash
# Required
ENVIRONMENT=production
JWT_SECRET=your-secret-key-here

# Optional
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 📊 Monitoring

- **Health Check**: `/health`
- **API Docs**: `/docs`
- **Upload Page**: `/`
- **Validation API**: `/api/validate/xml`

## 🚨 Troubleshooting

### Common Issues

1. **Schema not found**: Ensure `FA-3.xsd` is in `backend/schemas/`
2. **Import errors**: Check Python path and dependencies
3. **Port conflicts**: Use different port with `--port 8001`
4. **Static files**: Ensure `static/` directory is included

### Logs

```bash
# Heroku logs
heroku logs --tail

# Docker logs
docker-compose logs -f

# Local logs
tail -f backend/logs/app.log
```

## 🔒 Security Considerations

- Use strong JWT secrets
- Enable HTTPS in production
- Set proper CORS origins
- Validate file uploads
- Rate limit API endpoints

## 📈 Performance Optimization

- Enable GZip compression
- Use CDN for static files
- Implement caching
- Monitor response times
- Optimize database queries

---

**Ready to deploy? Follow the checklist above and your PolComply demo will be live!**
