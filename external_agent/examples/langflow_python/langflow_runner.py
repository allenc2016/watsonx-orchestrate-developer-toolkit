import os
import subprocess
from dotenv import load_dotenv

def run_langflow(langflow_json_path: str, envs: dict, input: str) -> str:
    '''
    Given path to a langflow JSON, run it and return its output
    '''

    # we can also load from dot_env
    load_dotenv()

    # override environment variable based on provided values
    if envs: 
        for key, value in envs.items():
            os.environ[key] = value

    # Define the command as a list of arguments
    command = [
#        "echo",
        "uv",
        "run",
        "lfx",
        "run",
        "-f", "text",
        langflow_json_path,
        f"\"{input}\""
    ]

    # Run the command
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("command failed with return code", e.returncode)
        raise RuntimeError(f"command failed with return code: {e.returncode}") from e
        
    # Print the output
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return result.stdout


