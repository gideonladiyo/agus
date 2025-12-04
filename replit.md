# Discord Bot - Punishing Gray Raven Helper

## Overview
This is a Discord bot that provides information about Punishing Gray Raven (PGR) game content, specifically:
- PPC (Player vs Player Combat) boss information and scoring
- Warzone stage information
- Boss statistics and predictions

## Project Structure
- `bot.py` - Main bot entry point with Discord commands
- `config.py` - Base configuration (API URLs)
- `models.py` - Data models for PPC and Warzone
- `services/` - Service layer for API calls and data processing
  - `api_service.py` - External API integration
  - `ppc_service.py` - PPC boss and scoring logic
  - `warzone_service.py` - Warzone information service
- `utils.py` - Utility functions for images, embeds, and server mapping

## Technologies
- Python 3.11
- discord.py - Discord bot framework
- aiohttp - Async HTTP requests
- Pillow - Image processing
- pandas - Data analysis for scoring calculations
- requests - HTTP library

## Setup Requirements
1. **Discord Bot Token**: Required to run the bot. Store securely in secrets.
2. **Dependencies**: Automatically installed via requirements.txt

## Discord Commands
- `!help` - Display all available commands
- `!ppc (server) (type)` - Show current PPC bosses
- `!wz (server)` - Show warzone stages
- `!ultiscore (difficulty) (time)` - Calculate PPC Ultimate score
- `!ultitotalscore (knight) (chaos) (hell)` - Calculate total Ultimate score
- `!advscore (difficulty) (time)` - Calculate PPC Advanced score
- `!advtotalscore (knight) (chaos) (hell)` - Calculate total Advanced score
- `!ppcboss (bossname)` - Get boss statistics
- `!ppcbosslist` - List all boss names

## Server Support
The bot supports multiple game servers:
- Asia (ap)
- Korea (kr)
- China (cn)
- Japan (jp)

## Recent Changes
- **2025-11-28**: Initial Replit setup
  - Installed Python 3.11 and dependencies
  - Configured Discord Bot workflow
  - Created .env.example template
  - Set up secure token management with secrets

## Running the Project
The bot runs automatically via the "Discord Bot" workflow. It will start when the workspace opens and restart on crashes.

## External Dependencies
- API: https://api.huaxu.app/ - Game data API
- Google Sheets: Score calculation data
- Image Assets: https://assets.huaxu.app/ - Boss icons and images
