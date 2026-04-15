import time
import smtplib
import os
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from google import genai # Yeni kütüphane: google-genai

# --- AYARLAR ---
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

ARAMA_LISTESI = ["Data Curation", "Model Evaluation", "Prompt Engineering", "Object Detection", "AI Data Analyst"]
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
ALICI_POSTA = EMAIL_USER

# Master CV Context [cite: 51, 52, 53, 55, 56]
MASTER_CV_CONTEXT = """
Arif Tuna Dabancı - Engineering Student at KTU (Metallurgy & Materials)[cite: 51, 52].
Skills: Python (Automation, yfinance, GitHub Actions) [cite: 37], AI Training (RLHF, Data Annotation at Crowdgen/OneForma)[cite: 41, 42], 
Computer Vision (Teknofest projects, PyTorch) [cite: 23, 25], E-commerce (Etsy owner) [cite: 37], Latin Dance (Interpersonal communication)[cite: 56].
Philosophy: First Principles, Antifragility.
"""

def cv_ozellestir(ilan_metni):
    prompt = f"Aşağıdaki iş tanımı için benim bilgilerimi kullanarak ATS dostu bir 'Professional Summary' ve 'Key Skills' bölümü yaz.\nİş Tanımı: {ilan_metni[:2000]}\nBenim Bilgilerim: {MASTER_CV_CONTEXT}"
    try:
        # Yeni SDK formatı (generate_content yerine models.generate_content)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"CV önerisi oluşturulamadı: {str(e)}"

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
        
        # Linkleri önce metin olarak topla (StaleElement hatasını engeller)
        link_elementleri = driver.find_elements(By.CLASS_NAME, "base-card__full-link")
        linkler = [el.get_attribute('href') for el in link_elementleri[:2]]
        
        for link in linkler:
            try:
                driver.get(link)
                time.sleep(3)
                
                # İçeriği çek
                description = driver.find_element(By.CLASS_NAME, "description__text").text
                ozel_cv = cv_ozellestir(description)
                
                ilan_detaylari.append(f"🔍 POZİSYON: {kelime}\n🔗 LİNK: {link}\n\n✨ ÖZEL CV ÖNERİSİ:\n{ozel_cv}\n" + "-"*30)
            except Exception as e:
                ilan_detaylari.append(f"🔍 POZİSYON: {kelime}\n🔗 LİNK: {link}\n(Hata: {str(e)})\n" + "-"*30)
            
    driver.quit()
    return ilan_detaylari

def mail_at(icerik_listesi):
    if not icerik_listesi:
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

sonuclar = ilan_tara()
mail_at(sonuclar)
