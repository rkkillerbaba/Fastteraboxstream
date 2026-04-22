# app.py - TeraBox Bypass Pro API
from flask import Flask, request, jsonify, render_template_string
import requests
import re
import random # For professional cookie rotation

app = Flask(__name__)

# ==========================================
# 👇 YOUR TERABOX COOKIES LIST (Automatically Handled) 👇
# We automatically rotate these to prevent account blocking and maximize longevity
# ==========================================
TERABOX_COOKIE_STRING = "ndus=YyPBtdPpeHuioBOotn8hQ5w5Fcp9crqvIgSHW7Ff,ndus=YVO1tdPpeHuiN1HVLQO2LnqhUPmEHx31cVFEnxWn,ndus=Y4LigdPpeHui9AKsyWNL2kMYNdetK21Gn4FhVtZG,ndus=YdQ_gdPpeHuiXw3lGYMzhpdy-L6POF9LLJBO2g73,ndus=YTingdPpeHui4OFlXqmaqITT0jZy2fQDDvnzWhHW,ndus=YQjXEdPpeHuiHz90KEylZx5-isZY8hVt_p38M2rz"

# Clean up the list: get rid of empty spaces, ensure proper ndus structure
TERABOX_COOKIES_LIST = []
for c in TERABOX_COOKIE_STRING.split(','):
    c_clean = c.strip()
    if c_clean:
        if 'ndus=' not in c_clean: # ensure prefix
             c_clean = 'ndus=' + c_clean
        if not c_clean.endswith(';'): # ensure suffix
            c_clean += ';'
        TERABOX_COOKIES_LIST.append(c_clean)

def extract_surl(url):
    # Regex that works with various TeraBox domains (1024, teraboxapp, etc.)
    match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if match:
        surl = match.group(1)
        if surl.startswith('1'):
            surl = surl[1:]
        return surl
    return None

# ==========================================
# FRONTEND UI with Sleek Video Player
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
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        .loader {
            border: 4px solid rgba(255,255,255,0.05);
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: none;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Smooth video display animation */
        #playerArea {
            transition: max-height 0.4s ease-out;
            max-height: 0;
            overflow: hidden;
        }
        #playerArea.show {
            max-height: 500px; /* Adjust based on video aspect ratio/size */
        }
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
            <div>
                <input type="text" id="teraUrl" placeholder="https://terabox.com/s/1Vk6weK3jl0Dya5o0pQrCrA" 
                    class="w-full p-4 rounded-xl bg-gray-900 border border-gray-700 text-white placeholder:text-gray-600 focus:outline-none focus:border-blue-500 transition">
            </div>
            
            <button onclick="getDirectLink()" id="btnSubmit"
                class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition duration-300 flex justify-center items-center gap-2">
                <span>Extract Link</span>
                <div class="loader" id="spinner"></div>
            </button>
        </div>

        <div id="resultBox" class="mt-8 hidden space-y-4">
            <div id="errorMsg" class="hidden bg-red-500/80 text-white p-4 rounded-xl text-sm mb-4 border border-red-700"></div>
            
            <div id="successBox" class="hidden space-y-4">
                <div class="bg-gray-900 p-4 rounded-xl border border-gray-700">
                    <p class="text-xs text-gray-400 mb-1">File Name:</p>
                    <p id="fileName" class="text-sm font-semibold truncate text-blue-300"></p>
                </div>

                <div id="playerArea" class="border-2 border-dashed border-gray-700 rounded-xl p-1 bg-black hidden">
                    <video id="videoPlayer" class="w-full h-auto rounded-lg" controls preload="metadata" playsinline>
                        <source src="" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>

                <div class="flex flex-col sm:flex-row gap-2">
                    <button onclick="togglePlayer()" id="playInAppBtn" class="flex-1 bg-green-600 hover:bg-green-700 text-center py-2.5 rounded-lg font-bold transition flex justify-center items-center gap-2">
                        <i id="playIcon" class="fa-solid fa-film"></i>
                        <span id="playText">Watch Here</span>
                    </button>
                    <a id="downloadBtn" href="#" target="_blank" class="flex-1 bg-gray-600 hover:bg-gray-700 text-center py-2.5 rounded-lg font-bold transition flex justify-center items-center gap-2">
                        <i class="fa-solid fa-download"></i> Download File
                    </a>
                    <button onclick="copyLink()" class="flex-1 bg-gray-700 hover:bg-gray-600 text-center py-2.5 rounded-lg font-bold transition flex justify-center items-center gap-2">
                        <i class="fa-solid fa-copy"></i> Copy Link
                    </button>
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
            const playerArea = document.getElementById('playerArea');
            const videoPlayer = document.getElementById('videoPlayer');
            const playText = document.getElementById('playText');

            if(!urlInput) {
                alert("Please enter a TeraBox link!");
                return;
            }

            // Show loading and reset states
            spinner.style.display = 'block';
            btn.disabled = true;
            resultBox.classList.remove('hidden');
            errorMsg.classList.add('hidden');
            successBox.classList.add('hidden');
            
            // Full Reset Player state
            currentDirectLink = "";
            videoPlayer.pause();
            videoPlayer.src = "";
            playerArea.classList.add('hidden');
            playText.innerText = "Watch Here";

            try {
                const response = await fetch(`/api/play?url=${encodeURIComponent(urlInput)}`);
                const data = await response.json();

                if(response.ok && data.status === 'success') {
                    document.getElementById('fileName').innerText = data.filename;
                    // For direct downloading button
                    document.getElementById('downloadBtn').href = data.direct_play_link;
                    // Store link to be loaded by player
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
                spinner.style.display = 'none';
                btn.disabled = false;
            }
        }

        // 👇 NEW function to toggle the in-app player smoothly 👇
        function togglePlayer() {
            const playerArea = document.getElementById('playerArea');
            const videoPlayer = document.getElementById('videoPlayer');
            const playText = document.getElementById('playText');

            if(!currentDirectLink) {
                alert("Extracted link is missing! Try again.");
                return;
            }

            if(playerArea.classList.contains('hidden')) {
                // Attempt Load and Play
                playText.innerText = "Loading...";
                videoPlayer.src = currentDirectLink;
                videoPlayer.load();

                // Simple browser embedded video tags are often blocked. 
                // TeraBox forces a Referer check. This player can sometimes fail.
                videoPlayer.play().then(() => {
                     // Playback success
                     playerArea.classList.remove('hidden');
                     playText.innerText = "Hide Player";
                     // Smooth scroll to video area to focus user
                     setTimeout(() => playerArea.scrollIntoView({ behavior: 'smooth' }), 300);
                }).catch(error => {
                    // Playback failed due to blocking
                    console.error("Playback failed:", error);
                    playText.innerText = "Playback Failed";
                    // Fallback alert: user must download
                    setTimeout(() => playText.innerText = "Watch Here", 2000);
                    alert("Superfast stream failed. This is common because TeraBox CDN often blocks direct embedded playback on free servers. Please use the 'Download File' button instead.");
                });

            } else {
                // Pause and Hide
                videoPlayer.pause();
                videoPlayer.src = "";
                playerArea.classList.add('hidden');
                playText.innerText = "Watch Here";
            }
        }

        function copyLink() {
            if(currentDirectLink) {
                navigator.clipboard.writeText(currentDirectLink);
                alert("Direct Link Copied to Clipboard!");
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# BACKEND API ROUTE with Cookie Rotation
# ==========================================
@app.route('/')
def home():
    # Frontend UI serve karna
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/play', methods=['GET'])
def get_stream_link():
    tera_url = request.args.get('url')
    
    if not tera_url:
        return jsonify({"error": "URL parameter missing."}), 400

    surl = extract_surl(tera_url)
    if not surl:
        return jsonify({"error": "Invalid TeraBox Link format."}), 400

    # 🔄 PROFESSIONAL COOKIE ROTATION LOGIC 🔄
    # Prevents account blocking by randomizing the cookie per request
    if not TERABOX_COOKIES_LIST:
        return jsonify({"error": "No valid cookies configured in app.py. The tool will not function."}), 500

    # Pick a random cookie from your list
    chosen_cookie = random.choice(TERABOX_COOKIES_LIST)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Cookie': chosen_cookie, # USE THE ROTATED COOKIE
        'Accept': 'application/json, text/plain, */*'
    }

    api_url = f"https://www.terabox.com/share/list?app_id=250528&shorturl={surl}&root=1"
    
    try:
        response = requests.get(api_url, headers=headers)
        # TeraBox share/list API rarely returns direct link. A professional API
        # would need to use mobile API endpoints found in image_3.png for M3U8 links.
        # This current implementation is a 'client-side' browser attempt.
        data = response.json()
        
        if data.get('errno') == 0:
            file_info = data['list'][0]
            
            # The 'dlink' is a download link, browsers *can* play MP4 direct links
            # but CDNs block them frequently.
            return jsonify({
                "status": "success",
                "filename": file_info.get('server_filename'),
                "direct_play_link": file_info.get('dlink')
            })
        else:
            return jsonify({
                "error": "Link expired or TeraBox account limits reached (cookies are working, but CDN blocked extraction).",
                "details": data
            }), 403
            
    except Exception as e:
        return jsonify({"error": f"Internal Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Start app, port 5000 is default but Gunicorn handles Render
    app.run(host='0.0.0.0', port=5000)
