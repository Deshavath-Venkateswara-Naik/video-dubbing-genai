from huggingface_hub import HfApi
api = HfApi()

print("Searching for models with 'speechbrain' and 'gender'...")
models = api.list_models(filter=["speechbrain"], search="gender")

found = False
for model in models:
    print(f"Found: {model.modelId}")
    found = True

if not found:
    print("No models found with 'speechbrain' tag and 'gender' in name/desc.")
    print("Searching for just 'gender' models...")
    models = api.list_models(search="gender", limit=10, sort="downloads", direction=-1)
    for model in models:
        print(f"Popular gender model: {model.modelId} (Tags: {model.tags})")
