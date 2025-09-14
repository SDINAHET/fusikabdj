from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime
import os

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# =======================
# PAGES LÉGALES
# =======================
@app.route('/cgv')
def cgv():
    return render_template('cgv.html')

@app.route('/cgu')
def cgu():
    return render_template('cgu.html')

@app.route('/politique_cookies')
def politique_cookies():
    return render_template('politique_cookies.html')

@app.route('/politique_confidentialite')
def politique_confidentialite():
    return render_template('politique_confidentialite.html')

@app.route('/mentions')
def mentions():
    return render_template('mentions.html')

# =======================
# PAGES PRINCIPALES
# =======================
@app.route('/')
def index():
    gallery_path = os.path.join(app.static_folder, 'gallery_confiance')
    images = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('index.html', images=images)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/gallery')
def gallery():
    gallery_path = os.path.join(app.static_folder, 'gallery')
    images = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('gallery.html', images=images)

# =======================
# CONTACT AVEC ENVOI MAIL
# =======================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        code_postal = request.form.get('code_postal')
        event_date_raw = request.form.get('event_date')
        location = request.form.get('location')
        contact_method = request.form.get('contact_method')
        demande = request.form.get('demande')
        besoins = request.form.getlist('besoin[]')

        # Conversion date en français
        if event_date_raw:
            try:
                event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                event_date = event_date_raw
        else:
            event_date = "Non précisée"

        # Besoins avec emojis
        besoins_emojis = {
            "pack_regie": "🎛️ Pack régie (sono + lumière)",
            "sonorisation": "🔊 Sonorisation",
            "barre_lumiere": "💡 Barre de lumière",
            "lyres": "🎇 Lyres",
            "video_projecteur": "📽️ Vidéo projecteur",
            "laser": "🔫 Laser",
            "machine_fumee": "💨 Machine à fumée",
            "machine_etincelle": "✨ Machine à étincelle",
            "machine_brouillard": "🌫️ Machine à brouillard"
        }

        besoins_formatted = "<br>".join([besoins_emojis.get(b, b) for b in besoins]) if besoins else "Aucun"
        demande_formatted = demande.replace('\n','<br>') if demande else "Aucun"

        logo_url = "https://lh3.googleusercontent.com/a-/ALV-UjWkHe66n_J1o9_PquFKOGeetukIAKfZxez9KCpF_SZaqmbE5BM=w72-h72-p-rp-mo-br100"

        # Contenu HTML mail pour admin
        html_admin = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
    <div style="max-width: 650px; margin: auto; background-color: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <div style="text-align:center;">
            <img src="{logo_url}" alt="Fusikab DJ" style="max-width:200px; margin-bottom:20px;">
        </div>
        <h2 style="color: #ffcc00; text-align: center;">📩 Nouvelle demande de contact - {prenom} {nom}</h2>
        <hr style="border:1px solid #ddd;">
        <p><strong>👤 Nom :</strong> {prenom} {nom}</p>
        <p><strong>✉️ Email :</strong> {email}</p>
        <p><strong>📞 Téléphone :</strong> {telephone}</p>
        <p><strong>📍 Code Postal :</strong> {code_postal}</p>
        <p><strong>📅 Date de l'évènement :</strong> {event_date}</p>
        <p><strong>📌 Lieu :</strong> {location}</p>
        <p><strong>☎️ Préférence contact :</strong> {'💌 Mail' if contact_method=='email' else '📞 Téléphone'}</p>
        <p><strong>🛠️ Besoins :</strong><br>{besoins_formatted}</p>
        <p><strong>💬 Message :</strong><br>{demande_formatted}</p>
        <hr style="border:1px solid #ddd;">
        <p style="text-align:center; color:#888;">Fusikab DJ - Formulaire de contact web</p>
    </div>
</body>
</html>
        """

        # Contenu HTML mail pour l'utilisateur
        html_user = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
    <div style="max-width: 650px; margin: auto; background-color: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <div style="text-align:center;">
            <img src="{logo_url}" alt="Fusikab DJ" style="max-width:200px; margin-bottom:20px;">
        </div>
        <h2 style="color: #28a745; text-align: center;">✅ Votre demande a été reçue !</h2>
        <p>Bonjour {prenom},</p>
        <p>Nous avons bien reçu votre demande de contact et reviendrons vers vous rapidement.</p>
        <p>Voici un récapitulatif de votre demande :</p>
        <p><strong>📅 Date de l'évènement :</strong> {event_date}</p>
        <p><strong>📌 Lieu :</strong> {location}</p>
        <p><strong>🛠️ Besoins :</strong><br>{besoins_formatted}</p>
        <p><strong>💬 Message :</strong><br>{demande_formatted}</p>
        <hr style="border:1px solid #ddd;">
        <p style="text-align:center; color:#888;">Fusikab DJ - Merci pour votre confiance !</p>
    </div>
</body>
</html>
        """

        try:
            # Envoi des mails
            mail.send(Message(subject=f"Demande de contact - {prenom} {nom}", recipients=[os.getenv('MAIL_USERNAME')], html=html_admin))
            mail.send(Message(subject="📬 Votre demande a bien été reçue - Fusikab DJ", recipients=[email], html=html_user))
            flash("✅ Votre message a été envoyé avec succès !", "success")
        except Exception as e:
            print(e)
            flash("❌ Une erreur est survenue lors de l'envoi. Merci de réessayer.", "danger")

        return redirect(url_for('contact'))

    return render_template('contact.html')

# =======================
# AUTRES PAGES
# =======================
@app.route('/disponibilites')
def disponibilites():
    return render_template('disponibilites.html')

@app.route('/sonorisation')
def sonorisation():
    return render_template('sonorisation.html')

@app.route('/lumieres')
def lumieres():
    return render_template('lumieres.html')

@app.route('/animation_musicale')
def animation_musicale():
    return render_template('animation_musicale.html')

@app.route('/engagement_ecoresponsable')
def engagement_ecoresponsable():
    return render_template('engagement_ecoresponsable.html')

@app.route('/prestations_sur_mesure')
def prestations_sur_mesure():
    return render_template('prestations_sur_mesure.html')

@app.route('/conseil_coaching')
def conseil_coaching():
    return render_template('conseil_coaching.html')

@app.route('/video_projection')
def video_projection():
    return render_template('video_projection.html')

@app.route('/animation_interactive')
def animation_interactive():
    return render_template('animation_interactive.html')

# =======================
# PARTENAIRES
# =======================
@app.route('/partenaire1_sallele5B')
def partenaire1_sallele5B():
    images_path = os.path.join(app.static_folder, 'images/partenaire1_sallele5B')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire1_sallele5B.html', images=images)

@app.route('/partenaires')
def partenaires():
    return render_template('partenaire/index_partenaires.html')

@app.route('/partenaire2_nozchantepie')
def partenaire2_nozchantepie():
    images_path = os.path.join(app.static_folder, 'images/partenaire2_nozchantepie')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire2_nozchantepie.html', images=images)

@app.route('/partenaire2_chateau')
def partenaire2_chateau():
    images_path = os.path.join(app.static_folder, 'images/partenaire2_chateau')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire2_chateau.html', images=images)

@app.route('/partenaire3_photographe')
def partenaire3_photographe():
    images_path = os.path.join(app.static_folder, 'images/partenaire3_photographe')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire3_photographe.html', images=images)

@app.route('/partenaire4_traiteur')
def partenaire4_traiteur():
    images_path = os.path.join(app.static_folder, 'images/partenaire4_traiteur')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire4_traiteur.html', images=images)

@app.route('/partenaire5_deco')
def partenaire5_deco():
    images_path = os.path.join(app.static_folder, 'images/partenaire5_deco')
    images = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('partenaire/partenaire5_deco.html', images=images)

# =======================
# LANCEMENT APP
# =======================
if __name__ == '__main__':
    app.run(debug=True)
