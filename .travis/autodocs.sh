# Adapted from https://gist.github.com/willprice/e07efd73fb7f13f917ea
#!/usr/bin/env sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI for Pantry Raid"
  git config --global github.user "travis-pantry-raid"
}

commit_docs() {
  git add docs/pantry_raid
  git checkout master
  git commit --message "[skip travis] Autodocs from commit $TRAVIS_COMMIT" -m "$TRAVIS_COMMIT_MESSAGE"
}

upload_files() {
  git remote set-url origin https://${GITHUB_TOKEN}@github.com/jepeffer/Pantry-Raid.git
  git push --force
}

setup_git
commit_docs
upload_files
