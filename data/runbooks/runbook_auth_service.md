# RUNBOOK: Authentication Service Troubleshooting

## Overview
Procedures for diagnosing and resolving authentication service issues including login failures, token validation errors, and service outages.

## Symptoms
- Users unable to log in
- 401 Unauthorized errors
- "Invalid token" errors
- JWT validation failures
- Authentication service health check failures

## Prerequisites
- Access to authentication service logs
- Redis access (for token cache)
- Service restart permissions
- Configuration management access

## Diagnosis Steps

### Step 1: Check Service Health
```bash
# Check service status
curl http://auth-service:8080/health

# Check service logs
tail -f /var/log/auth-service/auth.log
```

### Step 2: Verify JWT Configuration
```bash
# Check current JWT configuration
cat /etc/auth-service/application.yml | grep -A 10 jwt
```

Verify:
- Signing algorithm (HS256 or RS256)
- Secret key is set
- Token expiration times

### Step 3: Test Token Generation
```bash
# Generate test token
curl -X POST http://auth-service:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

### Step 4: Validate Token
```bash
# Decode JWT token (without verification)
echo "YOUR_TOKEN" | cut -d'.' -f2 | base64 -d | jq
```

## Common Issues and Solutions

### Issue 1: Invalid Token Type Error

**Symptoms:**
- "Invalid token type" in logs
- All token validations failing

**Resolution:**
1. Check JWT signing algorithm mismatch
2. Verify token format (should be: header.payload.signature)
3. Ensure signing key matches between generation and validation

```java
// Verify configuration
@Value("${jwt.signing.algorithm}")
private String signingAlgorithm; // Should match token generation

@Value("${jwt.secret}")
private String secret; // Must be same across all instances
```

### Issue 2: Token Expired

**Symptoms:**
- "Token expired" errors
- Users logged out unexpectedly

**Resolution:**
1. Check token expiration configuration
2. Verify server time synchronization (NTP)
3. Clear expired tokens from cache

```bash
# Clear Redis token cache
redis-cli FLUSHDB
```

### Issue 3: Service Unresponsive

**Symptoms:**
- Health check failures
- No response from service
- High CPU/memory usage

**Resolution:**
1. Check service logs for errors
2. Restart service if necessary
3. Verify database connectivity

```bash
# Restart authentication service
sudo systemctl restart auth-service

# Check resource usage
top -p $(pgrep -f auth-service)
```

## Resolution Steps

### Immediate Actions

1. **Verify Service is Running**
   ```bash
   systemctl status auth-service
   ```

2. **Check Recent Configuration Changes**
   ```bash
   git log -5 --oneline config/auth-service/
   ```

3. **Review Error Logs**
   ```bash
   grep -i error /var/log/auth-service/auth.log | tail -100
   ```

### Configuration Fixes

1. **Update JWT Configuration**
   ```yaml
   # application.yml
   jwt:
     secret: ${JWT_SECRET}
     signing:
       algorithm: HS256  # or RS256
     expiration:
       access-token: 3600000  # 1 hour
       refresh-token: 86400000  # 24 hours
   ```

2. **Restart Service**
   ```bash
   sudo systemctl restart auth-service
   ```

3. **Clear Token Cache**
   ```bash
   redis-cli -h redis-host -p 6379 FLUSHDB
   ```

## Verification

1. Test login with valid credentials
2. Verify token generation and validation
3. Check service health endpoint
4. Monitor error rates for 30 minutes
5. Confirm user reports of successful logins

## Rollback Plan

If issues persist:
1. Revert to previous configuration version
2. Restart all auth service instances
3. Clear all caches
4. Notify users of temporary service interruption

## Monitoring

Set up alerts for:
- Authentication failure rate > 5%
- Service response time > 1 second
- Health check failures
- Token validation errors

## Post-Incident

- Update configuration management
- Review and test JWT library updates
- Document any configuration changes
- Update monitoring thresholds
