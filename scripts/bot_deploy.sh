#!/bin/bash
# bot_deploy.sh

# Load environment variables
source .env

deploy_bot() {
    echo "Deploying Hooter-the-Tutor bot to Cloud Run..."

    # Build and push Docker image
    docker build -t "${DOCKER_REPO_URL}:latest" .
    docker push "${DOCKER_REPO_URL}:latest"

    # Deploy to Cloud Run
    gcloud run deploy "$BOT_SERVICE_NAME" \
        --image "${DOCKER_REPO_URL}:latest" \
        --platform managed \
        --region "$REGION" \
        --memory "${MEMORY_LIMIT:-512Mi}" \
        --cpu "${CPU_LIMIT:-1}" \
        --max-instances "${MAX_INSTANCES:-1}" \
        --min-instances "${MIN_INSTANCES:-1}" \
        --concurrency "${MAX_CONCURRENCY:-80}" \
        --timeout "${TIMEOUT:-240}" \
        --port 8080 \
        --allow-unauthenticated \
        --execution-environment="${EXECUTION_ENVIRONMENT:-gen2}" \
        --cpu-boost

    echo "Bot deployed to Cloud Run"
}

update_bot() {
    echo "Updating Hooter-the-Tutor bot..."

    # Build and push new Docker image
    docker build -t "${DOCKER_REPO_URL}:latest" .
    docker push "${DOCKER_REPO_URL}:latest"

    # Update Cloud Run service
    gcloud run services update "$BOT_SERVICE_NAME" \
        --image "${DOCKER_REPO_URL}:latest" \
        --platform managed \
        --region "$REGION" \
        --memory "${MEMORY_LIMIT:-512Mi}" \
        --cpu "${CPU_LIMIT:-1}" \
        --max-instances "${MAX_INSTANCES:-1}" \
        --min-instances "${MIN_INSTANCES:-1}" \
        --concurrency "${MAX_CONCURRENCY:-80}" \
        --timeout "${TIMEOUT:-240}" \
        --port 8080 \
        --execution-environment="${EXECUTION_ENVIRONMENT:-gen2}" \
        --cpu-boost

    echo "Bot updated on Cloud Run"
}

# Check if bot service exists
if ! gcloud run services describe "$BOT_SERVICE_NAME" --platform managed --region "$REGION" &> /dev/null; then
    deploy_bot
else
    update_bot
fi

echo "Bot deployment script completed."