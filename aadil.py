from utilities import OSUtils, Markdowner, JSONPermissions
import os
import re
import datetime
import sys

# ------------- GLOBALS --------------- #

sensitive_permissions = [
    'android.permission.CAMERA',
    'android.permission.RECORD_AUDIO',
    'android.permission.READ_SMS',
    'android.permission.READ_CONTACTS',
    'android.permission.READ_PHONE_STATE',
    'android.permission.READ_CALL_LOG',
    'android.permission.READ_EXTERNAL_STORAGE',
    'android.permission.WRITE_EXTERNAL_STORAGE',
    'android.permission.ACCESS_FINE_LOCATION',
    'android.permission.ACCESS_COARSE_LOCATION',
    'android.permission.CALL_PHONE',
    'android.permission.SEND_SMS',
]

json_permissions = JSONPermissions()
date = datetime.datetime.now().strftime("%m-%d-%Y %H-%M")
markdowner = Markdowner(f"results/output-{date}.md")

global_paths = {
    "APK_DIR": "apps",
    "DECODED_APK_DIR": "decoded_apks",
    "output_path": None,
    "manifest_file_path": None,
    "package_name": None,
    "app_dir": None
}

# ------------- FUNCTIONS --------------- #

def disassemble_apk(filepath: str):
    # given a filepath, run apktool on the apk
    apk_name = os.path.basename(filepath)
    output_path = os.path.join(global_paths["DECODED_APK_DIR"], apk_name.replace(".apk", ""))
    global_paths["output_path"] = output_path

    # Don't decode if the output path already exists
    if os.path.exists(output_path):
        if (os.path.exists(os.path.join(output_path, "AndroidManifest.xml"))):
            print(f"Output path already exists. Skipping decoding for {apk_name}...")
            return
        else:
            OSUtils.run_unix_command(f"rm -rf {output_path}")

    print(f"Decoding {apk_name} ...")
    # OSUtils.run_unix_command(f"echo | apktool d \"{filepath}\" -o {output_path} > /dev/null 2>>results/errors.txt")
    OSUtils.run_unix_command(f"echo | apktool d \"{filepath}\" -o {output_path}")

def get_important_paths():
    manifest_file_path = os.path.join(global_paths["output_path"], "AndroidManifest.xml")
    global_paths["manifest_file_path"] = manifest_file_path

    package_name = extract_package_name(manifest_file_path)
    global_paths["package_name"] = package_name

    app_dir = os.path.join(global_paths["output_path"], "smali", package_name.replace(".", "/"))
    global_paths["app_dir"] = app_dir

def extract_package_name(manifest_file_path: str):
    print(f"extracting package name from AndroidManifest.xml file at {manifest_file_path} ...")
    with open(manifest_file_path, 'r') as f:
        content = f.read()
        match = re.search(r'package="(.+?)"', content, flags=re.IGNORECASE)
        package_name = match.groups()[0]
    return package_name

def check_has_internet_permission(manifest_path: str):
    manifest_content = OSUtils.read_file(manifest_path)
    if 'android.permission.INTERNET' in manifest_content:
        return True
    return False

def tally_sensitive_permissions(manifest_path: str):
    manifest_content = OSUtils.read_file(manifest_path)
    permissions = re.findall(r'<uses-permission android:name="([^"]+)"', manifest_content)
    sensitive_permissions_count = 0
    permissions_list = []
    for permission in permissions:
        if permission in sensitive_permissions:
            permissions_list.append(permission)
            sensitive_permissions_count += 1

    permissions_dict = { permission: 1 for permission in permissions_list }
    return sensitive_permissions_count, permissions_dict

def validate_manifest_path():
    manifest_path = os.path.join(global_paths["output_path"], "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        return False
    return True


# ------------- MAIN --------------- #

def main():
    for filename in os.listdir(global_paths["APK_DIR"]):
            if OSUtils.isWindows():
                # print("running in git bash")
                disassemble_apk(f'{global_paths["APK_DIR"]}/{filename}')
            if OSUtils.isLinux():
                # print("running in wsl")
                disassemble_apk(f'{global_paths["APK_DIR"]}/{filename}')
            if not validate_manifest_path():
                print(f"Error: Could not find AndroidManifest.xml for {global_paths['package_name']}")
                continue
            get_important_paths()
            print(global_paths)
            manifest_path = global_paths["manifest_file_path"]
            hasInternetPermission = check_has_internet_permission(manifest_path)
            if hasInternetPermission:
                print(f'Internet permission found for {global_paths["package_name"]}')
                sensitive_perms_count, permissions_dict = tally_sensitive_permissions(manifest_path)
                json_permissions.write(permissions_dict)
                json_permissions.addInternet()
                # print("Found sensitive permissions")
                markdowner.write_heading(f'Results for {global_paths["output_path"]}', level=2)
                markdowner.write(f"Sensitive permissions count: {sensitive_perms_count}\n")
                permissions_list = [permission for permission in permissions_dict]
                markdowner.write_bullet(f"Sensitive permissions")
                for permission in permissions_list:
                    markdowner.write(f"\t- {permission}")
            else: 
                print("Internet permission not found")
        
if __name__ == "__main__":
    # write stuff down in markdown file
    markdowner.write_heading(f"RQ2 analysis", level=1)
    markdowner.write("These are the apps that have internet permission and sensitive permissions")

    # Clear the errors file
    with open("results/errors.txt", 'w') as f:
        f.write("")

    # main loop
    main()
