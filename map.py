import os

def print_structure(start_path='.', indent=''):
    for item in sorted(os.listdir(start_path)):
        full_path = os.path.join(start_path, item)
        
        # Skip the .git folder
        if item == '.git':
            continue
        
        print(indent + '├── ' + item)
        
        if os.path.isdir(full_path):
            print_structure(full_path, indent + '│   ')

print("Project Structure:")
print_structure()
