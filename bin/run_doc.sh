sphinx-apidoc --force -o doc/source kokex
(
  cd "$(dirname "$0")/../doc" || exit
  make clean
  make html
)
