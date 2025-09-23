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

# Install shell completion
install_completion() {
  # Determine user's shell and completion directory
  local user_shell="$(basename "${SHELL:-/bin/bash}")"
  local completion_installed=0
  
  case "$user_shell" in
    bash)
      # Try common bash completion directories
      for comp_dir in \
        "${HOME}/.bash_completion.d" \
        "/usr/local/etc/bash_completion.d" \
        "/etc/bash_completion.d" \
        "${PREFIX}/etc/bash_completion.d"; do
        
        if [[ -d "$comp_dir" ]] || mkdir -p "$comp_dir" 2>/dev/null; then
          if curl -fsSL "${WRAPPER_URL_DEFAULT%/bop}/bop-completion.bash" -o "${comp_dir}/bop" 2>/dev/null; then
            echo "✓ Bash completion installed to ${comp_dir}/bop"
            echo "  Run 'source ~/.bashrc' or start a new shell to enable completion"
            completion_installed=1
          fi
          break
        fi
      done
      ;;
    zsh)
      # Try common zsh completion directories
      for comp_dir in \
        "${HOME}/.zsh/completions" \
        "${HOME}/.oh-my-zsh/completions" \
        "/usr/local/share/zsh/site-functions" \
        "${PREFIX}/share/zsh/site-functions"; do
        
        if [[ -d "$comp_dir" ]] || mkdir -p "$comp_dir" 2>/dev/null; then
          if curl -fsSL "${WRAPPER_URL_DEFAULT%/bop}/bop-completion.bash" -o "${comp_dir}/_bop" 2>/dev/null; then
            echo "✓ Zsh completion installed to ${comp_dir}/_bop"
            echo "  Run 'autoload -U compinit && compinit' or start a new shell"
            completion_installed=1
          fi
          break
        fi
      done
      ;;
  esac
  
  # Fallback: install to user's home directory
  if [[ $completion_installed -eq 0 ]]; then
    local fallback_file="${HOME}/.bop-completion.bash"
    if curl -fsSL "${WRAPPER_URL_DEFAULT%/bop}/bop-completion.bash" -o "$fallback_file" 2>/dev/null; then
      echo "✓ Completion script downloaded to ${fallback_file}"
      echo "  Add 'source ${fallback_file}' to your shell config (~/.bashrc or ~/.zshrc)"
    else
      echo "⚠ Could not download completion script - tab completion will not be available"
      echo "  You can manually download from: ${WRAPPER_URL_DEFAULT%/bop}/bop-completion.bash"
    fi
  fi
}

# Install completion if URL is available
if [[ "${WRAPPER_URL_DEFAULT}" != *"github"* ]] || curl -fsSL "${WRAPPER_URL_DEFAULT%/bop}/bop-completion.bash" --head >/dev/null 2>&1; then
  install_completion
else
  echo "⚠ Completion script not available from source - tab completion will not be installed"
fi

echo "Try: bop --help"
