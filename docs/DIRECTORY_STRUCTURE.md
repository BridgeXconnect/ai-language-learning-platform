# Directory Structure Guide

## Root Level
- `client/` - Next.js frontend application
- `server/` - Python FastAPI backend application
- `packages/` - Shared utilities and types
- `agents/` - AI agent implementations
- `docs/` - Project documentation
- `scripts/` - Project-wide scripts and utilities
- `config/` - Configuration files
- `logs/` - Application and test logs
- `temp/` - Temporary files and debug artifacts

## Documentation Organization
- `docs/progress-reports/` - Development progress reports and summaries
- `docs/archived/` - Archived documentation
- `docs/prd/` - Product requirements documentation
- `docs/architecture/` - System architecture documentation

## Configuration Organization
- `config/docker/` - Docker configuration files
- `config/testing/` - Testing configuration files
- `config/environments/` - Environment-specific configurations

## Scripts Organization
- `scripts/deployment/` - Deployment and environment setup scripts
- `scripts/legacy/` - Legacy organization and cleanup scripts
- `scripts/` - Current project scripts

## Logs Organization
- `logs/` - All application logs, test outputs, and debugging information

## Temporary Files
- `temp/` - Debug files, test artifacts, and temporary development files

## Guidelines for New Files
1. **Documentation**: Place in appropriate `docs/` subdirectory
2. **Configuration**: Place in appropriate `config/` subdirectory
3. **Scripts**: Place in appropriate `scripts/` subdirectory
4. **Logs**: Place in `logs/` directory
5. **Temporary files**: Place in `temp/` directory
6. **Never leave files at root level** unless they are essential project files (README, .gitignore, etc.)
