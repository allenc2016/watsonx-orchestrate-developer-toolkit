
#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found!"
  exit 1
fi

# Run the Docker container
docker run --name travel-planner-agent -d -e GEMINI_API_KEY=$GEMINI_API_KEY -p 8002:8080 langflow-agent:0.1 