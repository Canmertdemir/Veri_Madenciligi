from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlencode

app = Flask(__name__, static_folder='static', template_folder='templates')


class ImageRequest:
    def __init__(self, url: str, sorgu: str):
        self.url = url
        self.sorgu = sorgu

def url_sorgu_al(url: str, sorgu: str):
    try:
        # Sorguyu URL'ye doğru şekilde ekle
        sorgulu_url = f"{url}?s={sorgu}"
        print(f"Tam URL: {sorgulu_url}")  # DEBUG

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(sorgulu_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')  # 'html.parser' kullanın
  # lxml parser
        img_tags = soup.find_all("img", src=True)
        print(f"{len(img_tags)} adet img bulundu.")  # DEBUG

        if img_tags:
            img_src = img_tags[0]["src"]
            return requests.compat.urljoin(sorgulu_url, img_src)  # mutlak yol çözümü
        return None
    except Exception as e:
        print(f"Hata: {e}")
        return None

def resim_indir(img_url: str, dosya_adi: str = "resim.gif") -> bool:
    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()
        with open(dosya_adi, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Görsel başarıyla '{dosya_adi}' olarak kaydedildi.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Görsel indirilirken bir hata oluştu: {e}")
        return False
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
        return False

@app.route("/")
def index():
    return render_template('index.html')
@app.route("/cek-gif/", methods=["POST"])
def cek_gif():
    try:
        data = request.get_json()  # JSON formatında veri alınır
        url = data.get("url")
        sorgu = data.get("sorgu")

        if not url or not sorgu:
            return jsonify({"error": "URL ve sorgu parametreleri zorunludur."}), 400

        img_url = url_sorgu_al(url, sorgu)
        if img_url:
            success = resim_indir(img_url)
            if success:
                return jsonify({"message": "Görsel başarıyla indirildi.", "img_url": img_url})
            else:
                return jsonify({"error": "Görsel indirilirken bir hata oluştu."}), 500
        else:
            return jsonify({"error": "Uygun bir görsel bulunamadı."}), 404
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen bir hata oluştu: {e}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
