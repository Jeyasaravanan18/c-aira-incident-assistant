# RUNBOOK: Disk Space Management

## Overview
Procedures for managing disk space issues on application servers, including log cleanup, monitoring, and prevention.

## Symptoms
- "No space left on device" errors
- Failed deployments
- Application unable to write logs
- Slow system performance
- Service health check failures

## Prerequisites
- SSH access to affected servers
- Sudo privileges
- Backup access (for log archival)

## Diagnosis Steps

### Step 1: Check Disk Usage
```bash
# Overall disk usage
df -h

# Find largest directories
du -h / | sort -rh | head -20

# Check specific partitions
df -h /var
df -h /tmp
df -h /opt
```

### Step 2: Identify Space Consumers
```bash
# Find large files (>100MB)
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# Check log directory size
du -sh /var/log/*

# Check application logs
du -sh /var/log/application/*
```

### Step 3: Check Log Rotation
```bash
# Verify logrotate configuration
cat /etc/logrotate.d/application

# Check logrotate status
cat /var/lib/logrotate/status
```

## Resolution Steps

### Immediate Actions (Critical - Disk Full)

1. **Free Up Space Quickly**
   ```bash
   # Compress old logs
   find /var/log/application -name "*.log" -mtime +7 -exec gzip {} \;
   
   # Remove old compressed logs
   find /var/log/application -name "*.gz" -mtime +30 -delete
   
   # Clear temporary files
   rm -rf /tmp/*
   rm -rf /var/tmp/*
   ```

2. **Verify Space Freed**
   ```bash
   df -h
   ```

### Long-term Solutions

1. **Configure Log Rotation**
   ```bash
   # Create/update logrotate config
   sudo nano /etc/logrotate.d/application
   ```
   
   Add configuration:
   ```
   /var/log/application/*.log {
       daily
       rotate 14
       compress
       delaycompress
       missingok
       notifempty
       create 0644 appuser appuser
       sharedscripts
       postrotate
           systemctl reload application-service > /dev/null 2>&1 || true
       endscript
   }
   ```

2. **Adjust Application Log Level**
   ```bash
   # Edit application configuration
   sudo nano /etc/application/application.properties
   ```
   
   Change:
   ```properties
   # From DEBUG to INFO in production
   logging.level.root=INFO
   logging.level.com.company=INFO
   ```

3. **Set Up Automated Cleanup**
   ```bash
   # Create cleanup script
   sudo nano /usr/local/bin/cleanup-logs.sh
   ```
   
   Script content:
   ```bash
   #!/bin/bash
   # Compress logs older than 7 days
   find /var/log/application -name "*.log" -mtime +7 -exec gzip {} \;
   
   # Delete compressed logs older than 30 days
   find /var/log/application -name "*.gz" -mtime +30 -delete
   
   # Delete old temp files
   find /tmp -mtime +7 -delete
   ```
   
   Make executable and schedule:
   ```bash
   sudo chmod +x /usr/local/bin/cleanup-logs.sh
   
   # Add to crontab (run daily at 2 AM)
   echo "0 2 * * * /usr/local/bin/cleanup-logs.sh" | sudo crontab -
   ```

4. **Set Up Monitoring**
   ```bash
   # Install disk space monitoring
   # Add to monitoring system or create alert script
   
   # Example: Simple alert script
   cat > /usr/local/bin/disk-alert.sh << 'EOF'
   #!/bin/bash
   THRESHOLD=80
   USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
   
   if [ $USAGE -gt $THRESHOLD ]; then
       echo "Disk usage is ${USAGE}% - exceeds threshold of ${THRESHOLD}%"
       # Send alert (email, Slack, PagerDuty, etc.)
   fi
   EOF
   
   chmod +x /usr/local/bin/disk-alert.sh
   
   # Run every hour
   echo "0 * * * * /usr/local/bin/disk-alert.sh" | crontab -
   ```

## Specific Scenarios

### Scenario 1: Application Logs Filling Disk

**Resolution:**
1. Change log level from DEBUG to INFO
2. Configure log rotation
3. Set up automated cleanup
4. Consider centralized logging (ELK, Splunk)

### Scenario 2: Database Backups Consuming Space

**Resolution:**
1. Move backups to separate storage
2. Implement backup retention policy
3. Compress old backups
4. Use incremental backups

### Scenario 3: Docker Images/Containers

**Resolution:**
```bash
# Remove unused Docker resources
docker system prune -a

# Remove old images
docker image prune -a --filter "until=720h"

# Remove stopped containers
docker container prune
```

## Verification

1. Verify disk usage is below 80%
2. Confirm log rotation is working
3. Test application can write logs
4. Verify deployments succeed
5. Check monitoring alerts are configured

## Prevention

1. **Implement Monitoring**
   - Set alerts at 80% disk usage
   - Monitor log growth rate
   - Track disk usage trends

2. **Regular Maintenance**
   - Weekly review of disk usage
   - Monthly cleanup of old files
   - Quarterly capacity planning

3. **Best Practices**
   - Use appropriate log levels (INFO in prod)
   - Implement log rotation for all applications
   - Archive old logs to object storage
   - Set up centralized logging
   - Document disk space requirements

## Rollback Plan

If cleanup causes issues:
1. Restore logs from backup if needed
2. Revert configuration changes
3. Restart affected services

## Post-Incident

- Document what filled the disk
- Update monitoring thresholds
- Review log retention policies
- Update capacity planning
- Share learnings with team
