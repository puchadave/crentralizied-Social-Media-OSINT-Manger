# Centralized Social Media OSINT Manager

This repository contains the **Social Media Manager** Odoo addon located in
`addons/social_media_manager`. The module provides a unified workspace for
connecting brand accounts, scheduling content, tracking metrics, and generating
AI-assisted messaging across major social networks.

## Features

- Secure storage for Facebook, Instagram, Twitter/X, LinkedIn, YouTube, and TikTok credentials
- Unified post composer with mixed-media scheduling, AI captioning, and campaign metadata
- Automated publishing and KPI synchronization via background jobs
- Dashboard with follower growth, engagement, SEO/SEA KPIs, and publishing cadence widgets
- ChatGPT-powered content wizard to suggest captions and hashtags with configurable prompts
- Python unit tests and a web tour covering content generation, API error handling, and dashboards

## Getting Started

1. Copy or symlink `addons/social_media_manager` into your Odoo `addons_path`.
2. Restart the Odoo server and update the app list.
3. Install **Social Media Manager** from the Apps menu.
4. Configure the OpenAI key in *Settings → Technical → System Parameters* using the
   key `social_media_manager.openai_api_key`.
5. Add your social accounts and schedule posts from the new Social Media Manager menu.

Refer to `addons/social_media_manager/docs/index.rst` for additional setup tips,
automation details, and dashboard usage instructions.
