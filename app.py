from flask import Flask, request, jsonify, render_template_string
import requests
import re
import random

app = Flask(__name__)

# ==========================================
# 👇 APNI COOKIES YAHAN RAKHEIN 👇
# ==========================================
TERABOX_COOKIE_STRING = "ndus=YyPBtdPpeHuioBOotn8hQ5w5Fcp9crqvIgSHW7Ff,ndus=YVO1tdPpeHuiN1HVLQO2LnqhUPmEHx31cVFEnxWn,ndus=Y4LigdPpeHui9AKsyWNL2kMYNdetK21Gn4FhVtZG,ndus=YdQ_gdPpeHuiXw3lGYMzhpdy-L6POF9LLJBO2g73,ndus=YTingdPpeHui4OFlXqmaqITT0jZy2fQDDvnzWhHW,ndus=YQjXEdPpeHuiHz90KEylZx5-isZY8hVt_p38M2rz"

TERABOX_COOKIES_LIST = []
for c in TERABOX_COOKIE_STRING.split(','):
    c_clean = c.strip()
    if c_clean:
        if 'ndus=' not in c_clean: 
             c_clean = 'ndus=' + c_clean
        if not c_clean.endswith(';'): 
            c_clean += ';'
        TERABOX_COOKIES_LIST.append(c_clean)

def extract_surl(url):
    match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if match:
        surl = match.group(1)
        if surl.startswith('1'):
            surl = surl[1:]
        return surl
    return None

# ==========================================
# FRONTEND UI (Same UI code)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeraBox Bypass Pro Streamer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; font-family: 'Segoe UI', sans-serif; min-height: 100vh; }
        .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 1.5rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); }
        .loader { border: 4px solid rgba(255,255,255,0.05); border-top: 4px solid #3b82f6; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #playerArea { transition: max-height 0.4s ease-out; max-height: 0; overflow: hidden; }
        #playerArea.show { max-height: 500px; }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="glass-card w-full max-w-lg p-8">
        <div class="text-center mb-8 flex flex-col items-center">
             <i class="fa-solid fa-cloud-arrow-down text-5xl text-blue-500 mb-3"></i>
            <h1 class="text-3xl font-bold mb-2">TeraBox Pro Streamer</h1>
            <p class="text-gray-400 text-sm">Paste any TeraBox link to get direct in-app stream/download link.</p>
        </div>
        <div class="space-y-4">
            <div><input type="text" id="teraUrl" placeholder="Paste link here..." class="w-full p-4 rounded-xl bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition"></div>
            <button onclick="getDirectLink()" id="btnSubmit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition duration-300 flex justify-center items-center gap-2">
                <span>Extract Link</span><div class="loader" id="spinner"></div>
            </button>
        </div>
        <div id="resultBox" class="mt-8 hidden space-y-4">
            <div id="errorMsg" class="hidden bg-red-500 text-white p-4 rounded-xl text-sm mb-4"></div>
            <div id="successBox" class="hidden space-y-4">
                <div class="bg-gray-900 p-4 rounded-xl border border-gray-700">
                    <p class="text-xs text-gray-400 mb-1">File Name:</p>
                    <p id="fileName" class="text-sm font-semibold truncate text-blue-300"></p>
                </div>
                <div id="playerArea" class="border-2 border-dashed border-gray-700 rounded-xl p-1 bg-black hidden">
                    <video id="videoPlayer" class="w-full h-auto rounded-lg" controls preload="metadata" playsinline>
                        <source src="" type="video/mp4">
                    </video>
                </div>
                <div class="flex flex-col sm:flex-row gap-2">
                    <button onclick="togglePlayer()" id="playInAppBtn" class="flex-1 bg-green-600 hover:bg-green-700 text-center py-2.5 rounded-lg font-bold transition flex justify-center items-center gap-2">
                        <i id="playIcon" class="fa-solid fa-film"></i><span id="playText">Watch Here</span>
                    </button>
                    <a id="downloadBtn" href="#" target="_blank" class="flex-1 bg-gray-600 hover:bg-gray-700 text-center py-2.5 rounded-lg font-bold transition flex justify-center items-center gap-2">
                        <i class="fa-solid fa-download"></i> Download
                    </a>
                </div>
            </div>
        </div>
    </div>
    <script>
        let currentDirectLink = "";
        async function getDirectLink() {
            const urlInput = document.getElementById('teraUrl').value;
            const btn = document.getElementById('btnSubmit');
            const spinner = document.getElementById('spinner');
            const resultBox = document.getElementById('resultBox');
            const errorMsg = document.getElementById('errorMsg');
            const successBox = document.getElementById('successBox');
            if(!urlInput) { alert("Please enter a TeraBox link!"); return; }
            spinner.style.display = 'block'; btn.disabled = true;
            resultBox.classList.remove('hidden'); errorMsg.classList.add('hidden'); successBox.classList.add('hidden');
            currentDirectLink = ""; document.getElementById('videoPlayer').pause(); document.getElementById('playerArea').classList.add('hidden'); document.getElementById('playText').innerText = "Watch Here";
            
            try {
                const response = await fetch(`/api/play?url=${encodeURIComponent(urlInput)}`);
                const data = await response.json();
                if(response.ok && data.status === 'success') {
                    document.getElementById('fileName').innerText = data.filename;
                    document.getElementById('downloadBtn').href = data.direct_play_link;
                    currentDirectLink = data.direct_play_link; 
                    successBox.classList.remove('hidden');
                } else {
                    errorMsg.innerText = data.error || "Failed to extract link.";
                    errorMsg.classList.remove('hidden');
                }
            } catch (err) {
                errorMsg.innerText = "Server Error! Please try again later.";
                errorMsg.classList.remove('hidden');
            } finally {
                spinner.style.display = 'none'; btn.disabled = false;
            }
        }
        function togglePlayer() {
            const playerArea = document.getElementById('playerArea');
            const videoPlayer = document.getElementById('videoPlayer');
            const playText = document.getElementById('playText');
            if(!currentDirectLink) { alert("Extracted link is missing! Try again."); return; }
            if(playerArea.classList.contains('hidden')) {
                playText.innerText = "Loading..."; videoPlayer.src = currentDirectLink; videoPlayer.load();
                videoPlayer.play().then(() => {
                     playerArea.classList.remove('hidden'); playText.innerText = "Hide Player";
                     setTimeout(() => playerArea.scrollIntoView({ behavior: 'smooth' }), 300);
                }).catch(error => {
                    console.error("Playback failed:", error); playText.innerText = "Playback Blocked";
                    setTimeout(() => playText.innerText = "Watch Here", 2000);
                    alert("Stream blocked by TeraBox. Please click 'Download' to view.");
                });
            } else {
                videoPlayer.pause(); videoPlayer.src = ""; playerArea.classList.add('hidden'); playText.innerText = "Watch Here";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/play', methods=['GET'])
def get_stream_link():
    tera_url = request.args.get('url')
    if not tera_url:
        return jsonify({"error": "URL parameter missing."}), 400

    surl = extract_surl(tera_url)
    if not surl:
        return jsonify({"error": "Invalid TeraBox Link format."}), 400

    if not TERABOX_COOKIES_LIST:
        return jsonify({"error": "No cookies configured."}), 500

    chosen_cookie = random.choice(TERABOX_COOKIES_LIST)

    # 🔥 YAHAN MAIN MAGIC HAI - MOBILE HEADERS 🔥
    # Hum TeraBox ko bata rahe hain ki ye request ek mobile app se aayi hai, PC se nahi.
    headers = {
        'User-Agent': 'dubox;4.15.10;moto+g62+5G;android-android;13;JSbridge1.0.10;jointbridge;1.1.39;',
        'Cookie': chosen_cookie,
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    # app_id 250528 (Dubox mobile app ID) ensures premium link response
    api_url = f"https://www.terabox.com/share/list?app_id=250528&shorturl={surl}&root=1"
    
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data.get('errno') == 0:
            file_info = data['list'][0]
            dlink = file_info.get('dlink')
            filename = file_info.get('server_filename')
            
            # Agar TeraBox ne phir bhi link chupa li (dlink null hai)
            if not dlink:
                return jsonify({
                    "error": f"TeraBox ne file ('{filename}') dhund li, par direct link block kar di hai. Ho sakta hai aapki cookies purani ho gayi hain ya premium file hai.",
                    "details": data
                }), 403

            return jsonify({
                "status": "success",
                "filename": filename,
                "direct_play_link": dlink
            })
        else:
            return jsonify({
                "error": "Link invalid hai ya cookies expire ho chuki hain.",
                "details": data
            }), 403
            
    except Exception as e:
        return jsonify({"error": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
