# LLMSysAdmin

LLMSysAdmin is a Python application designed to analyze system logs on a Debian Linux system using machine learning models from OpenAI and Google. The program collects `dmesg` logs from the past 24 hours and sends an email to the system administrator if any significant issues are detected. The email is created in Polish (you can change it in the prompt) and formatted using HTML.

## Table of Contents
- [Features](#features)
- [Example result](#example-result)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Installation](#installation)
- [Usage](#usage)
- [Code Overview](#code-overview)
- [License](#license)
- [Contact](#contact)


## Features
- Collects `dmesg` logs from the last 24 hours.
- Skips the first minute of logs if the system uptime is less than 24 hours to avoid boot messages.
- Analyzes logs using OpenAI and Google LLM APIs.
- Sends an HTML email to the system administrator if any significant issues are found.
- Generates clean and concise email content.

## Example result

```html
<!DOCTYPE html>
<html>
<head>
<title>Important dmesg Logs</title>
</head>
<body>
<h1>Important dmesg Logs</h1>
<p>The following events occurred in the last 24 hours:</p>
<ul>
<li>[Thu May 30 15:27:22 2024] loop7: detected capacity change from 0 to 631152</li>
</ul>
<p>Please check the above logs.</p>
</body>
</html>
```

## Requirements
- Python 3.11 (or maybe lower - not tested)
- Linux Debian
- API keys for OpenAI and Google LLM
- Configured email credentials

## Configuration
Before using LLMSysAdmin, you need to configure the following:

1. **API Keys:**
   - OpenAI: Set your OpenAI API key in the `openai` function in `llmgate.py`.
   - Google: Set your Google API key in the `google` function in `llmgate.py`.

2. **Email Settings:** 
   In the `send_html_email` function in `llmsysadmin.py`, configure the following:
   ```python
   from_address = "your-email@gmail.com"
   to_address = "admin-email@example.com"
   subject = "Log summary for host ..."
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   smtp_user = "your-email@gmail.com"
   smtp_password = "your-email-password"
   ```

3. **Prompt Adjustments:** 
   In `llmsysadmin.py`, you may adjust the system instruction prompt and extra instructions to fit your specific needs.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/webs1821/llmsysadmin.git
   cd llmsysadmin
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up your `crontab` to run the script daily at 8 AM:
   ```sh
   sudo crontab -e
   ```

   Add the following line to schedule the script:
   ```sh
   0 8 * * * /bin/python3 /path/to/llmsysadmin/llmsysadmin.py >> /path/to/llmsysadmin/llmsysadmin.log 2>&1
   ```

## Usage
1. Run the script manually to ensure everything is working correctly:
   ```sh
   python3 llmsysadmin.py
   ```

2. Check the logs to confirm that emails are being sent properly:
   ```sh
   tail -f /path/to/llmsysadmin/llmsysadmin.log
   ```

## Code Overview

**llmsysadmin.py**

- **get_system_uptime()**: Returns system uptime in seconds.
- **format_date()**: Formats the current date and time.
- **get_dmesg_json()**: Retrieves `dmesg` logs in JSON format since a specified time.
- **get_dmesg()**: Retrieves `dmesg` logs as a string since a specified time.
- **send_html_email()**: Sends an email with the specified HTML content.
- **remove_lines_with_prefix()**: Removes lines starting with a specified prefix from the text.
- **dmesg_since()**: Calculates the `dmesg` since value, excluding the first minute of system startup if uptime is less than 24 hours.

**llmgate.py**

- **question()**: Generates a response based on the prompt using the specified engine (OpenAI or Google).
- **openai()**: Generates a response using OpenAI's API.
- **google()**: Generates a response using Google's Generative AI API.


## License
LLMSysAdmin is licensed under the GNU General Public License v3.0. See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for more details.

## Contact
For any inquiries, please contact Konrad at k13.pl

---

**Note:** Replace placeholders such as `your-email@gmail.com`, `admin-email@example.com`, and `/path/to/llmsysadmin` with your actual email addresses and file paths.