import os
import json
from datetime import datetime, timedelta, timezone
from openai import OpenAI

def main():
    client = OpenAI() # API key and base URL are pre-configured in the environment
    
    with open("/home/ubuntu/prompt.txt", "r") as f:
        prompt_content = f.read()
    
    with open("/home/ubuntu/raw_articles.txt", "r") as f:
        articles_content = f.read()
    
    # Singapore Time (SGT) is UTC+8
    sgt_timezone = timezone(timedelta(hours=8))
    today = datetime.now(sgt_timezone).strftime("%B %d, %Y")
    
    system_prompt = "You are a specialized assistant that generates a daily watch digest in JSON format based on specific rules."
    user_prompt = f"""
Apply the following rules to the articles provided below.
Current Date: {today}
Location: Singapore

RULES:
{prompt_content}

ARTICLES:
{articles_content}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    digest_json = response.choices[0].message.content
    
    # Save the output
    with open("/home/ubuntu/generated_digest.json", "w") as f:
        f.write(digest_json)
    
    print(f"Successfully generated digest JSON for {today} (SGT).")

if __name__ == "__main__":
    main()
