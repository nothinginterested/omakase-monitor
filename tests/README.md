# Test Suite for Omakase Monitor

This directory contains test scripts to verify the functionality of the omakase-monitor application.

## Prerequisites

Before running tests, ensure you have:

1. **Created configuration files**:
   ```bash
   cp config.yaml.example config.yaml
   cp .env.example .env
   ```

2. **Configured your settings**:
   - Edit `config.yaml` with your omakase.in credentials and target restaurants
   - Edit `.env` with your Gmail App Password

3. **Installed dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Test Scripts

### 1. Parser Test (No credentials needed)

Tests the API response parser with various formats.

```bash
python tests/test_parser.py
```

**What it tests**:
- List format responses
- Grouped by date responses
- Nested structures
- Date/time normalization
- Alternative field names
- Empty responses
- Missing required fields

**Expected output**: All 7 tests should pass ✓

---

### 2. Login Test (Requires omakase.in credentials)

Tests login functionality and cookie persistence.

```bash
python tests/test_login.py
```

**What it tests**:
- Configuration loading and validation
- Connection to omakase.in
- CSRF token extraction
- Login form submission
- Cookie saving
- Cookie persistence across sessions

**Expected output**:
```
[1/5] Loading configuration... ✓
[2/5] Validating configuration... ✓
[3/5] Checking for existing cookies...
[4/5] Attempting login to omakase.in... ✓
[5/5] Testing cookie persistence... ✓
Login Test Completed Successfully! ✓
```

**Troubleshooting**:
- If login fails, verify your email/password in `config.yaml`
- Check if omakase.in is accessible from your network
- Look for CAPTCHA challenges in the logs

---

### 3. Email Test (Requires Gmail App Password)

Tests email notification functionality.

```bash
python tests/test_email.py
```

**What it tests**:
- Gmail SMTP connection
- Email template rendering with HTML
- Japanese character handling
- Price formatting
- Multiple time slots in email

**Expected output**:
- Sends a test email to the configured receiver
- Email should contain 3 test time slots
- HTML table formatting
- Proper price formatting (¥15,000)

**Troubleshooting**:
- Verify `GMAIL_APP_PASSWORD` in `.env`
- Ensure sender email has 2-Step Verification enabled
- Check spam folder if email not received

---

### 4. Complete Monitoring Test (Requires all credentials)

Tests the entire monitoring workflow end-to-end.

```bash
python tests/test_monitor.py
```

**What it tests**:
- Complete configuration validation
- Login to omakase.in
- Fetching real time slots from API
- API response parsing
- Change detection logic
- Email notification (if new slots found)
- State caching

**Expected output**:
```
[1/6] Loading configuration... ✓
[2/6] Checking restaurant configuration... ✓
[3/6] Initializing monitoring service... ✓
[4/6] Test execution confirmation
[5/6] Running monitoring cycle... ✓
[6/6] Results summary... ✓
```

**Notes**:
- First run will treat all slots as "new"
- Run again to test change detection (only truly new slots will notify)
- Check email inbox if notifications were sent
- Results depend on actual availability from omakase.in

**Troubleshooting**:
- If API calls fail, check restaurant slugs in `config.yaml`
- Enable DEBUG logging to see API responses
- Verify network connectivity to omakase.in

---

## Running All Tests

To run all tests in sequence:

```bash
# 1. Parser test (no credentials needed)
python tests/test_parser.py

# 2. Login test
python tests/test_login.py

# 3. Email test (optional - sends real email)
python tests/test_email.py

# 4. Complete monitoring test
python tests/test_monitor.py
```

---

## Enabling Debug Logging

To see detailed logs during testing, set the logging level to DEBUG in the test script or run:

```bash
# In Python code
import logging
logging.basicConfig(level=logging.DEBUG)

# Or modify the test script temporarily
```

Debug logs will show:
- API request/response details
- Cookie operations
- CSRF token extraction
- Email SMTP communication
- Parser decisions

---

## Common Issues

### Login Test Fails

**Problem**: "Login failed: Still on login page"

**Solutions**:
1. Verify email/password in `config.yaml`
2. Check if account is locked or requires CAPTCHA
3. Try logging in manually via browser first
4. Check for Cloudflare or rate limiting

### Email Test Fails

**Problem**: "SMTP authentication failed"

**Solutions**:
1. Verify Gmail App Password (not regular password)
2. Enable 2-Step Verification in Google Account
3. Generate new App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Check for spaces in the password (should be removed)

### Parser Test Fails

**Problem**: AssertionError on slot count

**Solutions**:
- This indicates a bug in the parser
- Check the test output to see which case failed
- Report issue with test output

### Monitor Test Returns No Slots

**Problem**: "No time slots were found"

**Possible reasons**:
1. Restaurant is fully booked (normal)
2. No upcoming availability (normal)
3. Incorrect restaurant slug (check `config.yaml`)
4. API structure has changed (enable DEBUG logging)

---

## Next Steps After Testing

Once all tests pass:

1. **Set up scheduling** - Add APScheduler for automated monitoring
2. **Deploy** - Configure for production environment
3. **Monitor logs** - Watch for any issues during operation
4. **Adjust configuration** - Fine-tune polling intervals

---

## Test Results Checklist

- [ ] Parser test passes all 7 cases
- [ ] Login test succeeds and creates cookies.json
- [ ] Second login reuses cookies (persistence works)
- [ ] Email test sends correctly formatted notification
- [ ] Monitor test completes full cycle
- [ ] Monitor test detects changes on second run
- [ ] No errors in logs

Once all items are checked, the application is ready for production use!
