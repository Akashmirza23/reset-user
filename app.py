from flask import Flask, render_template_string, request, flash
import requests

app = Flask(__name__)
app.secret_key = "secure_reset_key"

# --- MIKROTIK SETTINGS ---
ROUTER_IP = "YOUR_ROUTER_PUBLIC_IP"
AUTH = ("api_user", "your_password")
BASE_URL = f"https://{ROUTER_IP}/rest"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Hotspot Self-Reset</title></head>
<body>
    <h2>Reset Your Hotspot Session</h2>
    <form method="POST">
        <input type="text" name="user" placeholder="Username" required><br><br>
        <button type="submit">Reset and Clear Cookies</button>
    </form>
    {% with msgs = get_flashed_messages() %}{% for m in msgs %}<p>{{m}}</p>{% endfor %}{% endwith %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        user = request.form.get('user')
        try:
            # 1. Reset MAC Address Lock
            requests.patch(f"{BASE_URL}/ip/hotspot/user/{user}", json={"mac-address": ""}, auth=AUTH, verify=False)
            
            # 2. Remove Active Session (Disconnect User)
            active = requests.get(f"{BASE_URL}/ip/hotspot/active?user={user}", auth=AUTH, verify=False).json()
            for session in active:
                requests.delete(f"{BASE_URL}/ip/hotspot/active/{session['.id']}", auth=AUTH, verify=False)

            # 3. Remove MAC Cookies (Prevent Auto-Login)
            cookies = requests.get(f"{BASE_URL}/ip/hotspot/cookie?user={user}", auth=AUTH, verify=False).json()
            for c in cookies:
                requests.delete(f"{BASE_URL}/ip/hotspot/cookie/{c['.id']}", auth=AUTH, verify=False)
                
            flash(f"User {user} has been fully reset. Try logging in again.")
        except Exception as e:
            flash(f"Connection Error: {str(e)}")
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
