#!/usr/bin/env python
import subprocess
import os
import xml.etree.ElementTree as ET
import argparse






def get_existing_libraries(output_file):
    existing_libraries = {}
    try:
        with open(output_file, 'r') as f:
            for line in f:
                library, count = line.strip().split(': ')
                existing_libraries[library] = int(count)
    except FileNotFoundError:
        pass
    print(existing_libraries)
    return existing_libraries

def get_manifest_libraries(manifest_path):
    libraries_count = []
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns_map = {'android': 'http://schemas.android.com/apk/res/android'}
    for child in root.findall('.//uses-library', ns_map):
        library = child.get('{http://schemas.android.com/apk/res/android}name')
        if library not in libraries_count:
            libraries_count.append(library)
    return libraries_count

def update_libraries_count(existing_libraries, libraries_count):
    for library in libraries_count:
        if library in existing_libraries:
            existing_libraries[library] += 1
        else:
            existing_libraries[library] = 1
    return existing_libraries

def write_libraries_to_file(manifest_path, output_file):
    libraries_count = get_manifest_libraries(manifest_path)
    existing_libraries = get_existing_libraries("library.txt")
    updated_libraries = update_libraries_count(existing_libraries, libraries_count)
    with open(output_file, 'w') as f:
        for library, count in updated_libraries.items():
            f.write(f"{library}: {count}\n")


def get_existing_permissions(output_file):
    existing_permissions = {}
    try:
        with open(output_file, 'r') as f:
            for line in f:
                permission, count = line.strip().split(': ')
                existing_permissions[permission] = int(count)
    except FileNotFoundError:
        pass
    print(existing_permissions)
    return existing_permissions

def get_manifest_permissions(manifest_path):
    permissions_count = []
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns_map = {'android': 'http://schemas.android.com/apk/res/android'}
    for child in root.findall('.//uses-permission', ns_map):
        permission = child.get('{http://schemas.android.com/apk/res/android}name')
        if permission not in permissions_count:
            permissions_count.append(permission)
    return permissions_count

def update_permissions_count(existing_permissions, permissions_count):
    for permission in permissions_count:
        if permission in existing_permissions:
            existing_permissions[permission] += 1
        else:
            existing_permissions[permission] = 1
    return existing_permissions

def write_permissions_to_file(manifest_path, output_file):
    permissions_count = get_manifest_permissions(manifest_path)
    existing_permissions = get_existing_permissions(output_file)
    updated_permissions = update_permissions_count(existing_permissions,permissions_count)
    with open(output_file, 'w') as f:
        for permission, count in updated_permissions.items():
            f.write(f"{permission}: {count}\n")

def decode_apks(root_apps):
    files = os.listdir(root_apps)
    apk_files = [f for f in files if f.endswith('.apk')]
    apk_tool_path = "/usr/local/bin/apktool.jar"
    for apk in apk_files:
        apk_path = os.path.join(root_apps, apk)
        decoded_app = f"/Users/nicholasrose/mobile-app-final/Apps/{os.path.splitext(apk)[0]}"
        try:
            subprocess.run(['apktool', 'd', '-f', apk_path, '-o', decoded_app], check=True)
            print("APK disassembly successful. Output directory:", decoded_app)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
        manifest_path = os.path.join(decoded_app, 'AndroidManifest.xml')
        try:
            package_name = get_package_name(manifest_path)
            write_permissions_to_file(manifest_path, "permissions.txt")
            write_libraries_to_file(manifest_path, 'library.txt')
            search_for_setJavaScriptEnabled_mentions(decoded_app, manifest_path)

        except FileNotFoundError:
            print("ANDROIDMANIFEST.XML FILE NOT FOUND")


def rename_files_in_folder(folder_path: str):
        illegal_filepath_symbols = [" ", "(", ")", "[", "]", "{", "}", "!", "@", "#", "$", "%", "^", "&", "*", "+", "=", "?", "<", ">", ",", ";", ":", "'", "`", "~", "|"]
        for filename in os.listdir(folder_path):
            old_path = os.path.join(folder_path, filename)
            new_path = ''.join(e for e in old_path if e not in illegal_filepath_symbols)
            os.rename(old_path, new_path)



def disassemble_apk(apk_path, output_dir):
    if not is_apktool_installed():
        print("Apktool is not installed")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        subprocess.run(['apktool', 'd', '-f', apk_path, '-o', output_dir], check=True)
        print("APK disassembly successful. Output directory:", output_dir)
    except subprocess.CalledProcessError as e:
        print("Error:", e)

def is_apktool_installed():
    try:
        subprocess.run(['apktool', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False



def get_package_name(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    return root.attrib['package']

def search_for_setJavaScriptEnabled_mentions(output_dir, manifest_path):
    package_name = get_package_name(manifest_path)
    setJavaScriptEnabled_mentions = []

    package_dir = os.path.join(output_dir, 'smali', package_name.replace('.', os.sep))

    for root, dirs, files in os.walk(package_dir):
        for file_name in files:
            if file_name.endswith('.smali'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, start=1):
                        if 'setJavaScriptEnabled' in line:
                            parts = file_path.split('/')
                            filename = parts[-1]
                            setJavaScriptEnabled_mentions.append((package_name, filename, i, "setJavaScriptEnabled mention"))
                            break  # Stop after the first mention in this file

    if setJavaScriptEnabled_mentions:
        save_setJavaScriptEnabled_mentions_to_file(setJavaScriptEnabled_mentions)
    return len(setJavaScriptEnabled_mentions)

def save_setJavaScriptEnabled_mentions_to_file(setJavaScriptEnabled_mentions):
    with open("output.txt", 'a') as f:
        for package_name, file_path, line_number, mention_type in setJavaScriptEnabled_mentions:
            f.write(f"{package_name}: {file_path}: {line_number}: {mention_type}\n")
    print("setJavaScriptEnabled mentions saved to output.txt")

def count_distinct_package_names(file_path):
    package_names = set()

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split(': ')
            if len(parts) > 2:
                package_name = parts[0].strip()
                if package_name not in package_names:
                    package_names.add(package_name)

    distinct_count = len(package_names)
    return distinct_count


if __name__ == "__main__":
    folder_path = "/Users/nicholasrose/ROOTAPPS"
    decode_apks(folder_path)
    print(count_distinct_package_names('/Users/nicholasrose/mobile-app-final/output.txt'))
    
    
    
