#!/usr/bin/env bash
# BoxOfPorts installer — sets up the 'bop' wrapper locally
# "Once in a while you get shown the light" — let's make install one-liners easy.
set -euo pipefail

PREFIX="${PREFIX:-/usr/local}"
BIN_DIR="${BIN_DIR:-${PREFIX}/bin}"
WRAPPER_URL_DEFAULT="${WRAPPER_URL:-}"

usage() {
  cat <<EOF
Install BoxOfPorts wrapper

Environment variables:
  PREFIX            Installation prefix (default: /usr/local)
  BIN_DIR           Binary directory (default: "+${BIN_DIR}+")
  WRAPPER_URL       URL to fetch wrapper from; if empty, uses GitHub raw for this repo
  IMAGE             Docker image to embed in wrapper (default: altheasignals/boxofports:latest)

Example:
  curl -fsSL https://raw.githubusercontent.com/altheasignals/boxofports/main/scripts/install-bop.sh | bash
EOF
}

if [[ "${1-}" == "-h" || "${1-}" == "--help" ]]; then
  usage; exit 0
fi

mkdir -p "${BIN_DIR}"

# Determine wrapper URL
if [[ -z "${WRAPPER_URL_DEFAULT}" ]]; then
  # Attempt to infer GitHub raw URL for this repository branch 'main'
  WRAPPER_URL_DEFAULT="https://raw.githubusercontent.com/altheasignals/boxofports/main/scripts/bop"
fi

TMP_WRAPPER="$(mktemp)"
trap 'rm -f "${TMP_WRAPPER}"' EXIT

curl -fsSL "${WRAPPER_URL_DEFAULT}" -o "${TMP_WRAPPER}"
chmod +x "${TMP_WRAPPER}"

# Optionally inject image override
if [[ -n "${IMAGE-}" ]]; then
  # Replace default image in wrapper
  sed -i.bak "s~^DOCKER_IMAGE=\".*\"~DOCKER_IMAGE=\"${IMAGE}\"~" "${TMP_WRAPPER}" || true
  rm -f "${TMP_WRAPPER}.bak" 2>/dev/null || true
fi

install -m 0755 "${TMP_WRAPPER}" "${BIN_DIR}/bop"

echo "Installed 'bop' to ${BIN_DIR}/bop"
echo "Try: bop --help"