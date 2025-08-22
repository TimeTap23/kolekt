# Digital Ocean App Platform Deployment Guide

## Quick Deployment Commands

### Normal Deployment (Git Push)
```bash
./deploy.sh
# or
git push
```

### Force Rebuild with Cache Clearing
```bash
./deploy.sh force
```

## Prerequisites

### 1. Install doctl CLI
```bash
# macOS
brew install doctl

# Linux
snap install doctl

# Or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/
```

### 2. Authenticate with Digital Ocean
```bash
doctl auth init
# Enter your Digital Ocean API token when prompted
```

## Deployment Options

### Option 1: Normal Deployment
- **Command**: `./deploy.sh` or `git push`
- **What it does**: Pushes changes to git, triggers automatic deployment
- **When to use**: Regular updates, minor changes
- **Pros**: Fast, automatic
- **Cons**: May not clear build cache

### Option 2: Force Rebuild
- **Command**: `./deploy.sh force`
- **What it does**: 
  - Clears build cache
  - Forces complete rebuild
  - Monitors deployment progress
- **When to use**: 
  - After major changes
  - When assets aren't updating
  - After configuration changes
  - When experiencing cache issues
- **Pros**: Guarantees fresh build, clears all caches
- **Cons**: Takes longer, uses more resources

## Common Issues and Solutions

### Issue: Assets Not Updating
**Symptoms**: CSS/JS changes not appearing on live site
**Solution**: Use force rebuild
```bash
./deploy.sh force
```

### Issue: Build Cache Problems
**Symptoms**: Old code still running, deployment stuck
**Solution**: Force rebuild clears all caches
```bash
./deploy.sh force
```

### Issue: Environment Variables Not Applied
**Symptoms**: New env vars not working
**Solution**: Force rebuild ensures env vars are reloaded
```bash
./deploy.sh force
```

## Monitoring Deployment

### Check Deployment Status
```bash
doctl apps list
doctl apps get <app-id>
```

### View Logs
```bash
doctl apps logs <app-id>
doctl apps logs <app-id> --follow
```

### Check App Health
```bash
# Get your app URL
doctl apps get <app-id> --format Status.LiveURL

# Test the endpoint
curl https://your-app-url.ondigitalocean.app/health
```

## Best Practices

### 1. Use Force Rebuild When:
- ✅ Making major UI/UX changes
- ✅ Updating CSS/JS files
- ✅ Changing environment variables
- ✅ Experiencing cache issues
- ✅ After configuration changes

### 2. Use Normal Deployment When:
- ✅ Making minor text changes
- ✅ Updating documentation
- ✅ Small bug fixes
- ✅ Regular updates

### 3. Before Force Rebuilding:
- ✅ Commit all changes to git
- ✅ Test locally if possible
- ✅ Ensure all files are saved

## Troubleshooting

### Deployment Fails
```bash
# Check app status
doctl apps get <app-id>

# View detailed logs
doctl apps logs <app-id> --follow

# Check build logs
doctl apps get <app-id> --format Status.DeploymentLogs
```

### App Not Responding
```bash
# Check if app is running
doctl apps get <app-id> --format Status.Phase

# Restart app
doctl apps create-deployment <app-id>
```

### Cache Issues
```bash
# Force rebuild (recommended)
./deploy.sh force

# Or manually clear cache
doctl apps update <app-id> --spec app.yaml
```

## Environment Variables

### Important Variables for kolekt.io
Make sure these are set in Digital Ocean App Platform:

```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
JWT_SECRET=your_jwt_secret
SECRET_KEY=your_secret_key

# Optional
DEBUG=false
DATABASE_URL=your_database_url
```

### Updating Environment Variables
1. Go to Digital Ocean App Platform dashboard
2. Select your app
3. Go to Settings → Environment Variables
4. Add/update variables
5. **Important**: Use force rebuild after changing env vars
   ```bash
   ./deploy.sh force
   ```

## Performance Tips

### 1. Optimize Build Time
- Use `.dockerignore` to exclude unnecessary files
- Minimize dependencies in `requirements.txt`
- Use multi-stage Docker builds

### 2. Reduce Deployment Frequency
- Batch changes together
- Use feature branches for testing
- Only deploy when necessary

### 3. Monitor Resource Usage
```bash
# Check app metrics
doctl apps get <app-id> --format Status.Metrics
```

## Emergency Procedures

### Rollback to Previous Version
```bash
# List deployments
doctl apps list-deployments <app-id>

# Rollback to specific deployment
doctl apps create-deployment <app-id> --deployment-id <deployment-id>
```

### Complete App Reset
```bash
# Delete and recreate app (use with caution)
doctl apps delete <app-id>
# Then recreate through Digital Ocean dashboard
```

## Support

### Digital Ocean Resources
- [App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [Community Support](https://www.digitalocean.com/community/)

### Common Commands Reference
```bash
# List all apps
doctl apps list

# Get app details
doctl apps get <app-id>

# View app logs
doctl apps logs <app-id>

# Create new deployment
doctl apps create-deployment <app-id>

# Update app spec
doctl apps update <app-id> --spec app.yaml
```

---

**Remember**: When in doubt, use `./deploy.sh force` to ensure a clean deployment with cleared caches!
