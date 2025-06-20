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
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

import sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from expense_tracker.agent import root_agent

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

    remote_agent = agent_engines.create(
        app,
        requirements=[
            "google-adk (==0.5.0)",
            "google-cloud-aiplatform[adk,agent_engines] (==1.94.0)",
            "google-cloud-secret-manager"
        ]
    )

    print(f"Created remote agent: {remote_agent.resource_name}")
    print(f"Before testing, run the following: export AGENT_ENGINE_ID={remote_agent.resource_name}")

if __name__ == "__main__":
    app.run(main)
