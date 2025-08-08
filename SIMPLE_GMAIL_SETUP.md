# Simple Gmail Setup (Recommended)

For individual users, the **App Password method** is much simpler than OAuth.

## Quick Setup (5 minutes)

### 1. Enable App Passwords in Gmail
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click "Security" → "2-Step Verification" (enable if not already)
3. Click "App passwords" 
4. Select "Mail" and "Other (Custom name)"
5. Enter name: "AI Agent"
6. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`)

### 2. Set Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env file
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # Remove spaces
```

### 3. Done!
No OAuth setup, no credentials.json, no browser popups.

## How Other Apps Do It

**Thunderbird, Outlook, Apple Mail:** Use app passwords or OAuth
**Superhuman, Notion:** OAuth with their own Google Cloud project  
**Zapier, IFTTT:** Users authenticate through their web interface

## Your App Options:

### Option A: App Passwords (Current - Simplest)
- ✅ User just needs email + app password
- ✅ Works immediately 
- ✅ No Google Cloud setup needed
- ❌ Requires 2FA enabled

### Option B: Your Own OAuth App  
- Create single Google Cloud project
- Users visit `yourapp.com/auth/gmail`
- They authorize once through your interface  
- You store their tokens
- ✅ Professional UX like other apps
- ❌ Need web server + database

### Option C: Let Users Bring OAuth
- Provide instructions for users to create their own credentials.json
- Some tech-savvy users prefer this
- ✅ Maximum security/control
- ❌ Complex for non-technical users

## Recommendation

Start with **App Passwords** (Option A) - it's what most email apps use and requires zero setup from you. Users just need their Gmail email + app password.

If you want to scale to thousands of users later, build Option B (centralized OAuth).