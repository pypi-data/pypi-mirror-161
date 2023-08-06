cd "$SMALL_APP_DIR"

if [ -z $FORCE ]; then
    git push "$REMOTE_URL" "$BRANCH_NAME"
else
    git push "$REMOTE_URL" "$BRANCH_NAME" --force
fi
