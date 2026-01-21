# Omakase Restaurant Reservation Monitor

Monitor [omakase.in](https://omakase.in) restaurant reservations and receive email notifications when new time slots become available.

## Features

- 🔍 Monitor multiple restaurants simultaneously
- 📧 Email notifications via Gmail when new reservations appear
- ⏱️ Configurable polling intervals with random delays (anti-bot protection)
- 🔒 Secure credential management via environment variables
- 📝 Detailed logging for monitoring and debugging

## Requirements

- Python 3.10+
- Gmail account with App Password enabled
- omakase.in user account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nothinginterested/omakase-monitor.git
cd omakase-monitor
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up configuration files:
```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

4. Edit `.env` and add your Gmail App Password:
```bash
GMAIL_APP_PASSWORD=your_app_password_here
```

5. Edit `config.yaml` to configure:
   - Your omakase.in login credentials
   - Target restaurants to monitor
   - Notification email addresses
   - Polling intervals

## Gmail App Password Setup

1. Enable 2-Step Verification on your Google Account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Select "Mail" and your device
4. Copy the generated 16-character password
5. Add it to your `.env` file

**Important**: Never use your actual Gmail password. Always use an App Password.

## Configuration

### config.yaml Structure

```yaml
monitor:
  interval_min: 5           # Minimum polling interval (minutes)
  interval_max: 10          # Maximum polling interval (minutes)
  random_delay_max: 120     # Max random delay (seconds)

omakase:
  email: "your-email@example.com"
  password: "your-password"

restaurants:
  - name: "Restaurant Name"
    slug: "restaurant-slug"  # From URL: omakase.in/ja/r/{slug}
    url: "https://omakase.in/ja/r/slug"
    enabled: true

notification:
  gmail:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "sender@gmail.com"
    receiver_email: "receiver@gmail.com"
```

## Usage

Start the monitor:
```bash
python main.py
```

The script will:
1. Login to omakase.in
2. Poll configured restaurants at random intervals (5-10 minutes)
3. Detect new available time slots
4. Send email notifications when changes are found

Logs are written to `omakase_monitor.log` and console.

## Project Structure

```
omakase-monitor/
├── main.py                 # Entry point
├── config.yaml             # Configuration (create from example)
├── .env                    # Environment variables (create from example)
├── src/
│   ├── monitor.py          # Core monitoring logic
│   ├── omakase_client.py   # API client for omakase.in
│   ├── parser.py           # Response parser
│   ├── notifier.py         # Email notification module
│   ├── models.py           # Data models
│   └── utils.py            # Utility functions
└── requirements.txt        # Python dependencies
```

## Anti-Bot Measures

To avoid triggering rate limiting or CAPTCHA:

- Random polling intervals (5-10 minutes)
- Random delays between requests (1-3 seconds)
- Realistic User-Agent headers
- Cookie persistence to avoid frequent logins
- Exponential backoff on errors

## Troubleshooting

**Login fails**: Verify your omakase.in credentials in `config.yaml`

**Email not sending**:
- Ensure Gmail App Password is correct in `.env`
- Check sender email has 2-Step Verification enabled
- Verify SMTP settings in `config.yaml`

**CAPTCHA detected**: The script will pause and log an error. Wait before restarting.

## Security Notes

- Never commit `.env` or `config.yaml` to version control
- Use Gmail App Passwords, not real passwords
- Keep your credentials secure

## License

MIT License

## Disclaimer

This tool is for personal use only. Please respect omakase.in's terms of service and avoid excessive requests that may impact their service.
