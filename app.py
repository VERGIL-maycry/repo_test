from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import re
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# ===== GLOBAL STATE =====
conversation_states = {}
user_preferences = {}  # Store theme and font size preferences

# ===== CHATBOT DATA =====
qa_pairs = [
    # Acte de naissance
    {
        "questions": [
            "comment obtenir un acte de naissance", "acte de naissance", "acte naissance", "act naissance", 
            "acte naiss", "acte de naiss", "acte d naissance", "acte d'naissance", "acte dnaisance", 
            "كيف أحصل على عقد الازدياد", "عقد الازدياد", "عقد ازدياد", "عقد الازدياد؟", "عقد ازدياد؟", 
            "akd izdiad", "chahada izdiad", "akd l izdiad"
        ],
        "answer": """<div class="answer-section">
        <h4>📋 Documents requis / الوثائق المطلوبة :</h4>
        <ul>
            <li>Formulaire de demande rempli et signé / استمارة الطلب معبأة وموقعة</li>
            <li>Pièce d'identité du demandeur / بطاقة التعريف الوطنية للمتقدم</li>
            <li>Livret de famille (si disponible) / دفتر الحالة المدنية (إن وجد)</li>
            <li>Timbres fiscaux (montant selon le type de demande) / طوابع ضريبية (المبلغ حسب نوع الطلب)</li>
        </ul>
    </div>"""
    },
    
    # Horaires d'ouverture
    {
        "questions": [
            "quels sont les horaires d'ouverture", "horaires d'ouverture", "heures d'ouverture", 
            "horaire d'ouverture", "horaire ouverture", "horaire mairie", "horaire commune","horaire", 
            "horraire", "horraires", "ما هي أوقات العمل", "أوقات العمل", "اوقات العمل", 
            "اوقات العمل؟", "اوقات العمل الجماعة", "اوقات العمل في الجماعة", "awkat l3amal", 
            "awqat l3amal", "ouverture", "ouvertur", "ouvertur mairie"
        ],
        "answer": """<div class="answer-section">
        <h4>🕐 Horaires d'ouverture / أوقات العمل :</h4>
        <p><strong>Lundi - Vendredi / الاثنين - الجمعة :</strong> 8h00 - 16h00 / 8:00 صباحاً - 4:00 مساءً</p>
        <p><strong>Samedi / السبت :</strong> 8h00 - 12h00 / 8:00 صباحاً - 12:00 ظهراً</p>
        <p><strong>Dimanche / الأحد :</strong> Fermé / مغلق</p>
    </div>"""
    },
    
    # Certificat de résidence
    {
        "questions": [
            "comment obtenir un certificat de résidence", "certificat de résidence", "certificat résidence", 
            "certif residence", "certif de residence", "certificat de res", "certificat res", 
            "certificat de residance", "certificat de resedence", "كيف أحصل على شهادة السكنى", 
            "شهادة السكنى", "شهادة سكنى", "شهادة السكنى؟", "شهادة سكنى؟", "chahada sokna", 
            "shahada sokna", "chahadat sokna", "shahadat sokna"
        ],
        "answer": """<div class="answer-section">
        <h4>🏠 Documents requis / الوثائق المطلوبة :</h4>
        <ul>
            <li>Formulaire de demande rempli et signé / استمارة الطلب معبأة وموقعة</li>
            <li>Pièce d'identité nationale / البطاقة الوطنية للتعريف</li>
            <li>Justificatif de domicile (facture d'eau, électricité, téléphone) / وثيقة تثبت العنوان (فاتورة ماء، كهرباء، هاتف)</li>
            <li>Contrat de location ou titre de propriété (si applicable) / عقد الإيجار أو سند الملكية (إن وجد)</li>
            <li>Timbres fiscaux (10 dirhams) / طوابع ضريبية (10 دراهم)</li>
        </ul>
    </div>"""
    },
    
    # Adresse de la mairie
    {
        "questions": [
            "où se trouve la mairie", "ou se trouve la mairie", "ou est la mairie", "ou est mairie", "localisation", 
            "adresse de la mairie", "adresse mairie", "adresse commune", "mairie fes", "mairie de fes", 
            "mairie fès", "mairie fes adresse", "mairie fès adresse", "mairie fes adrsse", 
            "mairie fes adrese", "mairie fes adr", "mairie fes adrresse", "أين توجد الجماعة", 
            "عنوان الجماعة", "عنوان الجماعة؟", "اين توجد الجماعة", "اين الجماعة", "فين الجماعة", 
            "fin ljam3a", "fin jam3a"
        ],
        "answer": """<div class="answer-section">
        <h4>📍 Adresse de la mairie / عنوان الجماعة :</h4>
        <p><strong>Commune de Fès / جماعة فاس</strong></p>
        <p>Avenue des FAR / شارع القوات المسلحة الملكية</p>
        <p>Fès, Maroc / فاس، المغرب</p>
        <p><strong>Téléphone / الهاتف :</strong> 05 35 62 56 95</p>
    </div>"""
    },
    
    # Carte nationale d'identité
    {
        "questions": [
            "comment obtenir une carte d'identité nationale", "carte d'identité nationale", "cni", 
            "demande cni", "طلب بطاقة التعريف الوطنية", "بطاقة التعريف الوطنية", "carte nationale d'identité", 
            "carte identite nationale", "carte d'identite nationale", "carte d'identité nationnal", 
            "carte d'identité nationnal", "cni maroc", "cni marroc", "cni marok", "بطاقة تعريف وطنية", 
            "بطاقة تعريف", "بطاقة وطنية", "بطاقة تعريف وطنية؟", "بطاقة تعريف؟", "بطاقة وطنية؟", 
            "carta watania", "carta watania maroc", "carta watania marok"
        ],
        "answer": """<div class="answer-section">
        <h4>🆔 Documents requis / الوثائق المطلوبة :</h4>
        <ul>
            <li>Extrait d'acte de naissance récent (moins de 3 mois) / نسخة موجزة من عقد الازدياد حديثة (أقل من 3 أشهر)</li>
            <li>4 photos d'identité récentes, en couleur, sur fond blanc / أربع صور فوتوغرافية حديثة ملونة بخلفية بيضاء</li>
            <li>Certificat de résidence / شهادة السكنى</li>
            <li>Ancienne carte d'identité (en cas de renouvellement) / البطاقة الوطنية القديمة (في حالة التجديد)</li>
            <li>Timbres fiscaux (30 dirhams) / طوابع ضريبية (30 دراهم)</li>
        </ul>
        <p><strong>Durée de traitement / مدة المعالجة :</strong> 15-30 jours / 15-30 يوماً</p>
    </div>"""
    },
    
    # Taxes municipales
    {
        "questions": [
            "comment payer les taxes municipales", "paiement des taxes", "taxes municipales", "taxe municipale", 
            "taxe communal", "taxe communale", "taxe communale fes", "taxe fes", "taxes fes", 
            "tax municipale", "tax municipale fes", "دفع الضرائب الجماعية", "الضرائب الجماعية", 
            "دفع الضرائب", "دفع الضرائب؟", "دفع الضرائب الجماعية؟", "taxe", "tax", "taxs", "taxess", 
            "taxe communale?", "taxe municipale?"
        ],
        "answer": """<div class="answer-section">
        <h4>💰 Paiement des taxes / دفع الضرائب :</h4>
        <p><strong>Lieu de paiement / مكان الدفع :</strong></p>
        <ul>
            <li>Service des finances de la commune / مصلحة المالية بالجماعة</li>
            <li>En ligne (si disponible) / عبر الإنترنت (إن وجد)</li>
            <li>Guichet automatique / الصراف الآلي</li>
        </ul>
        <p><strong>Modes de paiement / طرق الدفع :</strong> Espèces, chèque, carte bancaire / نقداً، شيك، بطاقة بنكية</p>
    </div>"""
    },
    
    # Rendez-vous
    {
        "questions": [
            "comment prendre rendez-vous à la mairie", "prise de rendez-vous", "rendez-vous mairie", 
            "rendez vous mairie", "prendre rdv mairie", "prendre rdv", "prendre rendez-vous", 
            "prendre rendez vous", "rdv mairie", "rdv commune", "حجز موعد في الجماعة", "موعد في الجماعة", 
            "حجز موعد", "حجز موعد؟", "موعد جماعة", "موعد جماعة؟", "rdv", "rdv جماعة", "rdv جماعة؟"
        ],
        "answer": """<div class="answer-section">
        <h4>📅 Prise de rendez-vous / حجز المواعيد :</h4>
        <p><strong>Méthodes disponibles / الطرق المتاحة :</strong></p>
        <ul>
            <li>Par téléphone / بالهاتف : 05 35 62 56 95</li>
            <li>Sur place / في المكان : Guichet d'accueil / مكتب الاستقبال</li>
            <li>En ligne / عبر الإنترنت : Site web de la commune / موقع الجماعة</li>
        </ul>
        <p><strong>Horaires de prise de RDV / أوقات حجز المواعيد :</strong> 8h00 - 16h00 (Lun-Ven) / 8:00 صباحاً - 4:00 مساءً (الاثنين-الجمعة)</p>
    </div>"""
    },
    
    # Extrait de mariage
    {
        "questions": [
            "comment obtenir un extrait de mariage", "extrait de mariage", "demande extrait de mariage", 
            "extrait mariage", "extrait de marige", "extrait marige", "extrait mariage fes", 
            "extrait mariage fès", "طلب نسخة من عقد الزواج", "نسخة من عقد الزواج", "نسخة عقد الزواج", 
            "نسخة من عقد الزواج؟", "نسخة عقد الزواج؟", "عقد الزواج", "عقد الزواج؟", "chahada zawaj", 
            "chahadat zawaj"
        ],
        "answer": """<div class="answer-section">
        <h4>💒 Documents requis / الوثائق المطلوبة :</h4>
        <ul>
            <li>Formulaire de demande rempli et signé / استمارة الطلب معبأة وموقعة</li>
            <li>Pièce d'identité nationale / البطاقة الوطنية للتعريف</li>
            <li>Informations sur le mariage (date, lieu, noms des époux) / معلومات عن الزواج (التاريخ، المكان، أسماء الزوجين)</li>
            <li>Livret de famille (si disponible) / دفتر الحالة المدنية (إن وجد)</li>
            <li>Timbres fiscaux (15 dirhams) / طوابع ضريبية (15 دراهم)</li>
        </ul>
    </div>"""
    },
    
    # Services en ligne
    {
        "questions": [
            "quels sont les services en ligne disponibles", "services en ligne", "service en ligne", 
            "service enligne", "services enligne", "services online", "service online", 
            "الخدمات الإلكترونية المتوفرة", "الخدمات الإلكترونية", "الخدمات الالكترونية", 
            "الخدمات الالكترونية المتوفرة", "خدمات إلكترونية", "خدمات الكترونية", "خدمات اونلاين", 
            "خدمات عبر الانترنت", "services electroniques", "services electronique"
        ],
        "answer": """<div class="answer-section">
        <h4>💻 Services en ligne disponibles / الخدمات الإلكترونية المتوفرة :</h4>
        <ul>
            <li>Demande d'actes d'état civil / طلب وثائق الحالة المدنية</li>
            <li>Paiement des taxes municipales / دفع الضرائب الجماعية</li>
            <li>Prise de rendez-vous / حجز المواعيد</li>
            <li>Consultation des horaires / استشارة الأوقات</li>
            <li>Téléchargement de formulaires / تحميل الاستمارات</li>
        </ul>
        <p><strong>Site web / الموقع الإلكتروني :</strong> www.commune-fes.ma</p>
    </div>"""
    },
    
    # Propreté
    {
        "questions": [
            "comment signaler un problème de propreté", "déchets", "propreté urbaine", "proprete urbaine", 
            "proprete", "proprete", "proprete fes", "proprete fès", "proprete commune", "proprete ville", 
            "النفايات", "النظافة الحضرية", "الإبلاغ عن النفايات", "الإبلاغ عن النظافة", "النظافة", 
            "النظافة؟", "نفايات", "نفايات؟", "بلاغ عن النفايات", "بلاغ عن النظافة", "بلاغ عن نفايات", 
            "بلاغ عن نظافة"
        ],
        "answer": """<div class="answer-section">
        <h4>🧹 Signalement de problèmes / الإبلاغ عن المشاكل :</h4>
        <p><strong>Contactez le service d'hygiène / تواصل مع مصلحة النظافة :</strong></p>
        <ul>
            <li>Téléphone / الهاتف : 05 35 62 56 95</li>
            <li>Email / البريد الإلكتروني : hygiene@commune-fes.ma</li>
            <li>Sur place / في المكان : Service d'hygiène / مصلحة النظافة</li>
        </ul>
        <p><strong>Types de problèmes / أنواع المشاكل :</strong> Déchets, saleté, éclairage défaillant / نفايات، قذارة، إضاءة معطلة</p>
    </div>"""
    },
    
    # Numéro d'urgence
    {
        "questions": [
            "quel est le numéro d'urgence de la commune", "contact d'urgence", "numéro d'urgence", 
            "numero d'urgence", "numero urgence", "num d'urgence", "num urgence", "رقم الطوارئ بالجماعة", 
            "رقم الطوارئ", "رقم الطوارئ؟", "رقم الطوارئ الجماعة", "رقم الطوارئ في الجماعة", 
            "رقم الطوارئ جماعة", "رقم الطوارئ جماعة؟", "رقم الطوارئ بالجماعة؟", "num urgence commune", 
            "num urgence mairie"
        ],
        "answer": """<div class="answer-section">
        <h4>🚨 Numéros d'urgence / أرقام الطوارئ :</h4>
        <ul>
            <li><strong>Commune de Fès / جماعة فاس :</strong> 05 35 62 56 95</li>
            <li><strong>Police / الشرطة :</strong> 19</li>
            <li><strong>Pompiers / المطافئ :</strong> 15</li>
            <li><strong>Ambulance / الإسعاف :</strong> 15</li>
        </ul>
        <p><strong>Service 24h/24 / خدمة 24 ساعة :</strong> Oui / نعم</p>
    </div>"""
    }
]

# ===== INTENT RECOGNITION =====
def recognize_intent(question):
    normalized = question.lower().strip()
    
    # Document-related intents
    if any(phrase in normalized for phrase in ['acte de naissance', 'عقد الازدياد']):
        return {"intent": "birth_certificate", "confidence": 0.9, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['carte d\'identité', 'بطاقة التعريف']):
        return {"intent": "national_id", "confidence": 0.9, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['passeport', 'جواز السفر']):
        return {"intent": "passport", "confidence": 0.9, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['certificat de résidence', 'شهادة السكنى']):
        return {"intent": "residence_certificate", "confidence": 0.9, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['mariage', 'زواج']):
        return {"intent": "marriage", "confidence": 0.8, "requires_follow_up": True}
    
    # Service-related intents
    if any(phrase in normalized for phrase in ['horaires', 'أوقات']):
        return {"intent": "opening_hours", "confidence": 0.8, "requires_follow_up": False}
    if any(phrase in normalized for phrase in ['adresse', 'عنوان']):
        return {"intent": "address", "confidence": 0.8, "requires_follow_up": False}
    if any(phrase in normalized for phrase in ['taxes', 'ضرائب']):
        return {"intent": "taxes", "confidence": 0.8, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['commerce', 'محل تجاري']):
        return {"intent": "business", "confidence": 0.8, "requires_follow_up": True}
    
    # General intents
    if any(phrase in normalized for phrase in ['aide', 'مساعدة']):
        return {"intent": "help", "confidence": 0.7, "requires_follow_up": True}
    if any(phrase in normalized for phrase in ['rendez-vous', 'موعد']):
        return {"intent": "appointment", "confidence": 0.8, "requires_follow_up": True}
    
    return {"intent": "unknown", "confidence": 0.3, "requires_follow_up": False}

# ===== CONVERSATION FLOW =====
def get_follow_up_question(intent, step=1):
    follow_ups = {
        'birth_certificate': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>📋 Type d'acte de naissance :</h4>
        <p>Pour quel type d'acte de naissance avez-vous besoin ?</p>
        <ul>
            <li>Extrait simple</li>
            <li>Copie intégrale</li>
            <li>Acte avec mentions marginales</li>
        </ul>
    </div>
    <div class="arabic-section">
        <h4>📋 نوع عقد الازدياد :</h4>
        <p>ما نوع عقد الازدياد الذي تحتاجه؟</p>
        <ul>
            <li>نسخة بسيطة</li>
            <li>نسخة كاملة</li>
            <li>عقد مع إشارات هامشية</li>
        </ul>
    </div>
</div>"""
        },
        'national_id': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>🆔 Type de demande :</h4>
        <p>S'agit-il d'une première demande ou d'un renouvellement ?</p>
    </div>
    <div class="arabic-section">
        <h4>🆔 نوع الطلب :</h4>
        <p>هل هي طلب أولي أم تجديد؟</p>
    </div>
</div>"""
        },
        'passport': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>📘 Type de demande :</h4>
        <p>S'agit-il d'une première demande ou d'un renouvellement ?</p>
    </div>
    <div class="arabic-section">
        <h4>📘 نوع الطلب :</h4>
        <p>هل هي طلب أولي أم تجديد؟</p>
    </div>
</div>"""
        },
        'residence_certificate': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>🏠 Durée de résidence :</h4>
        <p>Habitez-vous à cette adresse depuis plus de 6 mois ?</p>
    </div>
    <div class="arabic-section">
        <h4>🏠 مدة السكنى :</h4>
        <p>هل تسكن في هذا العنوان منذ أكثر من 6 أشهر؟</p>
    </div>
</div>"""
        },
        'marriage': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>💒 Type de mariage :</h4>
        <p>S'agit-il d'un mariage civil ou religieux ?</p>
    </div>
    <div class="arabic-section">
        <h4>💒 نوع الزواج :</h4>
        <p>هل هو زواج مدني أم ديني؟</p>
    </div>
</div>"""
        },
        'taxes': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>💰 Type de taxes :</h4>
        <p>Quel type de taxes souhaitez-vous payer ?</p>
    </div>
    <div class="arabic-section">
        <h4>💰 نوع الضرائب :</h4>
        <p>ما نوع الضرائب التي تريد دفعها؟</p>
    </div>
</div>"""
        },
        'business': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>🏪 Type de commerce :</h4>
        <p>Quel type de commerce souhaitez-vous ouvrir ?</p>
    </div>
    <div class="arabic-section">
        <h4>🏪 نوع المحل التجاري :</h4>
        <p>ما نوع المحل التجاري الذي تريد فتحه؟</p>
    </div>
</div>"""
        },
        'appointment': {
            1: """<div class="answer-section">
    <div class="french-section">
        <h4>📅 Service demandé :</h4>
        <p>Pour quel service souhaitez-vous un rendez-vous ?</p>
    </div>
    <div class="arabic-section">
        <h4>📅 الخدمة المطلوبة :</h4>
        <p>ما الخدمة التي تريد موعداً لها؟</p>
    </div>
</div>"""
        }
    }
    
    return follow_ups.get(intent, {}).get(step)

def process_conversation_step(user_input, intent, step):
    responses = {
        'birth_certificate': {
            1: {
                'extrait simple': """<div class="answer-section">
    <div class="french-section">
        <h4>📋 Extrait simple - Documents requis :</h4>
        <ul>
            <li>Formulaire de demande</li>
            <li>Pièce d'identité</li>
            <li>Timbres fiscaux (5 dirhams)</li>
        </ul>
        <p><strong>Durée de traitement :</strong> 2-3 jours</p>
    </div>
    <div class="arabic-section">
        <h4>📋 نسخة بسيطة - الوثائق المطلوبة :</h4>
        <ul>
            <li>استمارة الطلب</li>
            <li>بطاقة التعريف</li>
            <li>طوابع ضريبية (5 دراهم)</li>
        </ul>
        <p><strong>مدة المعالجة :</strong> 2-3 أيام</p>
    </div>
</div>""",
                'copie intégrale': """<div class="answer-section">
    <div class="french-section">
        <h4>📋 Copie intégrale - Documents requis :</h4>
        <ul>
            <li>Formulaire de demande</li>
            <li>Pièce d'identité</li>
            <li>Livret de famille</li>
            <li>Timbres fiscaux (10 dirhams)</li>
        </ul>
        <p><strong>Durée de traitement :</strong> 3-5 jours</p>
    </div>
    <div class="arabic-section">
        <h4>📋 نسخة كاملة - الوثائق المطلوبة :</h4>
        <ul>
            <li>استمارة الطلب</li>
            <li>بطاقة التعريف</li>
            <li>دفتر الحالة المدنية</li>
            <li>طوابع ضريبية (10 دراهم)</li>
        </ul>
        <p><strong>مدة المعالجة :</strong> 3-5 أيام</p>
    </div>
</div>""",
                'acte avec mentions marginales': """<div class="answer-section">
    <div class="french-section">
        <h4>📋 Acte avec mentions - Documents requis :</h4>
        <ul>
            <li>Formulaire de demande</li>
            <li>Pièce d'identité</li>
            <li>Livret de famille</li>
            <li>Justificatifs des mentions</li>
            <li>Timbres fiscaux (15 dirhams)</li>
        </ul>
        <p><strong>Durée de traitement :</strong> 5-7 jours</p>
    </div>
    <div class="arabic-section">
        <h4>📋 عقد مع إشارات - الوثائق المطلوبة :</h4>
        <ul>
            <li>استمارة الطلب</li>
            <li>بطاقة التعريف</li>
            <li>دفتر الحالة المدنية</li>
            <li>وثائق الإشارات</li>
            <li>طوابع ضريبية (15 دراهم)</li>
        </ul>
        <p><strong>مدة المعالجة :</strong> 5-7 أيام</p>
    </div>
</div>""",
                'default': """<div class="answer-section">
    <div class="french-section">
        <h4>📋 Aide pour l'acte de naissance :</h4>
        <p>Je vais vous guider pour obtenir votre acte de naissance. Pouvez-vous me préciser le type d'acte dont vous avez besoin ?</p>
    </div>
    <div class="arabic-section">
        <h4>📋 مساعدة لعقد الازدياد :</h4>
        <p>سأرشدك للحصول على عقد الازدياد. هل يمكنك تحديد نوع العقد الذي تحتاجه؟</p>
    </div>
</div>"""
            }
        },
        'national_id': {
            1: {
                'première demande': "Pour une première demande de CNI, vous aurez besoin de :\n- Extrait d'acte de naissance récent\n- 4 photos d'identité\n- Certificat de résidence\n- Timbres fiscaux (30 dirhams)\n\nلطلب أولي للبطاقة الوطنية ستحتاج إلى:\n- نسخة عقد الازدياد حديثة\n- 4 صور فوتوغرافية\n- شهادة السكنى\n- طوابع ضريبية (30 دراهم)",
                'renouvellement': "Pour le renouvellement de votre CNI, vous aurez besoin de :\n- Ancienne carte d'identité\n- 4 photos d'identité récentes\n- Certificat de résidence\n- Timbres fiscaux (30 dirhams)\n\nلتجديد البطاقة الوطنية ستحتاج إلى:\n- البطاقة الوطنية القديمة\n- 4 صور فوتوغرافية حديثة\n- شهادة السكنى\n- طوابع ضريبية (30 دراهم)",
                'default': "Je vais vous aider avec votre demande de carte d'identité. S'agit-il d'une première demande ou d'un renouvellement ?\n\nسأساعدك في طلب البطاقة الوطنية. هل هي طلب أولي أم تجديد؟"
            }
        },
        'passport': {
            1: {
                'première demande': "Pour une première demande de passeport, vous aurez besoin de :\n- Carte d'identité nationale\n- 4 photos d'identité\n- Extrait d'acte de naissance\n- Certificat de résidence\n- Timbres fiscaux (200 dirhams)\n\nلطلب أولي لجواز السفر ستحتاج إلى:\n- البطاقة الوطنية للتعريف\n- 4 صور فوتوغرافية\n- نسخة عقد الازدياد\n- شهادة السكنى\n- طوابع ضريبية (200 دراهم)",
                'renouvellement': "Pour le renouvellement de votre passeport, vous aurez besoin de :\n- Ancien passeport\n- Carte d'identité nationale\n- 4 photos d'identité\n- Timbres fiscaux (200 dirhams)\n\nلتجديد جواز السفر ستحتاج إلى:\n- جواز السفر القديم\n- البطاقة الوطنية للتعريف\n- 4 صور فوتوغرافية\n- طوابع ضريبية (200 دراهم)",
                'default': "Je vais vous aider avec votre demande de passeport. S'agit-il d'une première demande ou d'un renouvellement ?\n\nسأساعدك في طلب جواز السفر. هل هي طلب أولي أم تجديد؟"
            }
        },
        'residence_certificate': {
            1: {
                'oui': "Parfait ! Pour obtenir votre certificat de résidence, vous aurez besoin de :\n- Formulaire de demande\n- Pièce d'identité nationale\n- Justificatifs de domicile (factures)\n- Timbres fiscaux (10 dirhams)\n\nممتاز! للحصول على شهادة السكنى ستحتاج إلى:\n- استمارة الطلب\n- البطاقة الوطنية للتعريف\n- وثائق العنوان (فواتير)\n- طوابع ضريبية (10 دراهم)",
                'non': "Pour obtenir un certificat de résidence, vous devez d'abord résider à cette adresse depuis au moins 6 mois. Pouvez-vous me confirmer votre situation ?\n\nللحصول على شهادة السكنى يجب أن تسكن في هذا العنوان منذ 6 أشهر على الأقل. هل يمكنك تأكيد وضعك؟",
                'default': "Pour vous aider avec le certificat de résidence, habitez-vous à cette adresse depuis plus de 6 mois ?\n\nلمساعدتك في شهادة السكنى، هل تسكن في هذا العنوان منذ أكثر من 6 أشهر؟"
            }
        },
        'marriage': {
            1: {
                'civil': "Pour un mariage civil, vous aurez besoin de :\n- Formulaire de demande\n- Pièces d'identité des deux époux\n- Extraits d'actes de naissance\n- Certificats de célibat\n- Certificats de résidence\n\nللزواج المدني ستحتاج إلى:\n- استمارة الطلب\n- بطاقات التعريف للزوجين\n- نسخ عقود الازدياد\n- شهادات العزوبة\n- شهادات السكنى",
                'religieux': "Pour un mariage religieux, vous aurez besoin de :\n- Formulaire de demande\n- Pièces d'identité des deux époux\n- Extraits d'actes de naissance\n- Certificats de célibat\n- Autorisation religieuse\n\nللزواج الديني ستحتاج إلى:\n- استمارة الطلب\n- بطاقات التعريف للزوجين\n- نسخ عقود الازدياد\n- شهادات العزوبة\n- إذن ديني",
                'default': "Je vais vous aider avec votre demande de mariage. S'agit-il d'un mariage civil ou religieux ?\n\nسأساعدك في طلب الزواج. هل هو زواج مدني أم ديني؟"
            }
        },
        'taxes': {
            1: {
                'taxe foncière': "Pour payer la taxe foncière, vous aurez besoin de :\n- Avis d'imposition\n- Pièce d'identité\n- Moyen de paiement\n\nلدفع الضريبة العقارية ستحتاج إلى:\n- إشعار الضريبة\n- بطاقة التعريف\n- وسيلة الدفع",
                'taxe d\'habitation': "Pour payer la taxe d'habitation, vous aurez besoin de :\n- Avis d'imposition\n- Pièce d'identité\n- Justificatif de domicile\n\nلدفع ضريبة السكن ستحتاج إلى:\n- إشعار الضريبة\n- بطاقة التعريف\n- وثيقة العنوان",
                'default': "Je vais vous aider avec le paiement des taxes. Quel type de taxes souhaitez-vous payer ?\n\nسأساعدك في دفع الضرائب. ما نوع الضرائب التي تريد دفعها؟"
            }
        },
        'business': {
            1: {
                'restaurant': "Pour ouvrir un restaurant, vous aurez besoin de :\n- Licence d'exploitation\n- Autorisation sanitaire\n- Plan de localisation\n- Contrat de location\n\nلفتح مطعم ستحتاج إلى:\n- رخصة الاستغلال\n- إذن صحي\n- خريطة الموقع\n- عقد الإيجار",
                'boutique': "Pour ouvrir une boutique, vous aurez besoin de :\n- Licence commerciale\n- Plan de localisation\n- Contrat de location\n- Extrait du registre de commerce\n\nلفتح متجر ستحتاج إلى:\n- رخصة تجارية\n- خريطة الموقع\n- عقد الإيجار\n- نسخة من السجل التجاري",
                'default': "Je vais vous aider avec l'ouverture de votre commerce. Quel type de commerce souhaitez-vous ouvrir ?\n\nسأساعدك في فتح محل تجاري. ما نوع المحل التجاري الذي تريد فتحه؟"
            }
        },
        'appointment': {
            1: {
                'acte de naissance': "Pour un rendez-vous pour un acte de naissance, vous aurez besoin de :\n- Pièce d'identité\n- Informations sur la naissance\n\nلموعد عقد الازدياد ستحتاج إلى:\n- بطاقة التعريف\n- معلومات الازدياد",
                'carte d\'identité': "Pour un rendez-vous pour une carte d'identité, vous aurez besoin de :\n- Extrait d'acte de naissance\n- Photos d'identité\n\nلموعد البطاقة الوطنية ستحتاج إلى:\n- نسخة عقد الازدياد\n- صور فوتوغرافية",
                'default': "Je vais vous aider à prendre un rendez-vous. Pour quel service souhaitez-vous un rendez-vous ?\n\nسأساعدك في حجز موعد. ما الخدمة التي تريد موعداً لها؟"
            }
        }
    }
    
    step_responses = responses.get(intent, {}).get(step)
    if not step_responses:
        return None
    
    normalized_input = user_input.lower()
    
    # Check for specific keywords in user response
    for key, response in step_responses.items():
        if key != 'default' and key in normalized_input:
            return response
    
    return step_responses.get('default')

def get_conversation_buttons(intent, step):
    button_configs = {
        'birth_certificate': {
            1: [
                {"text": "Extrait simple", "value": "Extrait simple"},
                {"text": "Copie intégrale", "value": "Copie intégrale"},
                {"text": "Avec mentions", "value": "Acte avec mentions marginales"}
            ]
        },
        'national_id': {
            1: [
                {"text": "Première demande", "value": "Première demande"},
                {"text": "Renouvellement", "value": "Renouvellement"}
            ]
        },
        'passport': {
            1: [
                {"text": "Première demande", "value": "Première demande"},
                {"text": "Renouvellement", "value": "Renouvellement"}
            ]
        },
        'residence_certificate': {
            1: [
                {"text": "Oui", "value": "Oui"},
                {"text": "Non", "value": "Non"}
            ]
        },
        'marriage': {
            1: [
                {"text": "Civil", "value": "Civil"},
                {"text": "Religieux", "value": "Religieux"}
            ]
        },
        'taxes': {
            1: [
                {"text": "Taxe foncière", "value": "Taxe foncière"},
                {"text": "Taxe habitation", "value": "Taxe d'habitation"}
            ]
        },
        'business': {
            1: [
                {"text": "Restaurant", "value": "Restaurant"},
                {"text": "Boutique", "value": "Boutique"}
            ]
        },
        'appointment': {
            1: [
                {"text": "Acte naissance", "value": "Acte de naissance"},
                {"text": "Carte identité", "value": "Carte d'identité"}
            ]
        }
    }
    
    return button_configs.get(intent, {}).get(step, [])

# ===== CHATBOT FUNCTIONS =====
def find_answer(question, session_id):
    normalized = question.strip().lower()
    
    # Get or create conversation state for this session
    if session_id not in conversation_states:
        conversation_states[session_id] = {
            "current_intent": None,
            "current_step": None,
            "user_info": {},
            "context": []
        }
    
    conversation_state = conversation_states[session_id]
    
    # Greeting detection
    greetings = [
        "bonjour", "salam", "salut", "hello", "hi", "bonsoir", 
        "السلام عليكم", "سلام", "اهلا", "أهلا", "اهلا وسهلا", "أهلا وسهلا"
    ]
    for greet in greetings:
        if normalized == greet or normalized.startswith(greet + ' ') or normalized.endswith(' ' + greet):
            # Reset conversation state for new conversation
            conversation_states[session_id] = {
                "current_intent": None,
                "current_step": None,
                "user_info": {},
                "context": []
            }
            return {
                "answer": """<div class="answer-section">
    <div class="french-section">
        <h4>👋 Bienvenue !</h4>
        <p>Comment puis-je vous aider aujourd'hui ?</p>
        <p>Je peux vous informer sur :</p>
        <ul>
            <li>Les documents administratifs</li>
            <li>Les horaires d'ouverture</li>
            <li>Les services en ligne</li>
            <li>Les procédures municipales</li>
        </ul>
    </div>
    <div class="arabic-section">
        <h4>👋 مرحباً !</h4>
        <p>كيف يمكنني مساعدتك اليوم؟</p>
        <p>يمكنني إعلامك بـ :</p>
        <ul>
            <li>الوثائق الإدارية</li>
            <li>أوقات العمل</li>
            <li>الخدمات الإلكترونية</li>
            <li>الإجراءات الجماعية</li>
        </ul>
    </div>
</div>""",
                "buttons": [],
                "in_conversation": False
            }
    
    # Goodbye/thanks detection
    goodbyes = [
        "merci", "thank you", "thanks", "au revoir", "bye", "goodbye", 
        "شكرا", "شكرًا", "شكرا جزيلا", "الى اللقاء", "إلى اللقاء", "مع السلامة", "باي", "باي باي"
    ]
    for bye in goodbyes:
        if bye in normalized:
            # Reset conversation state
            conversation_states[session_id] = {
                "current_intent": None,
                "current_step": None,
                "user_info": {},
                "context": []
            }
            return {
                "answer": """<div class="answer-section">
    <div class="french-section">
        <h4>👋 Merci pour votre visite !</h4>
        <p>N'hésitez pas à revenir si vous avez d'autres questions.</p>
        <p><strong>Horaires d'ouverture :</strong> 8h00 - 16h00 (Lun-Ven)</p>
        <p><strong>Contact :</strong> 05 35 62 56 95</p>
    </div>
    <div class="arabic-section">
        <h4>👋 شكراً لزيارتكم !</h4>
        <p>لا تتردد في العودة إذا كان لديك أي أسئلة أخرى.</p>
        <p><strong>أوقات العمل :</strong> 8:00 صباحاً - 4:00 مساءً (الاثنين-الجمعة)</p>
        <p><strong>الاتصال :</strong> 05 35 62 56 95</p>
    </div>
</div>""",
                "buttons": [],
                "in_conversation": False
            }
    
    # Check if we're in an ongoing conversation
    if conversation_state["current_intent"] and conversation_state["current_step"]:
        step_response = process_conversation_step(question, conversation_state["current_intent"], conversation_state["current_step"])
        if step_response:
            # Check if this is a complete response (not the default)
            responses = {
                'birth_certificate': ['extrait simple', 'copie intégrale', 'acte avec mentions marginales'],
                'national_id': ['première demande', 'renouvellement'],
                'passport': ['première demande', 'renouvellement'],
                'residence_certificate': ['oui', 'non'],
                'marriage': ['civil', 'religieux'],
                'taxes': ['taxe foncière', 'taxe d\'habitation'],
                'business': ['restaurant', 'boutique'],
                'appointment': ['acte de naissance', 'carte d\'identité']
            }
            
            valid_responses = responses.get(conversation_state["current_intent"], [])
            is_complete_response = any(response in normalized for response in valid_responses)
            
            if is_complete_response:
                # End conversation flow with complete information
                conversation_states[session_id] = {
                    "current_intent": None,
                    "current_step": None,
                    "user_info": {},
                    "context": []
                }
                return {
                    "answer": step_response + "\n\nAvez-vous d'autres questions ?\nهل لديك أسئلة أخرى؟",
                    "buttons": [],
                    "in_conversation": False
                }
            else:
                # Move to next step or end conversation
                next_step = conversation_state["current_step"] + 1
                next_follow_up = get_follow_up_question(conversation_state["current_intent"], next_step)
                
                if next_follow_up:
                    conversation_state["current_step"] = next_step
                    return {
                        "answer": step_response + "\n\n" + next_follow_up,
                        "buttons": get_conversation_buttons(conversation_state["current_intent"], next_step),
                        "in_conversation": True
                    }
                else:
                    # End conversation flow
                    conversation_states[session_id] = {
                        "current_intent": None,
                        "current_step": None,
                        "user_info": {},
                        "context": []
                    }
                    return {
                        "answer": step_response + "\n\nAvez-vous d'autres questions ?\nهل لديك أسئلة أخرى؟",
                        "buttons": [],
                        "in_conversation": False
                    }
    
    # Intent recognition for new questions
    intent = recognize_intent(question)
    
    if intent["confidence"] > 0.7 and intent["requires_follow_up"]:
        # Start conversation flow
        conversation_state["current_intent"] = intent["intent"]
        conversation_state["current_step"] = 1
        follow_up = get_follow_up_question(intent["intent"], 1)
        
        if follow_up:
            return {
                "answer": follow_up,
                "buttons": get_conversation_buttons(intent["intent"], 1),
                "in_conversation": True
            }
    
    # Search for matching Q&A pairs (fallback)
    for pair in qa_pairs:
        for q in pair["questions"]:
            if q in normalized:
                # Add follow-up question for document-related queries
                answer = pair["answer"]
                if intent["confidence"] > 0.7 and intent["requires_follow_up"]:
                    return {
                        "answer": answer + "\n\nAvez-vous besoin d'aide pour préparer les documents requis ?\nهل تحتاج مساعدة في تحضير الوثائق المطلوبة؟",
                        "buttons": [],
                        "in_conversation": False
                    }
                return {
                    "answer": answer,
                    "buttons": [],
                    "in_conversation": False
                }
    
    return {
        "answer": """<div class="answer-section">
    <div class="french-section">
        <h4>❓ Question non comprise</h4>
        <p>Désolé, je n'ai pas compris votre question. Veuillez reformuler.</p>
        <p>Vous pouvez me demander :</p>
        <ul>
            <li>Des informations sur les documents</li>
            <li>Les horaires d'ouverture</li>
            <li>L'adresse de la mairie</li>
            <li>Les services disponibles</li>
        </ul>
    </div>
    <div class="arabic-section">
        <h4>❓ سؤال غير مفهوم</h4>
        <p>عذراً، لم أفهم سؤالك. يرجى إعادة الصياغة.</p>
        <p>يمكنك أن تسألني عن :</p>
        <ul>
            <li>معلومات عن الوثائق</li>
            <li>أوقات العمل</li>
            <li>عنوان الجماعة</li>
            <li>الخدمات المتوفرة</li>
        </ul>
    </div>
</div>""",
        "buttons": [],
        "in_conversation": False
    }

# ===== SESSION MANAGEMENT =====
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_user_preferences(session_id):
    if session_id not in user_preferences:
        user_preferences[session_id] = {
            'theme': 'dark',
            'font_size': 'normal'
        }
    return user_preferences[session_id]

def get_theme_icon(theme):
    return '☀️' if theme == 'light' else '🌙'

def get_font_size_icon(font_size):
    icons = {
        'normal': '📝',
        'large': '🔍',
        'xlarge': '🔎'
    }
    return icons.get(font_size, '📝')

def get_font_size_tooltip(font_size):
    tooltips = {
        'normal': 'Taille de police: Normale (Cliquez pour grande)',
        'large': 'Taille de police: Grande (Cliquez pour très grande)',
        'xlarge': 'Taille de police: Très grande (Cliquez pour normale)'
    }
    return tooltips.get(font_size, 'Taille de police: Normale (Cliquez pour grande)')

# ===== ROUTES =====
@app.route('/')
def index():
    session_id = get_session_id()
    prefs = get_user_preferences(session_id)
    
    # Get chat history from session
    chat_history = session.get('chat_history', [])
    
    return render_template('index.html',
                         session_id=session_id,
                         chat_history=chat_history,
                         in_conversation=False,
                         conversation_buttons=[],
                         theme=prefs['theme'],
                         font_size=prefs['font_size'],
                         theme_icon=get_theme_icon(prefs['theme']),
                         font_size_icon=get_font_size_icon(prefs['font_size']),
                         font_size_tooltip=get_font_size_tooltip(prefs['font_size']))

@app.route('/chat', methods=['POST'])
def chat():
    session_id = get_session_id()
    question = request.form.get('question', '')
    
    if not question.strip():
        return redirect(url_for('index'))
    
    # Get response from chatbot
    response = find_answer(question, session_id)
    
    # Update chat history in session
    chat_history = session.get('chat_history', [])
    chat_history.append({
        'sender': 'user',
        'text': question,
        'timestamp': datetime.now().isoformat()
    })
    chat_history.append({
        'sender': 'bot',
        'text': response['answer'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 20 messages
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    
    session['chat_history'] = chat_history
    
    # Get user preferences
    prefs = get_user_preferences(session_id)
    
    return render_template('index.html',
                         session_id=session_id,
                         chat_history=chat_history,
                         in_conversation=response['in_conversation'],
                         conversation_buttons=response['buttons'],
                         theme=prefs['theme'],
                         font_size=prefs['font_size'],
                         theme_icon=get_theme_icon(prefs['theme']),
                         font_size_icon=get_font_size_icon(prefs['font_size']),
                         font_size_tooltip=get_font_size_tooltip(prefs['font_size']))

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session_id = get_session_id()
    
    # Clear chat history
    session['chat_history'] = []
    
    # Clear conversation state
    if session_id in conversation_states:
        del conversation_states[session_id]
    
    return redirect(url_for('index'))

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    session_id = get_session_id()
    prefs = get_user_preferences(session_id)
    
    # Toggle theme
    prefs['theme'] = 'light' if prefs['theme'] == 'dark' else 'dark'
    
    return redirect(url_for('index'))

@app.route('/toggle_font_size', methods=['POST'])
def toggle_font_size():
    session_id = get_session_id()
    prefs = get_user_preferences(session_id)
    
    # Cycle through font sizes
    sizes = ['normal', 'large', 'xlarge']
    current_index = sizes.index(prefs['font_size'])
    next_index = (current_index + 1) % len(sizes)
    prefs['font_size'] = sizes[next_index]
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 