#!/bin/bash

# Script to add your project to GitHub

echo "🚀 Setting up GitHub repository for AI Language Learning Platform"
echo "==============================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if GitHub CLI is installed (optional but helpful)
HAS_GH=false
if command -v gh &> /dev/null; then
    HAS_GH=true
    echo "✅ GitHub CLI detected. This will make the process easier."
else
    echo "⚠️ GitHub CLI not detected. We'll use manual steps instead."
    echo "   Consider installing GitHub CLI for easier setup: https://cli.github.com/"
fi

# Check if a remote is already configured
if git remote -v | grep -q origin; then
    echo "⚠️ A remote repository is already configured:"
    git remote -v
    read -p "Do you want to continue with this remote? (y/n): " use_existing
    if [[ $use_existing != "y" ]]; then
        read -p "Enter new remote name (e.g., origin): " remote_name
        read -p "Enter new remote URL (e.g., https://github.com/username/repo.git): " remote_url
        git remote remove origin
        git remote add $remote_name $remote_url
        echo "✅ Remote updated to $remote_name: $remote_url"
    fi
else
    # No remote configured
    if [[ "$HAS_GH" == true ]]; then
        echo "📦 Creating a new GitHub repository using GitHub CLI..."
        read -p "Enter repository name: " repo_name
        read -p "Enter repository description (optional): " repo_description
        read -p "Make repository private? (y/n): " make_private
        
        private_flag=""
        if [[ $make_private == "y" ]]; then
            private_flag="--private"
        else
            private_flag="--public"
        fi
        
        gh repo create $repo_name --description "$repo_description" $private_flag --source=. --remote=origin --push
        
        if [ $? -eq 0 ]; then
            echo "✅ Repository created and code pushed successfully!"
        else
            echo "❌ Failed to create repository. Please try manual setup."
        fi
    else
        echo "📦 Setting up remote repository manually..."
        echo "1. Go to https://github.com/new"
        echo "2. Create a new repository"
        echo "3. Copy the repository URL"
        read -p "Enter the repository URL: " repo_url
        
        git remote add origin $repo_url
        echo "✅ Remote 'origin' added: $repo_url"
    fi
fi

# If we didn't use gh cli to push already
if [[ "$HAS_GH" != true || $? -ne 0 ]]; then
    echo "📝 Preparing to commit and push code..."
    
    # Add all files
    git add .
    
    # Commit
    read -p "Enter commit message [Initial commit]: " commit_message
    commit_message=${commit_message:-"Initial commit"}
    
    git commit -m "$commit_message"
    
    # Set up the main branch if needed
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
        read -p "Current branch is '$current_branch'. Do you want to rename it to 'main'? (y/n): " rename_branch
        if [[ $rename_branch == "y" ]]; then
            git branch -M main
            echo "✅ Branch renamed to 'main'"
        fi
    fi
    
    # Push to remote
    echo "🚀 Pushing code to remote repository..."
    git push -u origin HEAD
    
    if [ $? -eq 0 ]; then
        echo "✅ Code pushed successfully!"
    else
        echo "❌ Failed to push code. Please check your remote repository configuration."
    fi
fi

echo ""
echo "✨ GitHub setup complete! ✨"
echo "Your code is now on GitHub. You can view it at the repository URL." 