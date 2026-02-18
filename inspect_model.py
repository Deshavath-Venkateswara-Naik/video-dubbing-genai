from huggingface_hub import HfApi
api = HfApi()
files = api.list_repo_files("JaesungHuh/voice-gender-classifier")
print(files)
