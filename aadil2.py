from utilities import OSUtils, Markdowner, JSONCreator
import os
import re
import datetime

date = datetime.datetime.now().strftime("%m-%d-%Y %H-%M")
markdowner = Markdowner(f"results/output-rq4-{date}.md")
jsoner = JSONCreator("results/rq4.json")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

global_paths = {
    "APK_DIR": "apps",
    "DECODED_APK_DIR": "decoded_apks",
    "output_path": None,
    "manifest_file_path": None,
    "package_name": None,
    "app_dir": None
}

def extract_package_name(manifest_file_path: str):
    print(f"extracting package name from AndroidManifest.xml file at {manifest_file_path} ...")
    with open(manifest_file_path, 'r') as f:
        content = f.read()
        match = re.search(r'package="(.+?)"', content, flags=re.IGNORECASE)
        package_name = match.groups()[0]
    return package_name

def check_for_hostname_verifier(filepath, content):
    vulnerabilities = 0
    def add_file_link(file_path , line_number):
        return  f"[Go to file]({file_path}#L{line_number})"
    
    if "AllowAllHostnameVerifier" in content:
        print(f"AllowAllHostnameVerifier found in file: {filepath}")
        markdowner.write_heading(f"`AllowAllHostnameVerifier` vulnerabilities found in file: `{filepath}`\n", level=3)

        for match in re.finditer(r'.*AllowAllHostnameVerifier.*', 
                                 content, 
                                 flags=re.MULTILINE):
            line_number = content.count("\n", 0, match.start()) + 1
            text = match.group()
            markdowner.write_bullet(f"""found AllowAllHostnameVerifier at line {line_number}. {add_file_link(filepath, line_number)}\n\n```smali\n{text}\n```\n""")
            vulnerabilities += 1
    return vulnerabilities

def extract_vulnerability():
    app_dir = global_paths["app_dir"]
    print(app_dir)
    vulnerability_count = 0
    for root, _, files in os.walk(app_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
                vulnerability_count = check_for_hostname_verifier(file_path, content)
    if vulnerability_count == 0:
        return None
    return { app_dir: vulnerability_count }

if __name__ == "__main__":
    vulnerabilities = []
    markdowner.write_heading("RQ4: How many apps use the AllowAllHostnameVerifier class?", level=1)

    for foldername in os.listdir(global_paths["DECODED_APK_DIR"]):
        global_paths["output_path"] = os.path.join(global_paths["DECODED_APK_DIR"], foldername)
        global_paths["manifest_file_path"] = os.path.join(global_paths["output_path"], "AndroidManifest.xml")
        if not os.path.exists(global_paths["manifest_file_path"]):
            print(f"AndroidManifest.xml file not found at {global_paths['manifest_file_path']}")
            continue
        global_paths["package_name"] = extract_package_name(global_paths["manifest_file_path"])
        package_name = global_paths["package_name"]
        app_dir = os.path.join(global_paths["output_path"], "smali", package_name.replace(".", "/"))
        global_paths["app_dir"] = app_dir

        if not os.path.exists(app_dir):
            print(f"{bcolors.WARNING}smali directory not found at {app_dir}{bcolors.ENDC}")
            continue

        obj = extract_vulnerability()
        print(obj)
        if obj:
            vulnerabilities.append(obj)

    jsoner.write(vulnerabilities)