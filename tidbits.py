import subprocess
import os
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import markdown
import json

class SecretKnowledgeTidbits:
    def __init__(self, readme_url: str):
        self.readme_url = readme_url
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        self.recipient_email = os.environ.get('RECIPIENT_EMAIL')
        self.sender_email = os.environ.get('SENDER_EMAIL')
    
    def get_daily_tidbits(self) -> str:
        """Use LLM to extract and explain three random tidbits."""
        random_numbers = [random.randint(1, 100) for _ in range(3)]
        
        prompt = f"""Go to this URL and read the content: {self.readme_url}
        
        You are a helpful assistant that will extract and explain interesting tools/commands/falsehoods from the provided URL (pulling content from some of the linked pages if necessary).
        
        To ensure random selection:
        1. Divide the tools/commands into roughly 100 segments.
        2. Pick the tools/commands that are closest to these random positions: {random_numbers}
        3. For each tool/command, provide:
           - A clear explanation of what it does
           - A practical example of how to use it
           - Any important considerations or warnings
        
        Format the response using Markdown with proper headers, lists, and code blocks.
        Make it look good in an email.
        
        Important: You MUST pick the tools/commands from different sections to ensure variety.
        If the random numbers point to similar tools, pick the next different tool in the list.
        
        Start with a friendly greeting and end with a nice sign-off."""
        
        try:
            result = subprocess.run(
                ['llm', '-m', 'gemini-2.0-flash-exp', prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running LLM tool: {e}")
            return None
    
    def send_email(self, markdown_content: str) -> bool:
        """Send email using SendGrid."""
        if not all([self.sendgrid_api_key, self.recipient_email]):
            raise ValueError("SendGrid API key and recipient email are required")
        
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['fenced_code', 'tables', 'codehilite']
            )
            
            # Add some basic CSS for better formatting
            styled_html = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        code {{
                            background: #f4f4f4;
                            border-radius: 4px;
                            padding: 2px 5px;
                            font-family: monospace;
                        }}
                        pre {{
                            background: #f4f4f4;
                            padding: 15px;
                            border-radius: 5px;
                            overflow-x: auto;
                        }}
                        h1, h2, h3 {{
                            color: #2c3e50;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
            </html>
            """
            
            message = Mail(
                from_email=self.sender_email,
                to_emails=self.recipient_email,
                subject='🔧 Daily Secret Knowledge Tidbits',
                html_content=styled_html
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            return response.status_code == 202
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def run(self, test_mode=True):
        """Run the complete tidbit extraction and sending process."""
        try:
            print("Extracting and analyzing tidbits...")
            markdown_content = self.get_daily_tidbits()
            
            if markdown_content:
                print("\nGenerated content:")
                print(markdown_content)
                
                if not test_mode:
                    success = self.send_email(markdown_content)
                    if success:
                        print("\nSuccessfully sent email!")
                    else:
                        print("\nFailed to send email")
                else:
                    print("\nTest mode - email not sent")
            else:
                print("\nFailed to generate content")
                
        except Exception as e:
            print(f"Error running tidbit processor: {e}")
            raise

if __name__ == "__main__":
    URLS = [
        "https://github.com/kdeldycke/awesome-falsehood?tab=readme-ov-file",
        "https://raw.githubusercontent.com/trimstray/the-book-of-secret-knowledge/refs/heads/master/README.md",
        "https://github.com/you-dont-need/You-Dont-Need-JavaScript?tab=readme-ov-file#you-dont-need-javascript",
        "https://github.com/mcinglis/c-style"
    ]
    
    random.shuffle(URLS)
    processor = SecretKnowledgeTidbits(URLS.pop())
    processor.run(test_mode=False)