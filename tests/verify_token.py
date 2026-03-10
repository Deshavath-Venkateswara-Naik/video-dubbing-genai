import os
from huggingface_hub import HfApi
from app.config import HF_TOKEN

def check_token():
    print(f"Checking token: {HF_TOKEN[:5]}...{HF_TOKEN[-5:]}")
    api = HfApi(token=HF_TOKEN)
    try:
        user = api.whoami()
        print(f"Logged in as: {user['name']}")
        
        # Try to check access to the model
        model_id = "ai4bharat/indictrans2-en-indic-dist-200M"
        try:
            api.model_info(model_id)
            print(f"SUCCESS: Token has access to {model_id}")
        except Exception as e:
            print(f"FAILURE: Token does NOT have access to {model_id}. Error: {e}")
            
    except Exception as e:
        print(f"FAILURE: Token is invalid or expired. Error: {e}")

if __name__ == "__main__":
    check_token()
