import os

def generate_tree(path, prefix=""):
    contents = sorted(os.listdir(path))
    pointers = ['├── '] * (len(contents) - 1) + ['└── ']
    
    for pointer, name in zip(pointers, contents):
        full_path = os.path.join(path, name)
        print(prefix + pointer + name)
        if os.path.isdir(full_path):
            extension = '│   ' if pointer == '├── ' else '    '
            generate_tree(full_path, prefix + extension)

# Change '.' to the root directory you want to map
print("Project Structure:")
generate_tree(".")
