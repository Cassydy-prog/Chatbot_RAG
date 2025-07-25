import requests
from bs4 import BeautifulSoup
import trafilatura
import logging
import schedule
import time
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv



# -------------------
# CONFIGURATION
# -------------------

links = ["https://www.aivancity.ai/propos-daivancity",
         "https://www.aivancity.ai/edito",
         "https://www.aivancity.ai/societe-mission-et-engagements",
         "https://www.aivancity.ai/le-board-aivancity",
         "https://www.aivancity.ai/lequipe-aivancity",
         "https://www.aivancity.ai/labels-et-reconnaissances",
         "https://www.aivancity.ai/se-reperer-parmi-les-labels-et-reconnaissances",
         "https://www.aivancity.ai/partenaires",
         "https://www.aivancity.ai/notre-reseau",
         "https://www.aivancity.ai/le-fonds-de-dotation-un-outil-innovant-pour-financer-le-mecenat",
         "https://www.aivancity.ai/etudiant/programme/programme-grande-ecole",
         "https://www.aivancity.ai/etudiant/programme/bachelor-science-intelligence-artificielle-appliquee",
         "https://www.aivancity.ai/etudiant/programme/msc-data-engineering-cloud-computing",
         "https://www.aivancity.ai/etudiant/programme/master-science-data-management",
         "https://www.aivancity.ai/etudiant-et-professionnel/programme/master-science-artificial-intelligence-business",
         "https://www.aivancity.ai/etudiant-et-professionnel/programme/msc-intelligences-artificielles-generatives",
         "https://www.aivancity.ai/certificats",
         "https://www.aivancity.ai/programmes-courts",
         "https://www.aivancity.ai/offres-pour-les-entreprises-intra",
         "https://www.aivancity.ai/financer-votre-formation-professionnelle",
         "https://www.aivancity.ai/une-offre-de-formation-100-online-aivancityx",
         "https://www.aivancity.ai/summer-school",
         "https://www.aivancity.ai/hybridation",
         "https://www.aivancity.ai/la-clinique-de-lintelligence-artificielle-plus-quun-lieu-un-concept-pedagogique-cree-par-aivancity",
         "https://www.aivancity.ai/boarding-aivancity",
         "https://www.aivancity.ai/campus-de-paris-villejuif",
         "https://www.aivancity.ai/campus-de-nice",
         "https://www.aivancity.ai/international",
         "https://www.aivancity.ai/bourses-et-financement",
         "https://www.aivancity.ai/handicap-et-accessibilite",
         "https://www.aivancity.ai/corps-professoral",
         "https://www.aivancity.ai/axes-et-projets-de-recherche",
         "https://www.aivancity.ai/chaires-de-recherche-et-dinnovation",
         "https://www.aivancity.ai/knowledge",
         "https://www.aivancity.ai/projet-adoptia-porte-par-aivancity-laureat-de-2e-vague-de-lami-cma-france-2030",
         "https://www.aivancity.ai/la-garantie-de-mise-jour-du-diplome",
         "https://www.aivancity.ai/les-metiers-de-lintelligence-artificielle-ia-et-de-la-data",
         "https://www.aivancity.ai/le-stage-en-entreprise-un-pilier-de-la-pedagogie-daivancity",
         "https://www.aivancity.ai/lalternance-un-passeport-pour-lemploi-et-un-outil-de-recrutement",
         "https://www.aivancity.ai/la-mission-citoyenne",
         "https://www.aivancity.ai/actualites",
         "https://www.aivancity.ai/evenements",
         "https://www.aivancity.ai/rencontrez-nous"
]

corpus_path = "corpus_ecole.txt"
log_path = "scraping.log"

# -------------------
# LOGGING SETUP
# -------------------

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

# -------------------
# EMAIL ALERT FUNCTION
# -------------------

def send_error_email(subject, message):
    sender = "agentscrapingcassy@gmail.com"
    receiver = "agentscrapingcassy@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        logging.info("Alerte envoyée par email.")
    except Exception as e:
        logging.error(f"Echec de l'envoi de l'email : {e}")

# -------------------
# ANTI-DOUBLON
# -------------------

def load_existing_texts(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(f.read().split("\n\n"))

def is_duplicate(text, existing_texts):
    return text.strip() in existing_texts

# -------------------
# SCRAPING
# -------------------

def scrape_filtered_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["header", "footer", "nav", "aside", "script", "style"]):
            tag.decompose()

        texte = trafilatura.extract(str(soup))
        if texte:
            return texte.strip()
        else:
            logging.info(f"Aucun contenu utile trouvé pour {url}")
            return ""
    except Exception as e:
        logging.error(f"Erreur scraping pour {url} : {e}")
        send_error_email("Erreur scraping", f"{url} : {e}")
        return ""

# -------------------
# JOB PRINCIPAL
# -------------------

def main_scraping():
    existing_texts = load_existing_texts(corpus_path)

    with open(corpus_path, "a", encoding="utf-8") as f:
        for url in links:
            texte = scrape_filtered_html(url)
            if texte and not is_duplicate(texte, existing_texts):
                f.write(texte + "\n\n")
                logging.info(f"[OK] Contenu ajouté pour {url}")
            else:
                logging.info(f"[Doublon ou vide] Ignoré : {url}")

# -------------------
# SCHEDULER
# -------------------

schedule.every().day.at("08:00").do(main_scraping)

logging.info("Lancement du scheduler. En attente de la première exécution...")

while True:
    schedule.run_pending()
    time.sleep(60)
