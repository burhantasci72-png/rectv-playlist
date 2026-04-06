import requests
import time

# --- AYARLAR ---
MAIN_URL = "https://a.prectv67.lol"
SW_KEY = "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
USER_AGENT = "googleusercontent"
REFERER = "https://twitter.com/"

# Sonsuz döngüyü engellemek için güvenlik amaçlı maksimum sayfa sayısı (1 sayfa ort. 15-20 film içerir. 200 sayfa = ~4000 film)
MAX_PAGES = 200 

# TÜM KATEGORİ LİSTESİ (Macera, Fantastik ve Romantik eklendi)
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

def fetch_data(category_name, category_url, token):
    """Kategorideki TÜM verileri bitene kadar çeker"""
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER,
        "Authorization": f"Bearer {token}"
    }
    all_items =[]
    
    for page in range(MAX_PAGES):
        url = category_url.replace("SAYFA", str(page))
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                # EĞER SAYFA BOŞ GELİRSE (Tüm filmler bittiyse) döngüyü kır!
                if not data: 
                    print(f"    -> [{category_name}] İçerik bitti. Toplam çekilen sayfa: {page}")
                    break
                
                all_items.extend(data)
                time.sleep(0.1) # Sunucuyu yorup ban yememek için milisaniyelik ufak bir bekleme
                
            except:
                break
        else:
            break
            
    return all_items

def clean_filename(name):
    """Kategori adından düzgün dosya adı oluşturur"""
    return name.lower().replace(" ", "_").replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ö", "o").replace("ğ", "g").replace("ü", "u")

def main():
    token = get_token()
    if not token:
        print("Token alinamadi!")
        return

    print("İçerikler çekiliyor. Bu işlem kategorideki tüm filmler çekileceği için biraz sürebilir...\n")

    # GENEL LİSTE
    with open("genel_liste.m3u", 'w', encoding='utf-8') as f_general:
        f_general.write("#EXTM3U\n")
        
        for cat_name, cat_url in CATEGORIES_TO_FETCH.items():
            print(f"[*] İşleniyor: {cat_name}")
            
            # KATEGORİ DOSYASI
            cat_filename = f"{clean_filename(cat_name)}.m3u"
            
            with open(cat_filename, 'w', encoding='utf-8') as f_cat:
                f_cat.write("#EXTM3U\n")
                
                # Tüm sayfaları çeken fonksiyonumuzu çağırıyoruz
                items = fetch_data(cat_name, cat_url, token)
                
                for item in items:
                    title = item.get("title", "Isimsiz").replace(",", " ")
                    image = item.get("image", "")
                    sources = item.get("sources",[])
                    
                    if sources:
                        stream_url = sources[0].get("url", "")
                        if stream_url:
                            m3u_entry = (
                                f'#EXTINF:-1 tvg-logo="{image}" group-title="{cat_name}",{title}\n'
                                f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
                                f'#EXTVLCOPT:http-referrer={REFERER}\n'
                                f'{stream_url}\n'
                            )
                            
                            f_cat.write(m3u_entry)
                            f_general.write(m3u_entry)
                            
    print("\n[+] BÜTÜN KATEGORİLERİN TÜM FİLMLERİ BAŞARIYLA ÇEKİLDİ VE KAYDEDİLDİ!")

if __name__ == "__main__":
    main()
