<p align="center">
      <img src="https://git.zabbix.com/projects/ZBX/repos/zabbix/browse/templates/media/discord/images/logo.png?raw=true">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/follow-nghtcode-white?style=for-the-badge" alt="follow me">
  <img src="https://img.shields.io/badge/discord-bot-blue?style=for-the-badge" alt="discord">
  <img src="https://img.shields.io/badge/requires-setup-crimson?style=for-the-badge" alt="python_version">
</p>

> [!TIP]
> **The [en.json](https://github.com/nghtcode/autoroomer-bot/blob/main/locales/en.json) file allows for customizable text configuration to suit your preferences. To support a language other than English, you must create a separate JSON file and provide a complete translation of the content from `en.json`.**

## Overview

This bot is designed to automate the management of voice channels on a Discord server. It provides functionality for creating rooms, sending messages to recruit participants, and managing both rooms and messages. The bot is ideal for servers hosting gaming sessions, meetings, or other events requiring dynamic room creation and management.

## Features

### 1. **Room Creation:**
+ Automatically creates voice channels on the server;
+ Supports organizing rooms into categories for better structure.
### 2. **Participant Recruitment Messages:**
+ Publishes messages in designated text channels with details about the created room (e.g., name, purpose, number of participants);
+ Supports customizable message text via the `en.json` file (or other JSON files for localization).
### 3. **Room and Message Management:**
+ Automatically removes empty rooms;
+ Updates or deletes recruitment messages when a room's status changes.

## Setup
+ **`Configuration:`** The bot requires a configured [.env](https://github.com/nghtcode/autoroomer-bot/blob/main/.env) file specifying the Discord token and other parameters (e.g., channel IDs).
+ **`Localization:`** Message text is customizable via the [en.json](https://github.com/nghtcode/autoroomer-bot/blob/main/locales/en.json) file. To support other languages, create a corresponding JSON file with translations.
+ **`Permissions:`** The bot requires permissions to manage channels, send messages and manage messages.