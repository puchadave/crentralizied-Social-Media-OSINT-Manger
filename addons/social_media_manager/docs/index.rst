Social Media Manager
====================

The Social Media Manager module centralizes campaign planning, automated publishing,
and KPI monitoring across major social networks.

.. contents:: Table of Contents
   :depth: 2

Setup
-----

* Install the module and ensure the ``social`` and ``marketing_automation`` apps are active.
* Configure API credentials on each social media account form and set the
  ``social_media_manager.openai_api_key`` system parameter with your OpenAI key.
* Assign users to the *Social Media Manager* security group to access the module.

Automation
----------

Two scheduled actions are provided out of the box:

* **Publish Scheduled Social Posts** executes every 15 minutes to publish ready posts.
* **Synchronize Social Media Metrics** runs every two hours to pull KPI updates.

Dashboard
---------

The dashboard aggregates followers, engagement, impressions, and campaign performance
with interactive charts, graphs, and calendars. Filters are available per channel and
time range.

AI Content Generation
---------------------

Create reusable prompt templates and generate drafts with OpenAI ChatGPT. Use the
"Generate Content" button on any post to open the wizard and refine prompts, captions,
and hashtags before scheduling.
