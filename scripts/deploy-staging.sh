#!/usr/bin/env bash
set -euo pipefail
umask 077

# Run inside an uploaded release directory. Secrets stay on the VPS.
deploy_root="${1:?deployment root is required}"
image_tag="${2:?image tag is required}"
registry="${3:-ghcr.io/programmisto}"
[[ "$deploy_root" =~ ^/[a-zA-Z0-9/_-]+$ && "$deploy_root" != / ]]
[[ "$image_tag" =~ ^sha-[0-9a-f]{40}$ ]]
[[ "$registry" =~ ^ghcr.io/[a-z0-9][a-z0-9_./-]+$ ]]
release_dir="$(pwd -P)"
deploy_root="$(realpath "$deploy_root")"
[[ "$release_dir" == "$deploy_root"/releases/* ]]
[[ -f "$deploy_root/.env.staging" ]]
[[ -f "$release_dir/docker-compose.prod.yml" ]]

# Also prevent overlapping manual deployments on the VPS.
exec 9>"$deploy_root/.deploy.lock"
flock -n 9 || { echo "Another deployment is running" >&2; exit 1; }
printf 'DOCKER_REGISTRY=%s\nIMAGE_TAG=%s\n' "$registry" "$image_tag" > "$release_dir/.image.env"
compose=(docker compose --project-name programmisto-staging
         --env-file "$deploy_root/.env.staging" --env-file "$release_dir/.image.env"
         -f "$release_dir/docker-compose.prod.yml")
"${compose[@]}" config --quiet
"${compose[@]}" pull --policy always
if ! "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180; then
    "${compose[@]}" ps -a
    echo "Deployment failed. current symlink was not promoted; inspect container logs." >&2
    exit 1
fi
"${compose[@]}" exec -T programmisto_auth python -m alembic current
"${compose[@]}" exec -T programmisto_integration python -m alembic current
previous="$(readlink -f "$deploy_root/current" 2>/dev/null || true)"
if [[ -n "$previous" && "$previous" != "$release_dir" && "$previous" == "$deploy_root"/releases/* ]]; then
    ln -sfnT -- "$previous" "$deploy_root/previous"
fi
ln -sfnT -- "$release_dir" "$deploy_root/current"
"${compose[@]}" ps
printf 'Deployment ready: %s\n' "$image_tag"
