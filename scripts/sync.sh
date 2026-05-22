#!/usr/bin/env bash
# sync.sh — Bidirectional sync between laptop, GitHub, and Debian.
#
# The Debian machine often has no internet (hotspot-only).
# This script handles the full triangle: Debian → laptop → GitHub → Debian.
#
# Usage:
#   scripts/sync.sh              # pull from Debian (run this at session start)
#   scripts/sync.sh push "msg"   # commit, push to GitHub and Debian
#   scripts/sync.sh push-debian  # push to Debian only (skip GitHub)
#   scripts/sync.sh status       # show sync state
#
# ALWAYS run "scripts/sync.sh" (pull) before editing anything.

set -euo pipefail

DEBIAN_HOSTS=("dob@10.42.0.1" "dob@192.168.88.136")
DEBIAN_REPO="/home/dob/_ii"
REMOTE_NAME="debian"

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# ── Helpers ────────────────────────────────────────────────────────────────────

DEBIAN_SSH=""

find_debian() {
    if [ -n "$DEBIAN_SSH" ]; then return 0; fi
    for host in "${DEBIAN_HOSTS[@]}"; do
        if ssh -o ConnectTimeout=3 -o BatchMode=yes "$host" true 2>/dev/null; then
            DEBIAN_SSH="$host"
            return 0
        fi
    done
    return 1
}

ensure_debian_remote() {
    find_debian || { echo "[sync] Debian not reachable."; return 1; }
    local url="${DEBIAN_SSH}:${DEBIAN_REPO}"
    if git remote get-url "$REMOTE_NAME" &>/dev/null; then
        git remote set-url "$REMOTE_NAME" "$url"
    else
        git remote add "$REMOTE_NAME" "$url"
    fi
}

push_to_debian() {
    ensure_debian_remote
    echo "[sync] allowing push to checked-out branch on Debian..."
    ssh "$DEBIAN_SSH" "git -C $DEBIAN_REPO config receive.denyCurrentBranch ignore"
    echo "[sync] pushing to Debian..."
    git push "$REMOTE_NAME" HEAD:main
    local commit
    commit=$(git rev-parse HEAD)
    echo "[sync] resetting Debian worktree to $commit..."
    ssh "$DEBIAN_SSH" "git -C $DEBIAN_REPO reset --hard $commit"
    echo "[sync] restarting affected services on Debian..."
    ssh "$DEBIAN_SSH" "cd $DEBIAN_REPO && scripts/update-and-restart.sh" 2>/dev/null \
        || ssh "$DEBIAN_SSH" "~/bin/ii restart ctrl; ~/bin/ii restart vis; ~/bin/ii restart web"
    echo "[sync] Debian is live."
}

# ── Commands ───────────────────────────────────────────────────────────────────

cmd_pull() {
    if ! ensure_debian_remote 2>/dev/null; then
        echo "[sync] Debian not reachable — skipping pull, using local state."
        return 0
    fi
    echo "[sync] fetching from Debian (${DEBIAN_SSH})..."
    git fetch "$REMOTE_NAME"

    local local_commit remote_commit
    local_commit=$(git rev-parse HEAD)
    remote_commit=$(git rev-parse "$REMOTE_NAME/main")

    if [ "$local_commit" = "$remote_commit" ]; then
        echo "[sync] already in sync with Debian."
        return 0
    fi

    if git merge-base --is-ancestor HEAD "$REMOTE_NAME/main"; then
        echo "[sync] Debian is ahead — fast-forwarding local..."
        git merge --ff-only "$REMOTE_NAME/main"
    elif git merge-base --is-ancestor "$REMOTE_NAME/main" HEAD; then
        local n
        n=$(git rev-list "$REMOTE_NAME/main"..HEAD --count)
        echo "[sync] local is $n commit(s) ahead of Debian — OK to proceed."
    else
        echo "[sync] DIVERGED — rebasing local commits on top of Debian..."
        git rebase "$REMOTE_NAME/main"
    fi
    echo "[sync] local is now up to date."
}

cmd_push() {
    local msg="${1:-sync: $(date '+%Y-%m-%d %H:%M')}"

    git add -A
    if ! git diff --cached --quiet; then
        git commit -m "$msg"
        echo "[sync] committed: $msg"
    else
        echo "[sync] nothing new to commit."
    fi

    echo "[sync] pushing to GitHub..."
    if PATH="/usr/bin:$PATH" git push origin main 2>&1; then
        echo "[sync] GitHub up to date."
    else
        echo "[sync] WARN: GitHub push failed (no internet?) — continuing to Debian."
    fi

    if find_debian; then
        push_to_debian
    else
        echo "[sync] WARN: Debian not reachable — skipped."
        echo "       When Debian is reachable: scripts/sync.sh push-debian"
    fi
}

cmd_push_debian() {
    find_debian || { echo "[sync] ERROR: Debian not reachable." >&2; exit 1; }
    push_to_debian
}

cmd_status() {
    echo "=== sync status ==="
    echo "local:  $(git log -1 --oneline)"

    if ensure_debian_remote 2>/dev/null; then
        git fetch "$REMOTE_NAME" -q
        echo "debian: $(git log -1 --oneline "$REMOTE_NAME/main")"
        local local_commit remote_commit
        local_commit=$(git rev-parse HEAD)
        remote_commit=$(git rev-parse "$REMOTE_NAME/main")

        if [ "$local_commit" = "$remote_commit" ]; then
            echo "status: IN SYNC"
        elif git merge-base --is-ancestor HEAD "$REMOTE_NAME/main"; then
            local n
            n=$(git rev-list HEAD.."$REMOTE_NAME/main" --count)
            echo "status: Debian is $n commit(s) AHEAD — run: scripts/sync.sh pull"
        elif git merge-base --is-ancestor "$REMOTE_NAME/main" HEAD; then
            local n
            n=$(git rev-list "$REMOTE_NAME/main"..HEAD --count)
            echo "status: local is $n commit(s) ahead — run: scripts/sync.sh push"
        else
            echo "status: DIVERGED — run: scripts/sync.sh pull (will rebase)"
        fi
    else
        echo "debian: not reachable"
    fi
}

case "${1:-pull}" in
    pull)        cmd_pull ;;
    push)        cmd_push "${2:-}" ;;
    push-debian) cmd_push_debian ;;
    status)      cmd_status ;;
    *)
        echo "usage: scripts/sync.sh [pull|push [msg]|push-debian|status]"
        exit 1
        ;;
esac
