from flask import Flask, request, jsonify, render_template_string
import requests
import re
import random

app = Flask(__name__)

# ==========================================
# APNI COOKIES YAHAN RAKHEIN
# ==========================================
TERABOX_COOKIE_STRING = "ndus=YyPBtdPpeHuioBOotn8hQ5w5Fcp9crqvIgSHW7Ff,ndus=YVO1tdPpeHuiN1HVLQO2LnqhUPmEHx31cVFEnxWn,ndus=Y4LigdPpeHui9AKsyWNL2kMYNdetK21Gn4FhVtZG,ndus=YdQ_gdPpeHuiXw3lGYMzhpdy-L6POF9LLJBO2g73,ndus=YTingdPpeHui4OFlXqmaqITT0jZy2fQDDvnzWhHW,ndus=YQjXEdPpeHuiHz90KEylZx5-isZY8hVt_p38M2rz"

TERABOX_COOKIES_LIST = [c.strip() for c in TERABOX_COOKIE_STRING.split(',') if c.strip()]

def extract_surl(url):
    match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if match:
        surl = match.group(1)
        return surl[1:] if surl.startswith('1') else surl
    return None

# UI Content (Wahi same premium dark theme)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeraBox Pro Streamer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; min-height: 100vh; font-family: sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1); }
        .loader { border: 3px solid #f3f3f3; border-top: 3px solid #3b82f6; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="glass w-full max-w-md p-8 shadow-2xl">
        <div class="text-center mb-6">
            <i class="fa-solid fa-bolt text-4xl text-yellow-400 mb-2"></i>
            <h1 class="text-2xl font-bold">TeraBox Fast Bypass</h1>
        </div>
        <input type="text" id="url" placeholder="Paste TeraBox Link" class="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 mb-4 focus:outline-none focus:border-blue-500">
        <button onclick="getLink()" id="btn" class="w-full bg-blue-600 p-3 rounded-lg font-bold flex justify-center items-center gap-2">
            <span>Extract Link</span> <div class="loader" id="ld"></div>
        </button>
        <div id="res" class="mt-6 hidden space-y-4">
            <div class="bg-black/40 p-3 rounded text-sm border border-gray-700">
                <p class="text-gray-400 text-xs">File Name:</p>
                <p id="fn" class="truncate font-medium"></p>
            </div>
            <div id="player" class="hidden"><video id="vid" controls class="w-full rounded-lg shadow-lg bg-black"></video></div>
            <div class="flex gap-2">
                <button onclick="playVid()" class="flex-1 bg-green-600 p-2 rounded font-bold text-sm"><i class="fa-solid fa-play"></i> Watch</button>
                <a id="dl" href="#" target="_blank" class="flex-1 bg-gray-700 p-2 rounded font-bold text-sm text-center"><i class="fa-solid fa-download"></i> Download</a>
            </div>
        </div>
    </div>
    <script>
        let dlink = "";
        async function getLink() {
            const url = document.getElementById('url').value;
            const btn = document.getElementById('btn');
            const ld = document.getElementById('ld');
            if(!url) return alert("Link daalein!");
            ld.style.display = "block"; btn.disabled = true;
            try {
                const r = await fetch(`/api/play?url=${encodeURIComponent(url)}`);
                const d = await r.json();
                if(d.status === 'success') {
                    document.getElementById('fn').innerText = d.filename;
                    dlink = d.direct_play_link;
                    document.getElementById('dl').href = dlink;
                    document.getElementById('res').classList.remove('hidden');
                } else { alert(d.error); }
            } catch(e) { alert("Server error!"); }
            finally { ld.style.display = "none"; btn.disabled = false; }
        }
        function playVid() {
            const v = document.getElementById('vid');
            document.getElementById('player').classList.remove('hidden');
            v.src = dlink; v.play();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/play')
def api():
    url = request.args.get('url')
    surl = extract_surl(url)
    if not surl: return jsonify({"error": "Invalid URL"}), 400
    
    cookie = random.choice(TERABOX_COOKIES_LIST)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie
    }

    # Step 1: Get File Details (uk & fs_id)
    info_url = f"https://www.terabox.com/share/list?app_id=250528&shorturl={surl}&root=1"
    try:
        res = requests.get(info_url, headers=headers).json()
        if res.get('errno') != 0: return jsonify({"error": "Cookie Expired"}), 403
        
        file_data = res['list'][0]
        uk = res.get('uk')
        fs_id = file_data.get('fs_id')
        filename = file_data.get('server_filename')
        
        # Step 2: Hit Direct Download API using fs_id
        # Yeh bypass endpoint mobile app ka hai jo dlink force karta hai
        dlink_url = f"https://www.terabox.com/share/download?app_id=250528&shorturl={surl}&fs_id={fs_id}"
        dlink_res = requests.get(dlink_url, headers=headers).json()
        
        # Final direct link extraction
        dlink = dlink_res.get('dlink') or file_data.get('dlink')
        
        if not dlink:
            return jsonify({"error": "Link block ho rahi hai, try another cookie"}), 403

        return jsonify({
            "status": "success",
            "filename": filename,
            "direct_play_link": dlink
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
