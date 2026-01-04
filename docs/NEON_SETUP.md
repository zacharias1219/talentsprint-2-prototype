# Neon Database Setup Guide

## Quick Setup (Recommended)

### Option 1: Quick Script (Fastest)

1. **Run the quick setup script with your Neon connection string:**

```bash
python scripts/quick_neon_setup.py "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

Replace the connection string with your actual Neon connection string from your Neon dashboard.

### Option 2: Interactive Setup

1. **Run the interactive setup script:**

```bash
python scripts/setup_neon_db.py
```

2. **Follow the prompts** to enter your Neon connection string.

### Option 3: Manual Setup

1. **Create a `.env` file** in the project root:

```bash
# In project root directory
touch .env
```

2. **Add your configuration:**

```env
AUTH_STORAGE_TYPE=database
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

3. **Replace the connection string** with your actual Neon connection string.

## Getting Your Neon Connection String

1. Log in to your [Neon Dashboard](https://console.neon.tech)
2. Select your project
3. Go to "Connection Details" or "Connection String"
4. Copy the connection string (it should look like):
   ```
   postgresql://username:password@ep-xxx-xxx.region.neon.tech/dbname?sslmode=require
   ```

## Verify Setup

After setup, test the connection:

```bash
python -c "from src.utils.database import init_connection_pool; init_connection_pool(); print('✅ Connection successful!')"
```

## Run the App

Once configured, run your Streamlit app:

```bash
streamlit run ui/streamlit_app.py
```

The authentication system will automatically:
- ✅ Use Neon database for user storage
- ✅ Create the users table if it doesn't exist
- ✅ Show "Production Mode: Database Storage" in the login page

## Troubleshooting

### Connection Errors

1. **Check your connection string format:**
   - Must start with `postgresql://`
   - Should include `?sslmode=require` for SSL

2. **Verify Neon database is running:**
   - Check your Neon dashboard
   - Ensure the database is active

3. **Check network connectivity:**
   - Ensure your IP is not blocked
   - Neon allows connections from anywhere by default

### Import Errors

If you get `psycopg2` import errors:

```bash
pip install psycopg2-binary
```

### Table Creation Errors

If the users table already exists, that's fine! The script uses `CREATE TABLE IF NOT EXISTS`.

## Security Notes

- ✅ `.env` file is already in `.gitignore` - your credentials are safe
- ✅ Never commit your `.env` file to git
- ✅ Use environment variables in production deployments
- ✅ Neon uses SSL by default for secure connections

## Next Steps

After setup:
1. ✅ Your app will use Neon for user authentication
2. ✅ All user accounts will be stored in Neon
3. ✅ You can scale to multiple app instances (they all use the same database)
4. ✅ Your data is backed up by Neon automatically

Enjoy your production-ready authentication system! 🚀

