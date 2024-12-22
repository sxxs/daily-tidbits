import subprocess
import os
import random

class SecretKnowledgeTidbits:
    def __init__(self, readme_url: str):
        self.readme_url = readme_url
        self.ifttt_webhook_url = os.environ.get('IFTTT_WEBHOOK_URL')
    
    def get_daily_tidbits(self) -> str:
        """Use LLM to extract and explain three random tidbits."""
        # Generate three random numbers between 1-100 to help force randomness
        random_numbers = [random.randint(1, 100) for _ in range(3)]
        
        prompt = f"""Go to this URL and read the content: {self.readme_url}
        
        You are a helpful assistant that will extract and explain interesting tools/commands from the Book of Secret Knowledge README.
        
        To ensure random selection:
        1. Divide the tools/commands into roughly 100 segments.
        2. Pick the tools/commands that are closest to these random positions: {random_numbers}
        3. For each tool/command, provide:
           - A clear explanation of what it does
           - A practical example of how to use it
           - Any important considerations or warnings
        
        Format the response as a friendly email that would be interesting to a developer or sysadmin.
        Keep your explanations concise but informative.
        
        Important: You MUST pick the tools/commands from different sections to ensure variety.
        If the random numbers point to similar tools, pick the next different tool in the list."""
        
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
    
    def send_to_ifttt(self, content: str) -> bool:
        """Send the content to IFTTT webhook."""
        if not self.ifttt_webhook_url:
            raise ValueError("IFTTT webhook URL not configured")
            
        import requests
        payload = {
            "value1": "",
            "value2": content
        }
        
        response = requests.post(self.ifttt_webhook_url, json=payload)
        return response.status_code == 200
    
    def run(self, test_mode=True):
        """Run the complete tidbit extraction and sending process."""
        try:
            print("Extracting and analyzing tidbits...")
            email_content = self.get_daily_tidbits()
            
            if email_content:
                print("\nGenerated email:")
                print(email_content)
                
                if not test_mode and self.ifttt_webhook_url:
                    success = self.send_to_ifttt(email_content)
                    if success:
                        print("\nSuccessfully sent today's tidbits!")
                    else:
                        print("\nFailed to send tidbits to IFTTT")
            else:
                print("\nFailed to generate content")
                
        except Exception as e:
            print(f"Error running tidbit processor: {e}")
            raise

if __name__ == "__main__":
    GITHUB_README_URL = "https://raw.githubusercontent.com/trimstray/the-book-of-secret-knowledge/refs/heads/master/README.md"
    
    processor = SecretKnowledgeTidbits(GITHUB_README_URL)
    processor.run(test_mode=False)