This directory contains configuration files for Gemini.

- `settings.local.json`: This file defines the permissions for the Gemini agent, specifying which shell commands and web domains it is allowed or denied access to. This is used to control the agent's capabilities and ensure it operates within a safe and secure environment.

- `commands/`: This directory contains custom commands and prompts that can be used to extend the functionality of the Gemini agent. Each file in this directory corresponds to a specific persona or role, such as `analyst.md`, `architect.md`, or `dev.md`. These files contain instructions and examples that guide the agent in performing tasks related to that role.
