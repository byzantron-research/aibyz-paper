import os

# Base directory 
base_dir = r"F:\my_AI_Projects\REASEARCH\Quanteron\Byzantron\Codes\Akhun\aibyz-paper\codes"

# Folder and file structure to be created
structure = {
    "environment": ["__init__.py", "pos_env.py"],
    "agent": ["__init__.py", "base_agent.py", "marl_agent.py", "trust_score.py"],
    "xai": ["__init__.py", "explainer.py"],
    "data": ["__init__.py", "dataset_loader.py"],
    ".": ["config.py", "train.py", "evaluate.py", "utils.py", "main.py"]
}

# Create folders and files
for folder, files in structure.items():
    dir_path = os.path.join(base_dir, folder) if folder != "." else base_dir
    os.makedirs(dir_path, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(dir_path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"# {file} - generated as part of modular structure\n")

print(" Modular structure created successfully inside 'codes/'")
