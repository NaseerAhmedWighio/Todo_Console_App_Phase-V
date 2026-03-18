# Database Setup Guide - Neon PostgreSQL

## Issue: Password Authentication Failed

Your database credentials need to be updated. Follow these steps:

## Step 1: Get Your Neon Database Connection String

### Option A: From Neon Console
1. Go to **https://console.neon.tech/** and sign in
2. Select your project (or create a new free project)
3. Click on **"Connection Details"** in the left sidebar
4. You'll see your connection string that looks like:
   ```
   postgresql://neondb_owner:password123@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
5. **Copy the entire connection string**

### Option B: Using Connection String Builder
1. In Neon Console, go to your project dashboard
2. Click **"Connection Details"**
3. Use the connection string builder to get the correct format
4. Make sure to select **"Pooler"** mode for better performance

## Step 2: Update .env File

1. Open `backend/.env` file
2. Find the line that starts with `DATABASE_URL=`
3. Replace the entire value with your copied connection string:
   ```bash
   DATABASE_URL=postgresql://your-username:your-password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```

## Step 3: Verify Connection

Run the test script:
```bash
cd backend
python test_db_connection.py
```

You should see:
```
[SUCCESS] Database connection established!
```

## Step 4: Run Database Migration

After confirming the connection works, run the migration:
```bash
cd backend
python migrate_simple.py
```

This will:
- Add `is_email_verified` column to users table
- Add `email_verified_at` column to users table
- Create `email_verifications` table
- Update reminders table with new columns

## Step 5: Start the Server

```bash
cd backend
python main.py
```

## Common Issues & Solutions

### Issue 1: "password authentication failed"
**Solution**: Double-check your password in the connection string. Make sure there are no extra spaces.

### Issue 2: "could not translate host name"
**Solution**: 
- Check your internet connection
- Verify the hostname is correct (should be like `ep-xxx-xxx.region.aws.neon.tech`)
- Try using the non-pooler connection string

### Issue 3: "SSL connection error"
**Solution**: Make sure `?sslmode=require` is at the end of your DATABASE_URL

### Issue 4: "database does not exist"
**Solution**: 
- Create a new database in your Neon project
- Or use the default `neondb` database that comes with every project

## Alternative: Use Connection String Directly

If you're having issues, you can also:

1. In Neon Console, click **"Copy connection string"** button
2. Paste it directly into your `.env` file
3. Make sure there are no line breaks or extra spaces

## Security Notes

- **Never commit your .env file** to Git (it's already in .gitignore)
- **Rotate your password** periodically in Neon Console
- **Use environment variables** in production instead of .env files

## Need Help?

1. Check Neon docs: https://neon.tech/docs/
2. Check your project's connection details in Neon Console
3. Verify your database is active (not paused)

---

After completing these steps, your registration and login should work properly with email verification!
