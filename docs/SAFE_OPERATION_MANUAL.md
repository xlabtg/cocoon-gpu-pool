# Safe Operation Manual - Cocoon GPU Pool

## Document Information

**Version**: 1.0
**Last Updated**: [Date]
**Maintainer**: Cocoon GPU Pool Security Team
**Review Cycle**: Quarterly

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Security Architecture](#security-architecture)
4. [Operational Procedures](#operational-procedures)
5. [Access Control](#access-control)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Backup and Recovery](#backup-and-recovery)
8. [Incident Response](#incident-response)
9. [Maintenance and Updates](#maintenance-and-updates)
10. [Compliance and Auditing](#compliance-and-auditing)

---

## Introduction

### Purpose

This manual provides comprehensive guidance for the safe and secure operation of the Cocoon GPU Pool system. It covers all aspects of system operation, from deployment to ongoing maintenance, with a focus on security best practices.

### Scope

This manual applies to:
- Pool operators
- System administrators
- Security personnel
- DevOps engineers
- Support staff

### Document Conventions

- **MUST**: Required procedures that are mandatory
- **SHOULD**: Recommended procedures that are strongly advised
- **MAY**: Optional procedures

---

## System Overview

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                    Users / Clients                       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend Dashboard / API                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                Pool Gateway Server                       │
│  • Task Distribution                                     │
│  • Worker Management                                     │
│  • Payment Processing                                    │
└─────────────┬───────────────────────┬───────────────────┘
              │                       │
              ▼                       ▼
   ┌──────────────────┐    ┌─────────────────────┐
   │ TON Blockchain   │    │  Worker Nodes       │
   │ • Smart Contracts│    │  • GPU Processing   │
   │ • Payments       │    │  • TEE/TDX          │
   └──────────────────┘    └─────────────────────┘
```

### Key Technologies

- **Blockchain**: TON (The Open Network)
- **Backend**: [Language/Framework]
- **Frontend**: [Framework]
- **TEE**: Intel TDX (Trust Domain Extensions)
- **Database**: [Database System]
- **Monitoring**: Prometheus, Grafana

---

## Security Architecture

### Defense in Depth

1. **Network Layer**: Firewalls, DDoS protection, VPN
2. **Application Layer**: Input validation, authentication, authorization
3. **Data Layer**: Encryption at rest and in transit
4. **Infrastructure Layer**: Hardened systems, security updates
5. **Physical Layer**: Secure data centers (if applicable)

### Trust Boundaries

```
External Users → Frontend → API Gateway → Backend Services → Database
                    ↓
              TON Blockchain
                    ↓
              Worker Nodes (TEE)
```

### Security Zones

- **Public Zone**: Frontend, public APIs
- **Protected Zone**: Pool Gateway, API servers
- **Restricted Zone**: Database, admin interfaces
- **Highly Restricted Zone**: Private keys, secrets, TEE enclaves

---

## Operational Procedures

### 1. System Startup

#### Pre-Startup Checklist
- [ ] Verify all security updates applied
- [ ] Check system logs for anomalies
- [ ] Validate backup integrity
- [ ] Verify monitoring systems operational
- [ ] Check firewall rules
- [ ] Validate SSL/TLS certificates

#### Startup Sequence
```bash
# 1. Start database
sudo systemctl start postgresql

# 2. Verify database connectivity
psql -U cocoon_user -d cocoon_db -c "SELECT 1"

# 3. Start backend services
sudo systemctl start cocoon-gateway

# 4. Start worker nodes (if applicable)
sudo systemctl start cocoon-worker@{1..N}

# 5. Start frontend
sudo systemctl start cocoon-frontend

# 6. Verify all services
sudo systemctl status cocoon-*
```

#### Post-Startup Verification
- [ ] All services running
- [ ] Health checks passing
- [ ] Monitoring receiving metrics
- [ ] No error logs
- [ ] API endpoints responding

### 2. Worker Node Management

#### Adding a New Worker

1. **Registration**
   ```bash
   # Generate worker credentials
   cocoon-admin worker create --id worker_new_001

   # Obtain attestation
   cocoon-admin worker attest --id worker_new_001
   ```

2. **Validation**
   - Verify TEE/TDX attestation
   - Check GPU capabilities
   - Validate network connectivity
   - Test task execution

3. **Activation**
   ```bash
   cocoon-admin worker activate --id worker_new_001
   ```

#### Removing a Worker

1. **Graceful Shutdown**
   ```bash
   # Drain tasks
   cocoon-admin worker drain --id worker_old_001

   # Wait for completion (monitor)
   cocoon-admin worker status --id worker_old_001

   # Deactivate
   cocoon-admin worker deactivate --id worker_old_001
   ```

2. **Cleanup**
   - Remove worker credentials
   - Update monitoring
   - Archive worker logs

### 3. Payment Processing

#### Payment Verification
- **MUST** verify transaction on blockchain before confirming
- **MUST** check for sufficient funds before processing
- **MUST** log all payment attempts
- **SHOULD** implement idempotency for payment operations

#### Payment Reconciliation
```bash
# Daily reconciliation
cocoon-admin payment reconcile --date $(date +%Y-%m-%d)

# Check for discrepancies
cocoon-admin payment audit --date $(date +%Y-%m-%d)
```

### 4. Database Maintenance

#### Daily Operations
```bash
# Backup
pg_dump cocoon_db > backup_$(date +%Y%m%d).sql

# Vacuum
psql -U cocoon_user -d cocoon_db -c "VACUUM ANALYZE"
```

#### Weekly Operations
- Review slow queries
- Check index usage
- Monitor database size
- Review replication lag (if applicable)

### 5. Security Operations

#### Daily Security Tasks
- [ ] Review security logs
- [ ] Check failed authentication attempts
- [ ] Verify SSL certificate validity
- [ ] Review firewall logs
- [ ] Check for system updates

#### Weekly Security Tasks
- [ ] Review access logs
- [ ] Audit user permissions
- [ ] Check for vulnerabilities
- [ ] Review security alerts
- [ ] Update threat intelligence

#### Monthly Security Tasks
- [ ] Conduct security audit
- [ ] Review and update firewall rules
- [ ] Rotate credentials
- [ ] Test disaster recovery
- [ ] Security training review

---

## Access Control

### Role-Based Access Control (RBAC)

| Role | Permissions | Access Level |
|------|-------------|--------------|
| **Pool Admin** | Full system access | All systems |
| **Operator** | Operational tasks, monitoring | Backend, monitoring |
| **Security** | Security logs, audits | Logs, security systems |
| **Developer** | Code deployment, debugging | Development environment |
| **Support** | Read-only access, user support | Frontend, logs (limited) |
| **Auditor** | Read-only access, reports | All logs, reports |

### Access Procedures

#### Granting Access
```bash
# Create user
cocoon-admin user create --username john_doe --role operator

# Assign permissions
cocoon-admin user grant --username john_doe --permission monitoring

# Generate credentials
cocoon-admin user credentials --username john_doe
```

#### Revoking Access
```bash
# Disable user
cocoon-admin user disable --username john_doe

# Remove all sessions
cocoon-admin user logout-all --username john_doe

# Audit user activity
cocoon-admin user audit --username john_doe
```

### Multi-Factor Authentication (MFA)

**MUST** be enabled for:
- Pool administrators
- Security personnel
- Anyone with production access

**SHOULD** be enabled for:
- All operators
- Developers with deployment rights

### Access Logging

All access **MUST** be logged with:
- Username
- Timestamp
- Action performed
- Source IP
- Success/failure status

---

## Monitoring and Alerting

### Key Metrics

#### System Health
- CPU usage (alert > 80%)
- Memory usage (alert > 85%)
- Disk usage (alert > 90%)
- Network throughput
- Service availability (alert on downtime)

#### Application Metrics
- Request rate
- Response time (P50, P95, P99)
- Error rate (alert > 1%)
- Task queue depth
- Worker node count

#### Security Metrics
- Failed login attempts (alert > 5 in 5 min)
- Authentication errors
- Authorization failures
- Suspicious API calls
- Firewall blocks

#### Business Metrics
- Active workers
- Tasks processed per hour
- Payments processed
- Revenue
- User count

### Alert Configuration

#### Critical Alerts (Immediate Response)
- Service down
- Database unavailable
- Payment system failure
- Security breach detected
- Data corruption

#### High Priority Alerts (Response within 30 min)
- High error rate (> 5%)
- Performance degradation (P99 > 5s)
- Worker node failure
- Disk space critical (> 95%)

#### Medium Priority Alerts (Response within 2 hours)
- Moderate error rate (> 1%)
- Resource utilization high (> 80%)
- Slow queries detected

### Monitoring Dashboards

**MUST** have dashboards for:
- System overview
- Performance metrics
- Security events
- Business metrics
- Individual component health

---

## Backup and Recovery

### Backup Strategy

#### Database Backups
- **Full Backup**: Daily at 02:00 UTC
- **Incremental Backup**: Every 6 hours
- **Transaction Logs**: Continuous
- **Retention**: 30 days

#### Configuration Backups
- **System Configuration**: Daily
- **Application Configuration**: On every change
- **Secrets**: Encrypted, weekly
- **Retention**: 90 days

#### Backup Verification
```bash
# Test restore (weekly)
./scripts/test_restore.sh --date $(date +%Y-%m-%d)

# Verify backup integrity
./scripts/verify_backup.sh --backup backup_$(date +%Y%m%d).sql
```

### Disaster Recovery

#### Recovery Time Objectives (RTO)
- **Critical Services**: 1 hour
- **Standard Services**: 4 hours
- **Non-critical Services**: 24 hours

#### Recovery Point Objectives (RPO)
- **Payment Data**: 5 minutes
- **User Data**: 1 hour
- **Configuration**: 24 hours

#### Recovery Procedures

**Database Recovery**:
```bash
# Stop application services
sudo systemctl stop cocoon-*

# Restore database
psql -U cocoon_user -d cocoon_db < backup_latest.sql

# Verify integrity
psql -U cocoon_user -d cocoon_db -c "SELECT COUNT(*) FROM workers"

# Restart services
sudo systemctl start cocoon-*
```

---

## Incident Response

See detailed [Incident Response Plan](./INCIDENT_RESPONSE_PLAN.md)

### Quick Reference

1. **Detect**: Monitoring alerts, user reports
2. **Contain**: Isolate affected systems
3. **Investigate**: Determine root cause
4. **Remediate**: Fix the issue
5. **Recover**: Restore normal operations
6. **Review**: Post-incident analysis

### Emergency Contacts

- **Security Team**: security@cocoonpool.example
- **On-Call Engineer**: [Phone]
- **Management**: [Contact]
- **External Support**: [Contact]

---

## Maintenance and Updates

### Update Procedures

#### Security Updates (Critical)
1. Review security advisory
2. Test in staging environment
3. Schedule maintenance window (if required)
4. Apply update to production
5. Verify system functionality
6. Monitor for 24 hours

#### Regular Updates (Non-Critical)
1. Plan update during maintenance window
2. Notify users
3. Test in staging
4. Apply to production
5. Verify and monitor

### Maintenance Windows

- **Regular Maintenance**: Every Tuesday, 02:00-04:00 UTC
- **Emergency Maintenance**: As needed, with notification

### Change Management

All changes **MUST**:
- Be documented
- Have a rollback plan
- Be tested in staging
- Have approval from change advisory board
- Be communicated to stakeholders

---

## Compliance and Auditing

### Compliance Requirements

- **Data Protection**: GDPR (if applicable)
- **Financial**: SOC 2 Type II
- **Security**: ISO 27001
- **Smart Contracts**: TON best practices

### Audit Logging

**MUST** log:
- User authentication and authorization
- Data access and modifications
- System configuration changes
- Payment transactions
- Security events

**Log Retention**: 1 year minimum

### Regular Audits

- **Security Audit**: Quarterly
- **Compliance Audit**: Annually
- **Code Audit**: Every major release
- **Infrastructure Audit**: Semi-annually

---

## Appendix A: Command Reference

### Common Operations

```bash
# Check system status
cocoon-admin status

# View logs
cocoon-admin logs --service gateway --tail 100

# List workers
cocoon-admin worker list

# Payment status
cocoon-admin payment status --date today

# System health
cocoon-admin health
```

---

## Appendix B: Troubleshooting

### Common Issues

**Service Won't Start**
1. Check logs: `journalctl -u cocoon-gateway -n 100`
2. Verify configuration: `cocoon-admin config verify`
3. Check dependencies: `cocoon-admin check-deps`

**High Error Rate**
1. Check error logs
2. Verify database connectivity
3. Check resource utilization
4. Review recent changes

**Payment Failures**
1. Verify TON blockchain connectivity
2. Check wallet balance
3. Review transaction logs
4. Check for blockchain congestion

---

## Appendix C: Security Hardening Checklist

- [ ] Operating system fully patched
- [ ] Unnecessary services disabled
- [ ] Firewall configured and enabled
- [ ] SSH key-based authentication only
- [ ] SELinux/AppArmor enabled
- [ ] Regular security updates scheduled
- [ ] Intrusion detection system deployed
- [ ] Log monitoring configured
- [ ] Backups tested and verified
- [ ] Incident response plan tested

---

## Document Approval

**Prepared By**: Security Team
**Reviewed By**: Operations Team
**Approved By**: Management

**Date**: _______________
**Next Review**: _______________

---

**Confidentiality**: This document contains operational procedures and should be protected accordingly.
