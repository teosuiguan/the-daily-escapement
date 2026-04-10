"""
daily_escapement.py (Singapore SGT Date Version)

Reads the digest JSON produced by Manus AI and injects it into
the Birch HTML template. The completed HTML is then sent via 
the Manus AI Gmail connector.
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta, timezone

INPUT_JSON    = "/home/ubuntu/generated_digest.json"
TEMPLATE_HTML = "/home/ubuntu/email_template.html"
OUTPUT_HTML   = "/home/ubuntu/daily_watch_summary.html"

def generate_html(data, template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Singapore Time (SGT) is UTC+8
    sgt_timezone = timezone(timedelta(hours=8))
    now = datetime.now(sgt_timezone)
    
    # Global placeholders
    date_str = data.get("date") or now.strftime("%B %d, %Y")
    
    # Placeholders for the template
    template = template.replace("{{date}}", date_str)
    template = template.replace("{{date_day}}", now.strftime("%A").upper())
    template = template.replace("{{date_year}}", now.strftime("%B %d, %Y").upper())
    template = template.replace("{{executive_summary}}", data.get("executive_summary", ""))

    # Main summaries (Top Stories)
    main_summaries = data.get("main_summaries", [])
    for i in range(1, 6): # Template may have up to 5 slots
        idx = i - 1
        if idx < len(main_summaries):
            story = main_summaries[idx]
            template = template.replace(f"{{{{title_{i}}}}}", story.get("title", ""))
            template = template.replace(f"{{{{source_{i}}}}}", story.get("source", ""))
            template = template.replace(f"{{{{date_{i}}}}}", story.get("date", ""))
            template = template.replace(f"{{{{url_{i}}}}}", story.get("url", ""))
            template = template.replace(f"{{{{summary_{i}}}}}", story.get("summary", ""))
        else:
            # Clear unused slots
            template = template.replace(f"{{{{title_{i}}}}}", "")
            template = template.replace(f"{{{{source_{i}}}}}", "")
            template = template.replace(f"{{{{date_{i}}}}}", "")
            template = template.replace(f"{{{{url_{i}}}}}", "")
            template = template.replace(f"{{{{summary_{i}}}}}", "")

    # Quick Hits
    quick_hits = data.get("quick_hits", [])
    for i in range(1, 6): # Template may have up to 5 slots
        idx = i - 1
        if idx < len(quick_hits):
            qh = quick_hits[idx]
            template = template.replace(f"{{{{qh_source_{i}}}}}", qh.get("source", ""))
            template = template.replace(f"{{{{qh_url_{i}}}}}", qh.get("url", ""))
            template = template.replace(f"{{{{qh_text_{i}}}}}", qh.get("text", ""))
        else:
            # Clear unused slots
            template = template.replace(f"{{{{qh_source_{i}}}}}", "")
            template = template.replace(f"{{{{qh_url_{i}}}}}", "")
            template = template.replace(f"{{{{qh_text_{i}}}}}", "")

    return template

def send_email(html_content, date_str):
    input_data = {
        "messages": [
            {
                "to": ["suiguan.teo@gmail.com"],
                "subject": f"The Daily Escapement — {date_str}",
                "content": html_content
            }
        ]
    }
    
    try:
        subprocess.run(
            ["manus-mcp-cli", "tool", "call", "gmail_send_messages", "--server", "gmail", "--input", json.dumps(input_data)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Success: Email sent via Gmail connector.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending email: {e}")
        sys.exit(1)

def main():
    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

    try:
        final_html = generate_html(data, TEMPLATE_HTML)
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"Success: Email HTML written to {OUTPUT_HTML}")
        
        # Send the email directly
        date_str = data.get("date") or datetime.now().strftime("%B %d, %Y")
        send_email(final_html, date_str)
        
    except Exception as e:
        print(f"Error generating or sending email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
