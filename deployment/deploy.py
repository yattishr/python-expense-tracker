# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl import app
import os
import sys
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# --- Added imports for packaging ---
import subprocess
import shutil
import tempfile
# --- End added imports ---

# Get the absolute path to the directory containing deploy.py (deployment)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the project root (parent of deployment)
project_root = os.path.dirname(script_dir)

# Add the project root to the Python path if it's not already there
# This is mainly for local execution of deploy.py to find expense_tracker
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now, the import should work assuming 'expense_tracker' is in the project_root
# This import is resolved locally using the sys.path modification above.
# The deployed agent will find 'expense_tracker' via extra_packages.
from expense_tracker import root_agent

def main(argv: list[str]) -> None:

    load_dotenv()

    PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
    LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
    STAGING_BUCKET = os.environ["GOOGLE_CLOUD_STORAGE_BUCKET"]

    if not PROJECT:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not LOCATION:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not STAGING_BUCKET:
        print("Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    print(f"PROJECT: {PROJECT}")
    print(f"LOCATION: {LOCATION}")
    print(f"STAGING_BUCKET: {STAGING_BUCKET}")

    vertexai.init(
        project=PROJECT,
        location=LOCATION,
        staging_bucket=f"gs://{STAGING_BUCKET}",
    )

    app = AdkApp(agent=root_agent, enable_tracing=False)

    # --- Start: Packaging the 'expense_tracker' module for deployment ---
    sdist_file_to_deploy = None
    original_cwd = os.getcwd() # Store original working directory

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Change to the project root directory
            os.chdir(project_root)

            # 2. Create a temporary setup.py in the project root
            setup_py_content = """
from setuptools import setup, find_packages

setup(
    name='expense_tracker',
    version='0.1.0', # You can update this version as needed
    packages=find_packages(),
    # If you have non-code files (like your prompt.py or sample-output.json
    # that need to be accessible within the package), you might need:
    include_package_data=True,
    package_data={
        'expense_tracker': ['prompt.py', '__init__.py'],
        'expense_tracker.sub_agents.categorizer_agent': ['prompt.py', '__init__.py'],
        'expense_tracker.sub_agents.reporter_agent': ['prompt.py', '__init__.py'],
        'expense_tracker.sub_agents.summarizer_agent': ['prompt.py', '__init__.py'],    
        'expense_tracker.sub_agents.ocr_agent': ['prompt.py', '__init__.py'],
        'expense_tracker.sub_agents.ocr_agent.agent': ['prompt.py', '__init__.py'],
        'expense_tracker.sub_agents.ocr_agent.agent.tools': ['prompt.py', '__init__.py'],        
    },
)
"""
            # Write setup.py to the project_root
            with open(os.path.join(project_root, "setup.py"), "w") as f:
                f.write(setup_py_content)

            # 3. Build the source distribution (sdist)
            print(f"Building sdist for 'expense_tracker' in {project_root}...")
            # Use 'pip install .' to ensure setuptools is available for sdist if not already
            # Or just ensure setuptools is in your deployment environment's requirements
            subprocess.run([sys.executable, "setup.py", "sdist"], check=True, capture_output=True)
            print("sdist build complete.")

            # 4. Find the generated .tar.gz file in the 'dist' directory
            dist_dir = os.path.join(project_root, "dist")
            for filename in os.listdir(dist_dir):
                if filename.startswith("expense_tracker-") and filename.endswith(".tar.gz"):
                    sdist_file_to_deploy = os.path.join(dist_dir, filename)
                    break

            if not sdist_file_to_deploy:
                raise FileNotFoundError("Could not find the generated expense_tracker sdist file.")
            print(f"Identified sdist for deployment: {sdist_file_to_deploy}")

            # 5. Pass the sdist_file_to_deploy to extra_packages
            remote_agent = agent_engines.create(
                app,
                requirements=[
                    "google-cloud-aiplatform[adk,agent_engines]",
                ],
                extra_packages=[sdist_file_to_deploy], # This is the key!
            )

    finally:
        # Clean up the temporary setup.py and dist directory
        if os.path.exists(os.path.join(project_root, "setup.py")):
            os.remove(os.path.join(project_root, "setup.py"))
        if os.path.exists(os.path.join(project_root, "dist")):
            shutil.rmtree(os.path.join(project_root, "dist"))
        # Change back to the original working directory
        os.chdir(original_cwd)
    # --- End: Packaging the 'expense_tracker' module for deployment ---

    print(f"Created remote agent: {remote_agent.resource_name}")
    print(f"Before testing, run the following: export AGENT_ENGINE_ID={remote_agent.resource_name}")

if __name__ == "__main__":
    app.run(main)