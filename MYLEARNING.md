# What I learned

## Setup

1. Install all dependencies with `pip install -r requirements.txt`. This installs androguard as a python library.
2. Install androguard as a command line tool with `pip install git+https://github.com/androguard/androguard`
3. To decode all apps, rename them all first with this code so you don't get any errors decoding.

   ```python
    def rename_files_in_folder(folder_path: str):
        illegal_filepath_symbols = [" ", "(", ")", "[", "]", "{", "}", "!", "@", "#", "$", "%", "^", "&", "*", "+", "=", "?", "<", ">", ",", ";", ":", "'", "`", "~", "|"]
        for filename in os.listdir(folder_path):
            old_path = os.path.join(folder_path, filename)
            new_path = ''.join(e for e in old_path if e not in illegal_filepath_symbols)
            os.rename(old_path, new_path)
   ```

4. Run `bash automate.sh` or make it executable to automate decoding all the apps in the `apps` folder.

## How to use androguard

### CLI

The `androguard analyze <apk-path>` command takes in one argument - the apk path to analyze. It then launches you into a python shell where you can do many things like see what activities and permissions the app has.

Examples of how to use androguard is at https://androguard.readthedocs.io/en/latest/

#### Getting manifest

The `androguard axml <apk>` command basically returns the manifest content. You can use this command to essentially get back the entire manifest of the apk as a string.

```bash
androguard axml apps/Fitbit_3.70.fitbit-mobile-37020001-481345019_Apkpure.apk > manifest.xml
```

## Linux

- You can simulate an enter on any command that requires user input by piping the command to `echo`, like `echo | <command>`.
- You can run any process in the background by adding `&` at the end of the command. You can also use the `screen <commands here>` command to run a process in the background and then detach from it by typing `Ctrl + A + D`. You can re-enter the process with `screen -r`.
  - List all screens with `screen -ls`
  - Kill a screen with `screen -X -S <screen_id> quit`
