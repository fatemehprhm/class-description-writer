import os
import ast
import argparse
from openai import OpenAI


def get_python_files(src_dir):
    python_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_classes_and_methods(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=file_path)
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'methods': []
            }
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    method_info = {
                        'name': child.name,
                    }
                    class_info['methods'].append(method_info)
            classes.append(class_info)
    
    return classes

def generate_class_description(client, class_name, methods):
    methods_descriptions = ""
    for method in methods:
        methods_descriptions += f"\nMethod Name: {method['name']}\n"

    prompt = f"Generate a short description for the following Python class based on its functions and init section:\n\nClass Name: {class_name}\n\nMethods:\n{methods_descriptions}\n\nDescription:"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system", "content": "You are a helpful assistant."
            },
            {
                "role": "user", "content": prompt
            }
        ],
        max_tokens=2000,
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_readme(client, classes_info):
    readme_content = "# Project Documentation\n\n"
    for file, classes in classes_info.items():
        readme_content += f"## {os.path.basename(file)}\n\n"
        for class_info in classes:
            class_description = generate_class_description(client, class_info['name'], class_info['methods'])
            readme_content += f"### Class: {class_info['name']}\n\n"
            readme_content += f"{class_description}\n\n"
    
    return readme_content

def main(api_key, src_dir, output_file):
    client = OpenAI(api_key=api_key)
    python_files = get_python_files(src_dir)
    
    classes_info = {}
    for file in python_files:
        classes_info[file] = extract_classes_and_methods(file)
    
    readme_content = generate_readme(client, classes_info)
    
    with open(output_file, "w", encoding='utf-8') as readme_file:
        readme_file.write(readme_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate README documentation for Python classes using OpenAI API.")
    parser.add_argument('--api_key', type=str, required=True, help="OpenAI API key.")
    parser.add_argument('--src_dir', type=str, required=True, help="Source directory containing Python files.")
    parser.add_argument('--output_file', type=str, required=True, help="Output file name for the generated README.")
    
    args = parser.parse_args()
    main(args.api_key, args.src_dir, args.output_file)