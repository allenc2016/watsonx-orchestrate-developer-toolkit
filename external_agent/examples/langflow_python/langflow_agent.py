import os
import subprocess

from langflow_runner import run_langflow

async def run_travel_agent(input: str) -> str:
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'resources', 'Travel3.json')

    return run_langflow(file_path, {}, input)


