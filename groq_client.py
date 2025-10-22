# smartplate/groq_client.py
from groq import Groq, APIConnectionError, AuthenticationError, RateLimitError, BadRequestError
from .ui.theme_manager import ThemeManager
import traceback

class GroqClient:
    """Handles communication with the Groq API (Llama models)."""

    def __init__(self):
        self.api_key = None
        self.client = None
        self.configure_client()

    def configure_client(self):
        """Configures the Groq client with the API key from settings."""
        self.api_key = ThemeManager.get_groq_api_key()
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                print("[GroqClient] Configured successfully.")
                return True
            except Exception as e:
                print(f"[GroqClient] ERROR configuring Groq: {e}")
                self.client = None
                return False
        else:
            print("[GroqClient] API Key not found in settings.")
            self.client = None
            return False

    def generate_response(self, prompt):
        """Sends a prompt to Groq and returns the response."""
        if not self.client:
            if not self.configure_client(): # Try to configure again
                return "Error: Groq API Key not configured or invalid. Please save it in Settings."

        print(f"[GroqClient] Sending prompt: '{prompt[:50]}...'")
        try:
            # --- ✅ Use the correct, active model ---
            model_to_use = "llama-3.1-8b-instant" 
            print(f"[GroqClient] Using model: {model_to_use}")
            
            response = self.client.chat.completions.create(
                model=model_to_use, 
                # --- End Change ---
                messages=[
                    {"role": "system", "content": "You are a helpful assistant knowledgeable about health, food, and nutrition. Provide concise and informative answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250 
            )

            response_text = response.choices[0].message.content
            print(f"[GroqClient] Received response: '{response_text[:100]}...'")
            return response_text.strip()

        except AuthenticationError:
            print("[GroqClient] ERROR: Invalid Groq API Key.")
            self.client = None 
            return "Error: Invalid Groq API Key. Please check and save it in Settings."
        except RateLimitError:
            print("[GroqClient] ERROR: Groq rate limit or quota exceeded.")
            return "Error: Groq API rate limit or quota exceeded. Please check your account usage."
        except APIConnectionError as e:
            print(f"[GroqClient] ERROR: Could not connect to Groq API: {e}")
            return "Error: Could not connect to Groq. Check your internet connection."
        except BadRequestError as e:
            print(f"[GroqClient] BAD REQUEST ERROR: {e}\n{traceback.format_exc()}")
            # Show the actual error message from Groq
            return f"Error: Groq Bad Request. API responded with: {str(e)}"
        except Exception as e:
            print(f"[GroqClient] ERROR generating response: {e}\n{traceback.format_exc()}")
            return f"Error: An unexpected error occurred while contacting Groq ({type(e).__name__})."