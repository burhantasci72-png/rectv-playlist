from curl_cffi import requests
import time
import json

# --- AYARLAR ---
MAIN_URL = "https://a.prectv70.lol"
SW_KEY = "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
MAX_PAGES = 200 

CATEGORIES_TO_FETCH = {
    "Canli TV": f"{MAIN_URL}/api/channel/by/filtres/0/0/SAYFA/{SW_KEY}/",
    "Son Filmler": f"{MAIN_URL}/api/movie/by/filtres/0/created/SAYFA/{SW_KEY}/",
    "Aile": f"{MAIN_URL}/api/movie/by/filtres/14/created/SAYFA/{SW_KEY}/",
    "Aksiyon": f"{MAIN_URL}/api/movie/by/filtres/1/created/SAYFA/{SW_KEY}/",
    "Animasyon": f"{MAIN_URL}/api/movie/by/filtres/13/created/SAYFA/{SW_KEY}/",
    "Belgesel": f"{MAIN_URL}/api/movie/by/filtres/19/created/SAYFA/{SW_KEY}/",
    "Bilim Kurgu": f"{MAIN_URL}/api/movie/by/filtres/4/created/SAYFA/{SW_KEY}/",
    "Dram": f"{MAIN_URL}/api/movie/by/filtres/2/created/SAYFA/{SW_KEY}/",
    "Fantastik": f"{MAIN_URL}/api/movie/by/filtres/10/created/SAYFA/{SW_KEY}/",
    "Komedi": f"{MAIN_URL}/api/movie/by/filtres/3/created/SAYFA/{SW_KEY}/",
    "Korku": f"{MAIN_URL}/api/movie/by/filtres/8/created/SAYFA/{SW_KEY}/",
    "Macera": f"{MAIN_URL}/api/movie/by/filtres/17/created/SAYFA/{SW_KEY}/",
    "Romantik": f"{MAIN_URL}/api/movie/by/filtres/5/created/SAYFA/{SW_KEY}/"
}

# Cloudflare Aşımı için Chrome 120 parmak izini taklit eden Oturum (Session)
session = requests.Session(impersonate="chrome120")
session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://twitter.com/",
    "Connection": "keep-alive"
})

def get_token():
    """Yeni Bearer Token Alır"""
    url = f"{MAIN_URL}/api/attest/nonce"
    try:
        response = session.get(url, timeout=15)
        if response.status_code == 200:
            try:
                return response.json().get("accessToken", response.text.strip())
            except:
                return response.text.strip()
        else:
            print(f"    -> [HATA] Token alınamadı. Durum Kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"    -> [HATA] Token bağlantı sorunu: {e}")
        return None

def fetch_data(category_name, category_url, token):
    """Gelişmiş tarayıcı taklidiyle verileri çeker"""
    session.headers.update({"Authorization": f"Bearer {token}"})
    all_items = []
    
    for page in range(MAX_PAGES):
        url = category_url.replace("SAYFA", str(page))
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if not data: 
                            print(f"    -> [{category_name}] İçerik bitti. Toplam sayfa: {page}")
                            return all_items
                        
                        all_items.extend(data)
                        time.sleep(1.5) # Bloklanmamak için insansı bekleme süresi
                        break 
                        
                    except:
                        print(f"    -> [HATA] JSON Parçalanamadı (Sayfa: {page}).")
                        return all_items
                        
                elif response.status_code == 403:
                    if attempt < max_retries - 1:
                        wait_time = 15 * (attempt + 1)
                        print(f"    -> [UYARI] 403 Hızı Yakalandı! {wait_time} saniye bekleniyor... (Sayfa: {page})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"    -> [HATA] 403 Engeli aşılamadı. Mevcut verilerle devam ediliyor.")
                        return all_items
                else:
                    print(f"    -> [HATA] Sunucu hatası: {response.status_code}")
                    return all_items
                    
            except Exception as e:
                print(f"    -> [HATA] İstek hatası: {e}")
                return all_items
                
    return all_items

def clean_filename(name):
    return name.lower().replace(" ", "_").replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ö", "o").replace("ğ", "g").replace("ü", "u")

def main():
    print("[*] Gelişmiş Cloudflare Bypass Sistemi Başlatıldı...")
    
    with open("genel_liste.m3u", 'w', encoding='utf-8') as f_general:
        f_general.write("#EXTM3U\n")
        
        for cat_name, cat_url in CATEGORIES_TO_FETCH.items():
            print(f"\n[*] Kategori İşleniyor: {cat_name}")
            
            token = get_token()
            if not token:
                print(f"    -> Token alınamadığı için {cat_name} atlandı.")
                continue
                
            cat_filename = f"{clean_filename(cat_name)}.m3u"
            
            with open(cat_filename, 'w', encoding='utf-8') as f_cat:
                f_cat.write("#EXTM3U\n")
                
                items = fetch_data(cat_name, cat_url, token)
                
                if not items:
                    print(f"    -> UYARI: {cat_name} için veri çekilemedi.")
                    continue
                    
                eklenen_sayi = 0
                for item in items:
                    title = item.get("title", "Isimsiz").replace(",", " ")
                    image = item.get("image", "")
                    sources = item.get("sources", [])
                    
                    if sources:
                        stream_url = sources[0].get("url", "")
                        if stream_url:
                            m3u_entry = (
                                f'#EXTINF:-1 tvg-logo="{image}" group-title="{cat_name}",{title}\n'
                                f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\n'
                                f'#EXTVLCOPT:http-referrer=https://twitter.com/\n'
                                f'{stream_url}\n'
                            )
                            f_cat.write(m3u_entry)
                            f_general.write(m3u_entry)
                            eklenen_sayi += 1
                            
                print(f"    -> [{cat_name}] Başarıyla {eklenen_sayi} adet link M3U dosyasına yazıldı.")
            
            time.sleep(5) # Kategoriler arası sunucuyu dinlendirme
            
    print("\n[+] TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    main()
