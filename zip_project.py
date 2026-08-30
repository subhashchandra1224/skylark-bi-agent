import os
import zipfile

def zip_project():
    source_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(source_dir, "skylark-bi-agent-submission.zip")
    
    # Exclude these directories/files
    exclude_dirs = {".git", "venv", "node_modules", "__pycache__", "dist", "build", ".venv", "env"}
    exclude_files = {".env", "zip_project.py", "skylark-bi-agent-submission.zip"}
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip excluded directories entirely
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith(".egg-info")]
            
            for file in files:
                if file in exclude_files or file.endswith(".pyc") or file.endswith(".env"):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                
    print(f"Successfully created ZIP file at {zip_path}")

if __name__ == "__main__":
    zip_project()
