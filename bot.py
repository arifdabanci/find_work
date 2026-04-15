import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import google.generativeai as genai

# --- AYARLAR ---
# Gemini API Anahtarını GitHub Secrets'a eklemelisin
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

ARAMA_LISTESI = ["Data Curation", "Model Evaluation", "Prompt Engineering", "Object Detection", "AI Data Analyst"]
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
ALICI_POSTA = EMAIL_USER

# Senin Master CV Bilgilerin (Botun referans alacağı kaynak)
MASTER_CV_CONTEXT = """
Arif Tuna Dabancı - Engineering Student at KTU (Metallurgy & Materials).
Skills: Python (Automation, yfinance, GitHub Actions), AI Training (RLHF, Data Annotation at Crowdgen/OneForma), 
Computer Vision (Teknofest projects, PyTorch), E-commerce (Etsy owner), Latin Dance (Interpersonal communication).
Philosophy: First Principles, Antifragility.
"""

def cv_ozellestir(ilan_metni):
    """Gemini API kullanarak ilana özel CV bölümleri üretir."""
    prompt = f"""
    Aşağıdaki iş tanımı için benim bilgilerimi kullanarak ATS dostu bir 'Professional Summary' ve 'Key Skills' bölümü yaz. 
    İş Tanımı: {ilan_metni[:2000]} 
    Benim Bilgilerim: {MASTER_CV_CONTEXT}
    Lütfen sadece işe en uygun teknik yetkinliklerimi vurgula.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "CV önerisi oluşturulamadı."

def ilan_tara():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    ilan_detaylari = []
    
    for kelime in ARAMA_LISTESI:
        url = f"https://www.linkedin.com/jobs/search/?keywords={kelime.replace(' ', '%20')}&location=Turkey&f_TPR=r86400"
        driver.get(url)
        time.sleep(5)
        
        # İlan linklerini bul
        linkler = driver.find_elements(By.CLASS_NAME, "base-card__full-link")
        
        for i in linkler[:2]: # Her kategori için en iyi 2 ilan
            link = i.get_attribute('href')
            driver.get(link) # İlanın içine gir
            time.sleep(3)
            
            try:
                # İlan açıklamasını çek (LinkedIn'in yapısına göre güncellendi)
                description = driver.find_element(By.CLASS_NAME, "description__text").text
                ozel_cv = cv_ozellestir(description)
                ilan_detaylari.append(f"🔍 POZİSYON: {kelime}\n🔗 LİNK: {link}\n\n✨ ÖZEL CV ÖNERİSİ:\n{ozel_cv}\n" + "-"*30)
            except:
                ilan_detaylari.append(f"🔍 POZİSYON: {kelime}\n🔗 LİNK: {link}\n(İçerik okunamadı)\n" + "-"*30)
            
            driver.back() # Arama listesine dön
            time.sleep(2)
            
    driver.quit()
    return ilan_detaylari

def mail_at(icerik_listesi):
    if not icerik_listesi:
        print("Bugün yeni ilan yok.")
        return

    msg = EmailMessage()
    body = "Bulunan İlanlar ve Senin İçin Hazırlanan Özel CV Taslakları:\n\n" + "\n\n".join(icerik_listesi)
    msg.set_content(body)
    msg['Subject'] = f"🚀 İlana Özel CV'lerin Hazır! - {time.strftime('%d/%m/%Y')}"
    msg['From'] = EMAIL_USER
    msg['To'] = ALICI_POSTA

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("Özel CV önerileri e-postana gönderildi!")

# Çalıştır
sonuclar = ilan_tara()
mail_at(sonuclar)
