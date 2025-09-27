#!/usr/bin/env bash

# retag_by_digest.sh - Retag Docker images by digest without rebuilding
# "The wheel is turning and you can't slow down" - but you can redirect
#
# Usage: retag_by_digest.sh source_ref target_tag

set -euo pipefail

# Check arguments
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 source_ref target_tag" >&2
    echo "Example: $0 altheasignals/boxofports:1.2.0 altheasignals/boxofports:stable" >&2
    exit 1
fi

SOURCE_REF="$1"
TARGET_TAG="$2"

echo "🎵 Retagging by digest..."
echo "  Source: $SOURCE_REF"
echo "  Target: $TARGET_TAG"

# Get the digest of the source reference
DIGEST=$(docker buildx imagetools inspect "$SOURCE_REF" --format '{{json .Manifest.Digest}}' | sed 's/"//g')

if [[ -z "$DIGEST" ]]; then
    echo "❌ Failed to get digest for $SOURCE_REF" >&2
    exit 1
fi

echo "  Digest: $DIGEST"

# Create the new tag pointing to the same digest
docker buildx imagetools create -t "$TARGET_TAG" "$SOURCE_REF@$DIGEST"

echo "✅ Successfully retagged $TARGET_TAG -> $SOURCE_REF@$DIGEST"