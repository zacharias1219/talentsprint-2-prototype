# Streamlit Cloud Setup Guide

## Secrets Configuration

In Streamlit Cloud, go to **Settings → Secrets** and add your environment variables as simple key-value pairs (NOT TOML format).

### Required Secrets

Add these secrets one by one:

```
AUTH_STORAGE_TYPE=database
DATABASE_URL=postgresql://neondb_owner:npg_Qo3WnyCUY6aZ@ep-tiny-hill-a181di5w-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Optional Secrets (if you use these features)

```
ALPHA_VANTAGE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=financial-advisor
```

## Important Notes

1. **No TOML syntax** - Don't use `[database]` or any section headers
2. **No quotes needed** - Just `KEY=value` format
3. **One per line** - Each secret on its own line
4. **Full connection string** - Make sure your DATABASE_URL is complete

## Example Correct Format

```
AUTH_STORAGE_TYPE=database
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
ALPHA_VANTAGE_API_KEY=your_key
```

## Your Current Issue

Your secrets had:
- `[database]` - Remove this (it's TOML syntax, not needed)
- `DATABASE_URL=my_postgres/-api"` - This looks incomplete/corrupted

**Fix it to:**
```
AUTH_STORAGE_TYPE=database
DATABASE_URL=postgresql://neondb_owner:npg_Qo3WnyCUY6aZ@ep-tiny-hill-a181di5w-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## After Setting Secrets

1. Save the secrets
2. The app will automatically restart
3. Check the logs to verify the connection works

