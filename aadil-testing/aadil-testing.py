import os
jadx_path_wsl = "/mnt/c/Users/Waadl/Documents/jadx-folder/bin/jadx"

def run_unix_command(command: str):
    try: 
        os.system(command)
    except Exception as e:
        print(f"Are you running in the correct environment? Error: {e}")

if __name__ == "__main__":
    run_unix_command(f"{jadx_path_wsl} -d decoded_apks_jadx/mercedes -r apps/_Mercedes-me_2.13.12_Apkpure.apk")