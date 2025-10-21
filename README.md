# Social Media OSINT Manager for Odoo

This repository provides an Odoo addon that combines social media scheduling, AI-assisted content generation, newsletter automation, and OSINT analytics in a single workspace. The solution is inspired by dedicated social suites such as Postiz and extends them with GPT-powered content authoring and visual dashboards.

## Key capabilities

- **Account management** – Configure social handles, tokens, and team permissions while tracking followers, engagement, and scheduling activity.
- **AI-assisted publishing** – Use integrated ChatGPT prompts to draft posts, captions, and newsletters directly from the record forms or via dedicated wizards.
- **Campaign analytics** – Capture OSINT snapshots for posts and accounts, including reach, engagement, sentiment, topic clusters, location heatmaps, and mention graphs.
- **Operational dashboards** – Review consolidated KPIs and per-post performance from a responsive backend dashboard without leaving Odoo.
- **Newsletter automation** – Transform high performing posts into email newsletters using the mass mailing application, ready for review or immediate distribution.

Install the module in an Odoo environment (16.0+) with the Marketing apps enabled (`mail`, `mass_mailing`, `utm`, `board`) and configure the OpenAI API key from the Social Intelligence → AI Settings menu.
