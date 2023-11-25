# install poetry project

echo "Installing poetry project..."
poetry install

# metadock build README

echo "Metadock-building README.md..."
poetry run metadock build -s README
cp .metadock/generated_documents/README.md README.md
git add README.md

# metadock build Intellisense snippets

echo "Metadock-building Intellisense snippets..."
poetry run metadock build -s jinja-md
cp .metadock/generated_documents/jinja-md.code-snippets .vscode/jinja-md.code-snippets
git add .vscode/jinja-md.code-snippets