#!/bin/bash
set -e

# Check if version argument is provided
if [ $# -ne 1 ]; then
    echo "Error: Version argument is required"
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.0"
    exit 1
fi

# Get the version from the argument
VERSION=$1

# Validate version format (should be like 1.0.0)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 1.0.0)"
    exit 1
fi

# Image name
IMAGE_NAME="customer-survey-app"
CONTAINER_REPO="${CONTAINER_REPO:-$IMAGE_NAME}"

echo "Building container images for $CONTAINER_REPO:$VERSION"

# Check if Finch is installed
if ! command -v finch &> /dev/null; then
    echo "Error: Finch is not installed. Please install Finch first."
    exit 1
fi

# Function to build for a specific platform
build_for_platform() {
    local platform=$1
    local tag_suffix=$2
    local platform_flag=""
    
    echo "Building image for $platform..."
    
    # Create a platform-specific Dockerfile with a safe filename
    local safe_filename="Dockerfile_${tag_suffix}"
    
    # Add platform-specific build args
    if [ "$platform" == "linux/amd64" ]; then
        platform_flag="--platform=linux/amd64"
        echo "FROM --platform=linux/amd64 python:3.10-slim" > "$safe_filename"
        tail -n +2 Dockerfile >> "$safe_filename"
    elif [ "$platform" == "linux/arm64" ]; then
        platform_flag="--platform=linux/arm64"
        echo "FROM --platform=linux/arm64 python:3.10-slim" > "$safe_filename"
        tail -n +2 Dockerfile >> "$safe_filename"
    fi
    
    # Build the image with Finch
    finch build $platform_flag \
        -f "$safe_filename" \
        --tag "$CONTAINER_REPO:$VERSION-$tag_suffix" \
        --build-arg VERSION="$VERSION" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        .
    
    # Clean up the temporary Dockerfile
    rm "$safe_filename"
    
    echo "Successfully built $CONTAINER_REPO:$VERSION-$tag_suffix"
}

# Build for AMD64
build_for_platform "linux/amd64" "amd64"

# Build for ARM64
build_for_platform "linux/arm64" "arm64"

# Tag the native architecture as the default version
NATIVE_ARCH=$(uname -m)
if [ "$NATIVE_ARCH" == "x86_64" ]; then
    finch tag "$CONTAINER_REPO:$VERSION-amd64" "$CONTAINER_REPO:$VERSION"
    finch tag "$CONTAINER_REPO:$VERSION-amd64" "$CONTAINER_REPO:latest"
    echo "Tagged amd64 as default (latest)"
elif [ "$NATIVE_ARCH" == "arm64" ]; then
    finch tag "$CONTAINER_REPO:$VERSION-arm64" "$CONTAINER_REPO:$VERSION"
    finch tag "$CONTAINER_REPO:$VERSION-arm64" "$CONTAINER_REPO:latest"
    echo "Tagged arm64 as default (latest)"
else
    echo "Unknown architecture: $NATIVE_ARCH"
    echo "Not creating default tags"
fi

echo "Successfully built images:"
echo "- $CONTAINER_REPO:$VERSION-amd64 (x86_64)"
echo "- $CONTAINER_REPO:$VERSION-arm64 (aarch64)"
echo "- $CONTAINER_REPO:$VERSION (native architecture)"
echo "- $CONTAINER_REPO:latest (native architecture)"

# Optional: Push to a registry
if [ -n "$PUSH_TO_REGISTRY" ] && [ "$PUSH_TO_REGISTRY" = "true" ]; then
    echo "Pushing images to registry..."
    
    # Push the architecture-specific tags
    finch push "$CONTAINER_REPO:$VERSION-amd64"
    finch push "$CONTAINER_REPO:$VERSION-arm64"
    
    # Push the version tag
    finch push "$CONTAINER_REPO:$VERSION"
    
    # Push the latest tag
    finch push "$CONTAINER_REPO:latest"
    
    echo "Images pushed to registry"
fi

echo "Build process completed successfully!"
echo ""
echo "To run the AMD64 version:"
echo "  finch run -p 8000:8000 $CONTAINER_REPO:$VERSION-amd64"
echo ""
echo "To run the ARM64 version:"
echo "  finch run -p 8000:8000 $CONTAINER_REPO:$VERSION-arm64"
