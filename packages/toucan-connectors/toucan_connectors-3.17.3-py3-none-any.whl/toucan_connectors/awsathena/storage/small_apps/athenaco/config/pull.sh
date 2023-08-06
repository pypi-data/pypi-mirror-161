cd "$SMALL_APP_DIR"

if [ -z $FORCE ]; then
    git pull "$REMOTE_URL" "$BRANCH_NAME"
else
    git remote add tmp_origin "$REMOTE_URL"
    git fetch tmp_origin "$BRANCH_NAME"
    git reset --hard "tmp_origin/$BRANCH_NAME"
    git remote rm tmp_origin
fi
