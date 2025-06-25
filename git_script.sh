read -r -p "Enter Commit _> " commit 
echo "Commit, ${commit}"

if [ -z "${commit}" ]; then
  echo "Commit Message is Empty"
  exit 1
fi
git add . 
git status
git commit -m "${commit}"
git push -u origin main 
