from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# ==========================================
# 👇 YAHAN APNI TERABOX KI 'ndus' COOKIE DAALEIN 👇
# ==========================================
TERABOX_COOKIE = "ndus=YQjXEdPpeHuiHz90KEylZx5-isZY8hVt_p38M2rz" 

def extract_surl(url):
    # Regex jo kisi bhi domain se /s/ ke aage ka code nikal lega
    match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if match:
        surl = match.group(1)
        if surl.startswith('1'):
            surl = surl[1:]
        return surl
    return None

# ==========================================
# FRONTEND UI (Professional Dark Theme)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeraBox Premium Bypass</title>
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
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        }
        .loader {
            border: 4px solid rgba(255,255,255,0.1);
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: none;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="flex items-center justify-center p-4">

    <div class="glass-card w-full max-w-lg p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold mb-2"><i class="fa-solid fa-cloud-arrow-down text-blue-500"></i> TeraBox Bypass API</h1>
            <p class="text-gray-400 text-sm">Paste any TeraBox link to get direct high-speed stream/download link.</p>
        </div>

        <div class="space-y-4">
            <div>
                <input type="text" id="teraUrl" placeholder="https://terabox.com/s/1xyz..." 
                    class="w-full p-4 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition">
            </div>
            
            <button onclick="getDirectLink()" id="btnSubmit"
                class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300 flex justify-center items-center gap-2">
                <span>Extract Link</span>
                <div class="loader" id="spinner"></div>
            </button>
        </div>

        <div id="resultBox" class="mt-6 hidden">
            <div id="errorMsg" class="hidden bg-red-500 text-white p-3 rounded-lg text-sm mb-4"></div>
            
            <div id="successBox" class="hidden space-y-4">
                <div class="bg-gray-800 p-4 rounded-lg border border-gray-700">
                    <p class="text-xs text-gray-400 mb-1">File Name:</p>
                    <p id="fileName" class="text-sm font-semibold truncate"></p>
                </div>
                
                <div class="flex gap-2">
                    <a id="playBtn" href="#" target="_blank" class="flex-1 bg-green-600 hover:bg-green-700 text-center py-2 rounded-lg font-bold transition">
                        <i class="fa-solid fa-play"></i> Play/Download
                    </a>
                    <button onclick="copyLink()" class="flex-1 bg-gray-700 hover:bg-gray-600 text-center py-2 rounded-lg font-bold transition">
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

            if(!urlInput) {
                alert("Please enter a TeraBox link!");
                return;
            }

            // Show loading
            spinner.style.display = 'block';
            btn.disabled = true;
            resultBox.classList.remove('hidden');
            errorMsg.classList.add('hidden');
            successBox.classList.add('hidden');

            try {
                const response = await fetch(`/api/play?url=${encodeURIComponent(urlInput)}`);
                const data = await response.json();

                if(response.ok && data.status === 'success') {
                    document.getElementById('fileName').innerText = data.filename;
                    document.getElementById('playBtn').href = data.direct_play_link;
                    currentDirectLink = data.direct_play_link;
                    
                    successBox.classList.remove('hidden');
                } else {
                    errorMsg.innerText = data.error || "Failed to extract link.";
                    errorMsg.classList.remove('hidden');
                }
            } catch (err) {
                errorMsg.innerText = "Server Error! Please try again.";
                errorMsg.classList.remove('hidden');
            } finally {
                spinner.style.display = 'none';
                btn.disabled = false;
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

@app.route('/')
def home():
    # Frontend serve karna
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/play', methods=['GET'])
def get_stream_link():
    tera_url = request.args.get('url')
    
    if not tera_url:
        return jsonify({"error": "URL parameter missing."}), 400

    surl = extract_surl(tera_url)
    if not surl:
        return jsonify({"error": "Invalid TeraBox Link format."}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Cookie': TERABOX_COOKIE,
        'Accept': 'application/json, text/plain, */*'
    }

    api_url = f"https://www.terabox.com/share/list?app_id=250528&shorturl={surl}&root=1"
    
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data.get('errno') == 0:
            file_info = data['list'][0]
            return jsonify({
                "status": "success",
                "filename": file_info.get('server_filename'),
                "direct_play_link": file_info.get('dlink')
            })
        else:
            return jsonify({
                "error": "Link expired or invalid cookie.",
                "details": data
            }), 403
            
    except Exception as e:
        return jsonify({"error": f"Internal Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
