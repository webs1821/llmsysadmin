# This file is part of LLMSysAdmin.
# 
# LLMSysAdmin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LLMSysAdmin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with LLMSysAdmin.  If not, see <https://www.gnu.org/licenses/>.
# 
# Copyright (C) 2024 Konrad k13.pl

import llmgate as lg
import subprocess
import json
import smtplib
import locale
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime,  timedelta


lg.system_instruction = "You are a Debian Linux system administator assistant. \
    Your task is to look at the output of dmesg command and create an email for administrator if any important logs occured. \
    The dmesg is from last 24 hours. If there are no important logs output just 'OK'. \
    If you find something important create an e-mail in Polish and format it using HTML. This HTML output will be send as an email. \
    Do not use Markdown at any case!"


def get_system_uptime() -> float:
    """
    Get the system uptime in seconds.
    
    :return: System uptime in seconds.
    """
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds


def format_date() -> str:
    """
    Format the current date and time in a specific format.
    
    :return: Formatted date and time string.
    """
    locale.setlocale(locale.LC_TIME, '')
    now = datetime.now()
    day_name = now.strftime("%a")
    day = now.day
    month_name = now.strftime("%b")
    time = now.strftime("%H:%M:%S")
    year = now.year

    formatted_date = f"[{day_name} {day} {month_name} {time} {year}]"
    return formatted_date


def get_dmesg_json(since_time: str) -> dict | None:
    """
    Get the dmesg log entries since the specified time and return them as a JSON object.

    :param since_time: The time since when to get the dmesg log entries (e.g., "24 hour ago").
    :return: A JSON object containing the dmesg log entries, or None if an error occurs.
    """
    try:
        result = subprocess.run(
            ['sudo', 'dmesg', '--since', since_time, '-J'],
            capture_output=True,
            text=True,
            check=True
        )
        dmesg_json = json.loads(result.stdout)
        for entry in dmesg_json.get('dmesg', []):
            if 'pri' in entry:
                del entry['pri']
        return dmesg_json
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON output: {e}")
        return None
    
def get_dmesg(since_time: str) -> str | None:
    """
    Get the dmesg log entries since the specified time and return them as a string object.

    :param since_time: The time since when to get the dmesg log entries (e.g., "24 hour ago").
    :return: A string object containing the dmesg log entries, or None if an error occurs.
    """
    try:
        result = subprocess.run(
            ['sudo', 'dmesg', '--since', since_time, '-T'],
            capture_output=True,
            text=True,
            check=True
        )        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(format_date(), f"Command failed with error: {e}")
        print(format_date(), f"stderr: {e.stderr}")
        print(format_date(), f"stdout: {e.stdout}")
        return None

def send_html_email(html_content: str) -> None:
    """
    Send an email with HTML content.

    :param html_content: HTML content of the email.
    """
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d-%m-%Y')
    
    ###################################
    #Configure below for your needs
    from_address = "...@gmail.com"
    to_address = "...@..."
    subject = "Log summary for host ... " + formatted_date
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "...@gmail.com"
    smtp_password = "..."
    ###################################

    msg = MIMEMultipart('alternative')
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    part = MIMEText(html_content, 'html')

    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_address, to_address, msg.as_string())
        print(format_date(), "Email sent successfully.")
    except Exception as e:
        print(format_date(), f"Failed to send email: {e}")

def remove_lines_with_prefix(text: str, prefix: str) -> str:
    """
    Remove lines from the text that start with the given prefix.

    :param text: The input text from which lines should be removed.
    :param prefix: The prefix that identifies lines to be removed.
    :return: The text with specified lines removed.
    """
    lines = text.split('\n')
    filtered_lines = [line for line in lines if not line.startswith(prefix)]
    return '\n'.join(filtered_lines)

def dmesg_since() -> str:
    """
    Get the dmesg since value excluding the first 1 minute after system startup.

    :return: The dmesg since value as a string.
    """
    uptime_seconds = get_system_uptime()

    if uptime_seconds < 24 * 3600:
        exclusion_time_seconds = uptime_seconds - 60
        exclusion_time = timedelta(seconds=exclusion_time_seconds)
        
        current_time = datetime.now()
        filter_time = current_time - exclusion_time
        filter_time_str = filter_time.strftime('%Y-%m-%d %H:%M:%S')
        return filter_time_str
    else:
        return "24 hour ago" 

        
if __name__ == "__main__":
    dmesg_logs = get_dmesg(dmesg_since())
    extra_instructions = "You can ignore lines related to audit and nextcloud. "

    #Delete one or both LLMs will be used:
    if dmesg_logs:
        email_content = lg.question(extra_instructions + dmesg_logs, "openai")
        email_content = remove_lines_with_prefix(email_content, "```")
        print(format_date(), email_content)
        if email_content.strip() != "OK":
            send_html_email(email_content)

    if dmesg_logs:
        email_content = lg.question(extra_instructions + dmesg_logs, "google")
        email_content = remove_lines_with_prefix(email_content, "```")
        print(format_date(), email_content)
        if email_content.strip() != "OK":
            send_html_email(email_content)