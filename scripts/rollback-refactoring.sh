#!/bin/bash

# Rollback Refactoring
# Safely rollback refactoring changes if something goes wrong

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_BASE="$PROJECT_ROOT/refactoring-backups"

echo "🔄 Refactoring Rollback Utility"
echo "=============================="

show_help() {
    echo ""
    echo "Usage: $0 [phase|all|list]"
    echo ""
    echo "Commands:"
    echo "  phase1    - Rollback environment consolidation"
    echo "  phase2    - Rollback backend reorganization" 
    echo "  phase3    - Rollback naming standardization"
    echo "  all       - Rollback all phases (dangerous!)"
    echo "  list      - List available backups"
    echo "  help      - Show this help"
    echo ""
}

list_backups() {
    echo "📁 Available backups:"
    if [ -d "$BACKUP_BASE" ]; then
        find "$BACKUP_BASE" -maxdepth 1 -type d -name "phase*" | sort
    else
        echo "  No backups found"
    fi
}

rollback_phase() {
    local phase="$1"
    local backup_dir
    
    # Find the most recent backup for this phase
    backup_dir=$(find "$BACKUP_BASE" -maxdepth 1 -type d -name "${phase}-*" | sort -r | head -n 1)
    
    if [ -z "$backup_dir" ]; then
        echo "❌ No backup found for $phase"
        return 1
    fi
    
    echo "📁 Rolling back from: $backup_dir"
    
    # Confirm with user
    read -p "⚠️  This will overwrite current files. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Rollback cancelled"
        return 1
    fi
    
    # Perform rollback based on phase
    case "$phase" in
        "phase1")
            echo "🔄 Rolling back environment consolidation..."
            # Restore environment files
            if [ -d "$backup_dir" ]; then
                find "$backup_dir" -name ".env*" -exec cp {} "$PROJECT_ROOT/" \;
                echo "  ✅ Environment files restored"
            fi
            ;;
        "phase2")
            echo "🔄 Rolling back backend reorganization..."
            # Restore server structure
            if [ -d "$backup_dir/app" ]; then
                rm -rf "$PROJECT_ROOT/server/app"
                cp -r "$backup_dir/app" "$PROJECT_ROOT/server/"
                echo "  ✅ Backend structure restored"
            fi
            ;;
        "phase3")
            echo "🔄 Rolling back naming standardization..."
            # Restore from naming fixes backup
            if [ -d "$BACKUP_BASE/naming-fixes" ]; then
                echo "  ⚠️  Manual restoration required for renamed files"
                echo "  📁 Check: $BACKUP_BASE/naming-fixes"
            fi
            ;;
        *)
            echo "❌ Unknown phase: $phase"
            return 1
            ;;
    esac
    
    echo "✅ Rollback complete for $phase"
}

rollback_all() {
    echo "⚠️  DANGER: This will rollback ALL refactoring changes"
    read -p "Are you absolutely sure? Type 'ROLLBACK' to confirm: " confirmation
    
    if [ "$confirmation" != "ROLLBACK" ]; then
        echo "Rollback cancelled"
        return 1
    fi
    
    # Rollback in reverse order
    rollback_phase "phase3"
    rollback_phase "phase2" 
    rollback_phase "phase1"
    
    echo "🔄 All phases rolled back"
}

# Main command handling
case "${1:-help}" in
    phase1|phase2|phase3)
        rollback_phase "$1"
        ;;
    all)
        rollback_all
        ;;
    list)
        list_backups
        ;;
    help|*)
        show_help
        ;;
esac
