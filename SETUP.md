# Local Workspace MCP setup

Workspace MCP **1.26.0** is installed with `uv tool install` from the inspected upstream checkout. `workspace-mcp` and `workspace-cli` are on PATH. The installation uses the package's declared dependency ranges; MCP startup, tool discovery and live Drive reads were verified with the resolved dependencies.

The server is registered as **`workspace-google`** in the current Codex account, the standard Codex home, Claude Code's user configuration and Claude Desktop. New agent sessions or a client restart are needed to load that registration. It exposes **99 tools**: complete tiers for Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks and Contacts.

Both configured Google accounts have their identities verified using Drive's account endpoint. Existing Docs/Drive OAuth grants were copied into Workspace's native owner-only credential store. Live Drive searches through the actual stdio MCP server succeeded for each account; returned file contents and names were not saved in this repository.

## Authorization status

Docs/Drive are working. The remaining services require broader Google OAuth consent; `gcloud` infrastructure credentials alone do not grant Gmail or Calendar access. The existing OAuth client's Cloud project already has the relevant APIs enabled, so no Cloud project or API enablement changes were needed.

At setup time, the personal account's consent flow displayed Google's unverified-app warning for the user's own OAuth client, and the work account needed browser sign-in. Those steps remain for the user. The OAuth client is displayed by Google as `everything-app`; it is the existing client also used by gdoc.

The account is explicit on each call through `user_google_email`. No default account or single-user fallback was configured.

## Configuration and credentials

Client configurations contain paths, not credential values:

| Setting | Purpose |
|---|---|
| `GOOGLE_CLIENT_SECRET_PATH` | Points to the existing `~/.config/gdoc/credentials.json` OAuth client. |
| `WORKSPACE_MCP_CREDENTIALS_DIR` | Points to `~/.google_workspace_mcp/credentials`, with one native OAuth token file per account. |
| `WORKSPACE_MCP_LOG_LEVEL` | `ERROR` reduces routine server log output. |

No new API keys were obtained. Existing OAuth client files and native token caches were reused; no secrets were added to this repository. Configuration backups are under `~/.local/state/workspace-mcp/20260912T133442Z/` with owner-only permissions.

## Finish authorization

In a newly started MCP-connected agent session, call:

```text
start_google_auth(service_name="Google Workspace", user_google_email="ACCOUNT_EMAIL")
```

Open the returned Google authorization link, sign in to the named account and complete consent. Keep the agent session running until Google's callback reports success. Repeat for the other account if needed. Then verify with `list_calendars` and `search_gmail_messages`; a successful tool-registration check alone does not prove those Google scopes work.

The initial setup also opened two consent tabs and kept a temporary callback listener alive for 15 minutes. If those links expire, request fresh ones as above.

The native `workspace-cli` speaks to a running **HTTP** server; this installation configures **stdio**, which each agent client starts on demand. No permanent HTTP server or background service was installed.

[Actual tool and command comparison](COMMANDS.md) · [Codex MCP configuration documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
