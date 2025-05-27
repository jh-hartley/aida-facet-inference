#!/bin/bash

echo "Setting up Git hooks..."
cp pre-commit ../.git/hooks/pre-commit
chmod +x ../.git/hooks/pre-commit
echo "Git hooks set up successfully!" 