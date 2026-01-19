# RUNBOOK: Database Connection Timeout Resolution

## Overview
This runbook provides step-by-step procedures for diagnosing and resolving database connection timeout issues.

## Symptoms
- API responses timing out (>30 seconds)
- "Connection timeout" errors in application logs
- "Too many connections" errors in database logs
- Connection pool exhausted messages
- 500 Internal Server Error responses

## Prerequisites
- Access to application servers
- Database admin credentials
- Monitoring dashboard access
- Deployment permissions (if code changes needed)

## Diagnosis Steps

### Step 1: Check Connection Pool Status
```bash
# Check current connection pool metrics
curl http://localhost:8080/actuator/metrics/hikaricp.connections.active
curl http://localhost:8080/actuator/metrics/hikaricp.connections.total
```

Expected: Active connections should be < 80% of total pool size

### Step 2: Review Application Logs
```bash
# Search for connection timeout errors
grep -i "connection timeout" /var/log/application/app.log | tail -50
grep -i "connection pool" /var/log/application/app.log | tail -50
```

### Step 3: Check Database Connection Count
```sql
-- For PostgreSQL
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';

-- For MySQL
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

### Step 4: Identify Connection Leaks
Look for:
- Long-running queries (>60 seconds)
- Idle transactions
- Connections in "idle in transaction" state

## Resolution Steps

### Immediate Actions (If Service is Down)

1. **Restart Application Servers**
   ```bash
   sudo systemctl restart application-service
   ```
   This will reset the connection pool.

2. **Kill Idle Database Connections**
   ```sql
   -- PostgreSQL
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'idle in transaction' 
   AND state_change < current_timestamp - INTERVAL '5 minutes';
   ```

### Long-term Fixes

1. **Review Code for Connection Leaks**
   - Ensure all database connections are closed in finally blocks
   - Check error handling paths
   - Verify connection.close() is called

2. **Adjust Connection Pool Settings**
   ```properties
   # application.properties
   spring.datasource.hikari.maximum-pool-size=50
   spring.datasource.hikari.connection-timeout=60000
   spring.datasource.hikari.idle-timeout=300000
   spring.datasource.hikari.max-lifetime=600000
   ```

3. **Enable Connection Pool Monitoring**
   - Set up alerts for pool exhaustion
   - Monitor connection acquisition time
   - Track connection leak detection

4. **Implement Connection Leak Detection**
   ```properties
   spring.datasource.hikari.leak-detection-threshold=60000
   ```

## Verification

1. Monitor connection pool metrics for 2 hours
2. Verify API response times return to normal (<500ms)
3. Check error logs for any remaining timeout errors
4. Confirm connection count stays within limits

## Rollback Plan

If changes don't resolve the issue:
1. Revert configuration changes
2. Restart services
3. Escalate to database team

## Post-Incident

- Document root cause
- Update monitoring thresholds
- Review and update this runbook
- Schedule code review if leak was found
