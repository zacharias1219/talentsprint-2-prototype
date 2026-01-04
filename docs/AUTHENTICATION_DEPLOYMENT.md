# Authentication & User Storage Deployment Guide

## Overview

The authentication system supports two storage backends:
1. **JSON File Storage** (Development) - For local development and testing
2. **PostgreSQL Database** (Production) - For production deployments

## Storage Configuration

### Environment Variable

Set the `AUTH_STORAGE_TYPE` environment variable to choose the storage backend:

```bash
# For JSON file storage (development)
export AUTH_STORAGE_TYPE=json

# For PostgreSQL database (production)
export AUTH_STORAGE_TYPE=database
```

### Default Behavior

If `AUTH_STORAGE_TYPE` is not set, the system defaults to JSON file storage.

## Storage Options

### 1. JSON File Storage (Development)

**Location:** `data/users/users.json`

**Pros:**
- Easy to set up (no database required)
- Good for development and testing
- Simple backup (just copy the file)

**Cons:**
- Not suitable for production
- No concurrent access protection
- Limited scalability
- No built-in backup/recovery

**Use Case:** Local development, demos, single-user deployments

### 2. PostgreSQL Database (Production)

**Location:** Configured via `DATABASE_URL` in environment variables or `config/config.yaml`

**Pros:**
- Production-ready
- Supports concurrent users
- ACID compliance
- Built-in backup/recovery options
- Scalable
- Better security (connection pooling, prepared statements)

**Cons:**
- Requires database setup
- More complex configuration

**Use Case:** Production deployments, multi-user environments

## Production Deployment Options

### Option 1: Cloud Database Services

#### PostgreSQL on AWS RDS
```bash
# Set environment variables
export AUTH_STORAGE_TYPE=database
export DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/financial_advisor
```

#### PostgreSQL on Google Cloud SQL
```bash
export AUTH_STORAGE_TYPE=database
export DATABASE_URL=postgresql://username:password@/financial_advisor?host=/cloudsql/project:region:instance
```

#### PostgreSQL on Azure Database
```bash
export AUTH_STORAGE_TYPE=database
export DATABASE_URL=postgresql://username:password@your-azure-server.postgres.database.azure.com:5432/financial_advisor
```

#### Managed PostgreSQL Services
- **Supabase**: Free tier available, easy setup
- **Heroku Postgres**: Add-on for Heroku deployments
- **ElephantSQL**: Free tier available
- **Neon**: Serverless PostgreSQL

### Option 2: Self-Hosted PostgreSQL

#### Docker Compose (Included)
The project includes `docker-compose.yml` with PostgreSQL:

```bash
# Start PostgreSQL container
docker-compose up -d db

# Set environment variable
export AUTH_STORAGE_TYPE=database
export DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_advisor
```

#### Standalone PostgreSQL Server
1. Install PostgreSQL on your server
2. Create database:
   ```sql
   CREATE DATABASE financial_advisor;
   CREATE USER app_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE financial_advisor TO app_user;
   ```
3. Set environment variables:
   ```bash
   export AUTH_STORAGE_TYPE=database
   export DATABASE_URL=postgresql://app_user:secure_password@your-server:5432/financial_advisor
   ```

### Option 3: Serverless/Container Platforms

#### Streamlit Cloud
1. Add PostgreSQL add-on or use external database
2. Set `AUTH_STORAGE_TYPE=database` in secrets
3. Add `DATABASE_URL` to secrets

#### Heroku
1. Add Heroku Postgres add-on:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
2. Set environment variable:
   ```bash
   heroku config:set AUTH_STORAGE_TYPE=database
   ```
3. `DATABASE_URL` is automatically set by Heroku

#### Railway
1. Add PostgreSQL service
2. Set `AUTH_STORAGE_TYPE=database` in environment variables
3. Use provided `DATABASE_URL`

#### Render
1. Create PostgreSQL database service
2. Set environment variables in service settings
3. Use internal database URL for connection

## Database Schema

The users table is automatically created on first use:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    username_lower VARCHAR(30) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_username_lower ON users(username_lower);
```

## Migration from JSON to Database

To migrate existing users from JSON to database:

1. **Backup JSON file:**
   ```bash
   cp data/users/users.json data/users/users.json.backup
   ```

2. **Set database storage:**
   ```bash
   export AUTH_STORAGE_TYPE=database
   export DATABASE_URL=your_database_url
   ```

3. **Run migration script** (create if needed):
   ```python
   # scripts/migrate_users_to_db.py
   import json
   from pathlib import Path
   from ui.components.auth import save_user_db
   
   json_file = Path("data/users/users.json")
   if json_file.exists():
       with open(json_file) as f:
           users = json.load(f)
       for user_key, user_data in users.items():
           save_user_db(user_key, user_data)
   ```

## Security Considerations

### Password Storage
- Passwords are hashed using bcrypt with salt
- Never stored in plain text
- Hash cannot be reversed

### Account Security
- Account lockout after 5 failed login attempts
- Failed attempt tracking
- Last login timestamp

### Database Security
- Use SSL/TLS for database connections in production
- Use connection pooling
- Implement proper access controls
- Regular backups
- Use environment variables for credentials (never hardcode)

### Best Practices
1. **Use strong passwords** (enforced by validation)
2. **Enable SSL** for database connections
3. **Regular backups** of user data
4. **Monitor failed login attempts** for security threats
5. **Rotate database credentials** periodically
6. **Use read replicas** for scaling read operations

## Backup Strategy

### JSON Storage Backup
```bash
# Simple file backup
cp data/users/users.json data/users/users.json.backup
```

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U username -d financial_advisor > backup.sql

# Restore
psql -h localhost -U username -d financial_advisor < backup.sql
```

### Automated Backups
- Set up cron jobs for regular backups
- Use cloud storage for backup files
- Test restore procedures regularly

## Monitoring

### Key Metrics to Monitor
- Number of registered users
- Failed login attempts
- Account lockouts
- Database connection pool usage
- Authentication response times

### Logging
- All authentication attempts are logged
- Failed login attempts are tracked
- Account lockouts are recorded

## Troubleshooting

### Database Connection Issues
1. Verify `DATABASE_URL` is correct
2. Check database is running
3. Verify network connectivity
4. Check firewall rules
5. Verify credentials

### Migration Issues
1. Ensure database user has CREATE TABLE permissions
2. Check for existing table conflicts
3. Verify data types match

### Performance Issues
1. Monitor connection pool usage
2. Add database indexes if needed
3. Consider read replicas for scaling
4. Optimize queries

## Recommended Production Setup

1. **Use PostgreSQL database** (`AUTH_STORAGE_TYPE=database`)
2. **Managed database service** (AWS RDS, Google Cloud SQL, etc.)
3. **Enable SSL/TLS** for database connections
4. **Set up automated backups** (daily at minimum)
5. **Monitor authentication metrics**
6. **Use connection pooling** (already implemented)
7. **Implement rate limiting** (already implemented for API)
8. **Regular security audits**

