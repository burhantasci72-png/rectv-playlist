import requests
import json

# --- AYARLAR ---
MAIN_URL = "https://a.prectv67.lol"
SW_KEY = "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
USER_AGENT = "googleusercontent"
REFERER = "https://twitter.com/"

# Hangi kategoriler otomatik çekilsin?
# Format: "İsim": ("API_URL", Çekilecek_Sayfa_Sayısı)
CATEGORIES_TO_FETCH = {
    "Canlı TV": (f"{MAIN_URL}/api/channel/by/filtres/0/0/SAYFA/{SW_KEY}/", 2),
    "Son Filmler": (f"{MAIN_URL}/api/movie/by/filtres/0/created/SAYFA/{SW_KEY}/", 3)
}

def get_token():
    """Yeni Bearer Token Alır"""
    url = f"{MAIN_URL}/api/attest/nonce"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json().get("accessToken", response.text.strip())
        except:
            return response.text.strip()
    return None

def fetch_data(category_url, token, page_count):
    """Verileri Çeker"""
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER,
        "Authorization": f"Bearer {token}"
    }
    all_items =[]
    for page in range(page_count):
        url = category_url.replace("SAYFA", str(page))
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                if not data: break
                all_items.extend(data)
            except:
                pass
    return all_items

def main():
    token = get_token()
    if not token:
        print("Token alinamadi!")
        return

    # Dosyayı bir kere açıp, tüm kategorileri içine yazıyoruz
    with open("playlist.m3u", 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for cat_name, (cat_url, pages) in CATEGORIES_TO_FETCH.items():
            print(f"{cat_name} çekiliyor...")
            items = fetch_data(cat_url, token, pages)
            
            for item in items:
                title = item.get("title", "Isimsiz").replace(",", " ")
                image = item.get("image", "")
                sources = item.get("sources", [])
                
                if sources:
                    stream_url = sources[0].get("url", "")
                    if stream_url:
                        f.write(f'#EXTINF:-1 tvg-logo="{image}" group-title="{cat_name}",{title}\n')
                        f.write(f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n')
                        f.write(f'#EXTVLCOPT:http-referrer={REFERER}\n')
                        f.write(f'{stream_url}\n')
                        
    print("M3U listesi basariyla olusturuldu!")

if __name__ == "__main__":
    main()
