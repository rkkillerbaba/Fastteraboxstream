from flask import Flask, request, jsonify, render_template_string
import requests
import re
import random

app = Flask(__name__)

# ==========================================
# 👇 EK BAAR NEW COOKIE CHECK KARLO 👇
# Agar fir bhi error aaye, toh browser mein TeraBox login karke 
# naya 'ndus' nikaal kar yahan refresh kar dena.
# ==========================================
TERABOX_COOKIES = [
    "ndus=YyPBtdPpeHuioBOotn8hQ5w5Fcp9crqvIgSHW7Ff;",
    "ndus=YVO1tdPpeHuiN1HVLQO2LnqhUPmEHx31cVFEnxWn;",
    "ndus=Y4LigdPpeHui9AKsyWNL2kMYNdetK21Gn4FhVtZG;",
    "ndus=YdQ_gdPpeHuiXw3lGYMzhpdy-L6POF9LLJBO2g73;",
    "ndus=YTingdPpeHui4OFlXqmaqITT0jZy2fQDDvnzWhHW;",
    "ndus=YQjXEdPpeHuiHz90KEylZx5-isZY8hVt_p38M2rz;"
]

def get_surl(url):
    match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if match:
        s = match.group(1)
        return s[1:] if s.startswith('1') else s
    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeraBox Ultra Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #0b0f19; color: white; font-family: sans-serif; }
        .card { background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; }
        .loader { border: 3px solid transparent; border-top: 3px solid #3b82f6; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; display: none; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="card w-full max-w-md p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-center mb-6 text-blue-400">TeraBox Pro Bypass</h1>
        <input type="text" id="url" placeholder="Paste link here..." class="w-full p-4 rounded-xl bg-gray-900 border border-gray-700 mb-4 focus:ring-2 focus:ring-blue-500 outline-none">
        <button onclick="fetchLink()" id="btn" class="w-full bg-blue-600 p-4 rounded-xl font-bold flex justify-center items-center gap-3 hover:bg-blue-700 transition">
            <span>Extract & Play</span> <div class="loader" id="ld"></div>
        </button>
        <div id="res" class="mt-8 hidden animate-fade-in">
            <div class="bg-blue-900/20 p-4 rounded-xl border border-blue-500/30 mb-4">
                <p class="text-xs text-blue-400 uppercase tracking-wider font-bold mb-1">File Found</p>
                <p id="fn" class="text-sm truncate font-medium"></p>
            </div>
            <video id="v" controls class="w-full rounded-xl bg-black shadow-lg mb-4 hidden"></video>
            <div class="flex gap-3">
                <button onclick="playVideo()" class="flex-1 bg-green-600 p-3 rounded-xl font-bold text-sm shadow-lg shadow-green-900/20">Watch</button>
                <a id="dl" href="#" target="_blank" class="flex-1 bg-gray-700 p-3 rounded-xl font-bold text-sm text-center">Download</a>
            </div>
        </div>
    </div>
    <script>
        let dlink = "";
        async function fetchLink() {
            const u = document.getElementById('url').value;
            const b = document.getElementById('btn');
            const l = document.getElementById('ld');
            if(!u) return alert("Link kahan hai?");
            l.style.display = "block"; b.disabled = true;
            try {
                const res = await fetch(`/api/stream?url=${encodeURIComponent(u)}`);
                const data = await res.json();
                if(data.status === 'success') {
                    dlink = data.link;
                    document.getElementById('fn').innerText = data.name;
                    document.getElementById('dl').href = dlink;
                    document.getElementById('res').classList.remove('hidden');
                } else { alert("Error: " + data.message); }
            } catch(e) { alert("Server Down!"); }
            finally { l.style.display = "none"; b.disabled = false; }
        }
        function playVideo() {
            const vid = document.getElementById('v');
            vid.classList.remove('hidden');
            vid.src = dlink; vid.play();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/stream')
def stream():
    url = request.args.get('url')
    surl = get_surl(url)
    if not surl: return jsonify({"status": "error", "message": "Invalid URL"}), 400

    # User-Agent ko Browser jaisa hi rakho, Mobile headers avoid karo for now
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.terabox.com/'
    }

    # Sabhi cookies try karega jab tak ek kaam na kar jaye
    random.shuffle(TERABOX_COOKIES)
    
    for cookie in TERABOX_COOKIES:
        headers['Cookie'] = cookie
        try:
            # Step 1: Link details
            api = f"https://www.terabox.com/share/list?app_id=250528&shorturl={surl}&root=1"
            r = requests.get(api, headers=headers, timeout=10).json()
            
            if r.get('errno') == 0:
                item = r['list'][0]
                # Direct Link check
                dlink = item.get('dlink')
                
                # Step 2: Agar dlink nahi hai, toh force fetch download link
                if not dlink:
                    dl_api = f"https://www.terabox.com/share/download?app_id=250528&shorturl={surl}&fs_id={item['fs_id']}"
                    dl_res = requests.get(dl_api, headers=headers, timeout=10).json()
                    dlink = dl_res.get('dlink')

                if dlink:
                    return jsonify({
                        "status": "success",
                        "name": item['server_filename'],
                        "link": dlink
                    })
        except:
            continue

    return jsonify({"status": "error", "message": "Sabhi cookies expire ho chuki hain! Nayi ndus cookie daalein."}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
