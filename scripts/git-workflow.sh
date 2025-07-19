#!/bin/bash

# AI Language Learning Platform - Git Workflow Helper
# For non-developers using BMAD method and agentic coding

echo "🤖 AI Language Learning Platform - Git Workflow Helper"
echo "=================================================="

# Function to show current status
show_status() {
    echo "📊 Current Git Status:"
    echo "Branch: $(git branch --show-current)"
    echo "Status:"
    git status --short
    echo ""
}

# Function to create a feature branch
create_feature() {
    echo "🔧 Creating feature branch..."
    echo "💡 Tip: Use hyphens instead of spaces (e.g., 'add-ai-chat' or 'sales-dashboard')"
    read -p "Enter feature name: " feature_name
    if [ -n "$feature_name" ]; then
        # Replace spaces with hyphens and remove special characters
        clean_name=$(echo "$feature_name" | tr ' ' '-' | tr -cd 'a-zA-Z0-9\-')
        git checkout -b feature/$clean_name
        echo "✅ Created and switched to feature/$clean_name"
    else
        echo "❌ No feature name provided"
    fi
}

# Function to save progress
save_progress() {
    echo "💾 Saving your progress..."
    read -p "Enter commit message (describe what you changed): " commit_msg
    if [ -n "$commit_msg" ]; then
        git add .
        git commit -m "$commit_msg"
        echo "✅ Progress saved!"
    else
        echo "❌ No commit message provided"
    fi
}

# Function to push to GitHub
push_to_github() {
    echo "🚀 Pushing to GitHub..."
    current_branch=$(git branch --show-current)
    git push origin $current_branch
    echo "✅ Pushed to GitHub!"
}

# Function to switch branches
switch_branch() {
    echo "🔄 Available branches:"
    git branch -a
    echo ""
    read -p "Enter branch name to switch to: " branch_name
    if [ -n "$branch_name" ]; then
        git checkout $branch_name
        echo "✅ Switched to $branch_name"
    else
        echo "❌ No branch name provided"
    fi
}

# Function to merge feature to develop
merge_feature() {
    echo "🔀 Merging feature to develop..."
    current_branch=$(git branch --show-current)
    if [[ $current_branch == feature/* ]]; then
        git checkout develop
        git merge $current_branch
        echo "✅ Merged $current_branch to develop"
        echo "💡 You can now delete the feature branch if needed"
    else
        echo "❌ You're not on a feature branch"
    fi
}

# Main menu
while true; do
    echo ""
    echo "🎯 What would you like to do?"
    echo "1. 📊 Show current status"
    echo "2. 🔧 Create new feature branch"
    echo "3. 💾 Save progress (commit)"
    echo "4. 🚀 Push to GitHub"
    echo "5. 🔄 Switch branches"
    echo "6. 🔀 Merge feature to develop"
    echo "7. 🏠 Go back to main branch"
    echo "8. 📚 Show help"
    echo "9. 🚪 Exit"
    echo ""
    read -p "Enter your choice (1-9): " choice

    case $choice in
        1)
            show_status
            ;;
        2)
            create_feature
            ;;
        3)
            save_progress
            ;;
        4)
            push_to_github
            ;;
        5)
            switch_branch
            ;;
        6)
            merge_feature
            ;;
        7)
            git checkout main
            echo "✅ Switched to main branch"
            ;;
        8)
            echo ""
            echo "📚 Git Workflow Help:"
            echo "===================="
            echo "• Always work on feature branches, never on main"
            echo "• Save progress frequently with meaningful messages"
            echo "• Push to GitHub regularly for backup"
            echo "• Merge features to develop when complete"
            echo "• Only merge develop to main when ready for production"
            echo ""
            ;;
        9)
            echo "👋 Goodbye! Your work is safe on GitHub."
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1-9."
            ;;
    esac
done 