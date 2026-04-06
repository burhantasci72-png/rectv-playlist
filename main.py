import requests

# --- AYARLAR ---
MAIN_URL = "https://a.prectv67.lol"
SW_KEY = "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
USER_AGENT = "googleusercontent"
REFERER = "https://twitter.com/"

# Hangi kategoriler otomatik çekilsin? (İsterseniz sayfa sayılarını artırabilirsiniz)
CATEGORIES_TO_FETCH = {
    "Canli TV": (f"{MAIN_URL}/api/channel/by/filtres/0/0/SAYFA/{SW_KEY}/", 2),
    "Son Filmler": (f"{MAIN_URL}/api/movie/by/filtres/0/created/SAYFA/{SW_KEY}/", 3),
    "Aile": (f"{MAIN_URL}/api/movie/by/filtres/14/created/SAYFA/{SW_KEY}/", 1),
    "Aksiyon": (f"{MAIN_URL}/api/movie/by/filtres/1/created/SAYFA/{SW_KEY}/", 2),
    "Animasyon": (f"{MAIN_URL}/api/movie/by/filtres/13/created/SAYFA/{SW_KEY}/", 1),
    "Belgesel": (f"{MAIN_URL}/api/movie/by/filtres/19/created/SAYFA/{SW_KEY}/", 1),
    "Bilim Kurgu": (f"{MAIN_URL}/api/movie/by/filtres/4/created/SAYFA/{SW_KEY}/", 1),
    "Dram": (f"{MAIN_URL}/api/movie/by/filtres/2/created/SAYFA/{SW_KEY}/", 1),
    "Komedi": (f"{MAIN_URL}/api/movie/by/filtres/3/created/SAYFA/{SW_KEY}/", 1),
    "Korku": (f"{MAIN_URL}/api/movie/by/filtres/8/created/SAYFA/{SW_KEY}/", 1)
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

def clean_filename(name):
    """Kategori adından düzgün dosya adı oluşturur (Boşlukları tire yapar, Türkçe karakterleri düzeltir)"""
    return name.lower().replace(" ", "_").replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ö", "o").replace("ğ", "g").replace("ü", "u")

def main():
    token = get_token()
    if not token:
        print("Token alinamadi!")
        return

    # GENEL LİSTE DOSYASINI AÇ (Tüm içerikler burada toplanacak)
    with open("genel_liste.m3u", 'w', encoding='utf-8') as f_general:
        f_general.write("#EXTM3U\n")
        
        for cat_name, (cat_url, pages) in CATEGORIES_TO_FETCH.items():
            print(f"{cat_name} çekiliyor...")
            
            # KATEGORİYE ÖZEL DOSYA ADI OLUŞTUR (Örn: canli_tv.m3u, son_filmler.m3u)
            cat_filename = f"{clean_filename(cat_name)}.m3u"
            
            # KATEGORİYE ÖZEL DOSYAYI AÇ
            with open(cat_filename, 'w', encoding='utf-8') as f_cat:
                f_cat.write("#EXTM3U\n")
                
                items = fetch_data(cat_url, token, pages)
                
                for item in items:
                    title = item.get("title", "Isimsiz").replace(",", " ")
                    image = item.get("image", "")
                    sources = item.get("sources",[])
                    
                    if sources:
                        stream_url = sources[0].get("url", "")
                        if stream_url:
                            # M3U formatı verisi
                            m3u_entry = (
                                f'#EXTINF:-1 tvg-logo="{image}" group-title="{cat_name}",{title}\n'
                                f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
                                f'#EXTVLCOPT:http-referrer={REFERER}\n'
                                f'{stream_url}\n'
                            )
                            
                            # HEM KATEGORİ DOSYASINA HEM DE GENEL DOSYAYA YAZ
                            f_cat.write(m3u_entry)
                            f_general.write(m3u_entry)
                            
    print("Tum listeler basariyla olusturuldu!")

if __name__ == "__main__":
    main()
