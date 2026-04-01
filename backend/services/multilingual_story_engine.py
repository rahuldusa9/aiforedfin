"""
AI FOR EDUCATION – Multilingual Story Generation Engine
Advanced story generation with prosody markers, emotional depth,
and support for 25+ languages. Creates immersive educational narratives.
"""

import logging
import json
import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum

from services.gemini_service import generate_text
from services.prosody_engine import (
    ProsodyEngine, get_prosody_engine, EmotionType, ProsodySettings
)
from services.multilingual_voices import (
    get_storyteller_voice, get_narrator_voice, is_language_supported,
    LANGUAGE_NAMES, detect_language_from_text
)

logger = logging.getLogger(__name__)


class StoryGenre(Enum):
    """Story genres with different narrative styles."""
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    SCIENCE = "science"
    HISTORY = "history"
    FANTASY = "fantasy"
    BIOGRAPHY = "biography"
    FABLE = "fable"
    EDUCATIONAL = "educational"


class AgeGroup(Enum):
    """Target age groups affecting vocabulary and complexity."""
    CHILDREN = "children"       # Ages 5-8
    KIDS = "kids"               # Ages 9-12
    TEENS = "teens"            # Ages 13-17
    ADULTS = "adults"          # Ages 18+


@dataclass
class StoryConfig:
    """Configuration for story generation."""
    language: str = "en"
    genre: StoryGenre = StoryGenre.EDUCATIONAL
    age_group: AgeGroup = AgeGroup.KIDS
    word_count: int = 500
    include_dialogue: bool = True
    emotional_depth: str = "moderate"  # light, moderate, deep
    prosody_markers: bool = True
    cultural_adaptation: bool = True


# -------------------------------------------------------
# Language-Specific Story Prompts - Short & Spicy!
# -------------------------------------------------------
STORY_PROMPTS = {
    "en": """Write a SHORT, PUNCHY educational story about "{topic}" in English.

STYLE: Fast-paced, exciting, dramatic!

REQUIREMENTS:
- {word_count} words MAX - be concise!
- 3-4 paragraphs only
- Start with ACTION or DRAMA - hook instantly
- 2-3 quick dialogue exchanges
- EXCITING - vivid verbs, short punchy sentences
- End with a twist or revelation about {topic}

TONE:
- Energetic and dynamic
- Short sentences for tension: "She gasped. The answer was right there."
- Use "..." for dramatic pauses
- Use "!" for excitement

STRUCTURE:
1. HOOK (2-3 sentences): Start mid-action or mystery
2. ADVENTURE (1-2 paragraphs): Quick discovery of {topic}
3. CLIMAX (1 paragraph): Dramatic revelation + lesson

TARGET: {age_group}, GENRE: {genre}

NO titles. Jump into action!""",

    "es": """Escribe una historia educativa CORTA y EMOCIONANTE sobre "{topic}" en español.

ESTILO: Ritmo rápido, emocionante, dramático!

REQUISITOS:
- {word_count} palabras MÁXIMO
- Solo 3-4 párrafos
- Comienza con ACCIÓN o DRAMA
- 2-3 intercambios de diálogo rápidos
- EMOCIONANTE - verbos vívidos, oraciones cortas
- Termina con un giro o revelación sobre {topic}

TONO:
- Energético y dinámico
- Oraciones cortas para tensión
- Usa "..." para pausas dramáticas
- Usa "¡!" para emoción

ESTRUCTURA:
1. GANCHO (2-3 oraciones): Acción o misterio
2. AVENTURA (1-2 párrafos): Descubrimiento de {topic}
3. CLÍMAX (1 párrafo): Revelación + lección

PÚBLICO: {age_group}, GÉNERO: {genre}

Sin títulos. ¡Directo a la acción!""",

    "fr": """Écris une histoire éducative COURTE et PALPITANTE sur "{topic}" en français.

STYLE: Rythme rapide, excitant, dramatique!

EXIGENCES:
- {word_count} mots MAXIMUM
- Seulement 3-4 paragraphes
- Commence par ACTION ou DRAME
- 2-3 échanges de dialogue rapides
- EXCITANT - verbes vifs, phrases courtes
- Termine avec une révélation sur {topic}

TON:
- Énergique et dynamique
- Phrases courtes pour la tension
- Utilise "..." pour les pauses dramatiques
- Utilise "!" pour l'excitation

STRUCTURE:
1. ACCROCHE (2-3 phrases): Action ou mystère
2. AVENTURE (1-2 paragraphes): Découverte de {topic}
3. CLIMAX (1 paragraphe): Révélation + leçon

PUBLIC: {age_group}, GENRE: {genre}

Pas de titres. Directement dans l'action!""",

    "de": """Schreibe eine KURZE, SPANNENDE Bildungsgeschichte über "{topic}" auf Deutsch.

STIL: Schnell, aufregend, dramatisch!

ANFORDERUNGEN:
- {word_count} Wörter MAXIMUM
- Nur 3-4 Absätze
- Beginne mit ACTION oder DRAMA
- 2-3 schnelle Dialoge
- SPANNEND - lebhafte Verben, kurze Sätze
- Ende mit Enthüllung über {topic}

TON:
- Energisch und dynamisch
- Kurze Sätze für Spannung
- Verwende "..." für dramatische Pausen
- Verwende "!" für Aufregung

STRUKTUR:
1. HOOK (2-3 Sätze): Aktion oder Geheimnis
2. ABENTEUER (1-2 Absätze): Entdeckung von {topic}
3. HÖHEPUNKT (1 Absatz): Enthüllung + Lektion

PUBLIKUM: {age_group}, GENRE: {genre}

Keine Titel. Direkt in die Action!""",

    "zh": """用中文写一个关于"{topic}"的简短刺激的教育故事。

风格：节奏快、刺激、戏剧性！

要求：
- 最多{word_count}字
- 只要3-4段
- 以动作或戏剧开始
- 2-3个快速对话
- 刺激 - 生动动词，短句
- 以关于{topic}的揭示结尾

语气：
- 充满活力
- 短句制造紧张感
- 用"……"表示戏剧性停顿
- 用"！"表示兴奋

结构：
1. 钩子（2-3句）：动作或悬念
2. 冒险（1-2段）：发现{topic}
3. 高潮（1段）：揭示+教训

受众：{age_group}，类型：{genre}

不要标题。直接开始！""",

    "ja": """「{topic}」についての短くてエキサイティングな教育ストーリーを日本語で書いてください。

スタイル：テンポが速く、刺激的、ドラマチック！

要件：
- 最大{word_count}語
- 3-4段落のみ
- アクションかドラマで始める
- 2-3の素早い対話
- エキサイティング - 生き生きとした動詞、短い文
- {topic}についての驚きの結末

トーン：
- エネルギッシュでダイナミック
- 緊張感のための短い文
- 「……」でドラマチックな間
- 「！」で興奮

構造：
1. フック（2-3文）：アクションか謎
2. 冒険（1-2段落）：{topic}の発見
3. クライマックス（1段落）：啓示+教訓

対象：{age_group}、ジャンル：{genre}

タイトルなし。すぐにアクション開始！""",

    "ko": """"{topic}"에 대한 짧고 흥미진진한 교육 이야기를 한국어로 쓰세요.

스타일: 빠른 템포, 흥미진진, 드라마틱!

요구 사항:
- 최대 {word_count}단어
- 3-4단락만
- 액션이나 드라마로 시작
- 2-3개의 빠른 대화
- 흥미진진 - 생생한 동사, 짧은 문장
- {topic}에 대한 반전으로 끝

톤:
- 에너지 넘치고 역동적
- 긴장감을 위한 짧은 문장
- "..."로 극적인 멈춤
- "!"로 흥분

구조:
1. 후크 (2-3문장): 액션이나 미스터리
2. 모험 (1-2단락): {topic} 발견
3. 클라이맥스 (1단락): 깨달음 + 교훈

대상: {age_group}, 장르: {genre}

제목 없이. 바로 액션 시작!""",

    "hi": """"{topic}" के बारे में एक छोटी, रोमांचक शैक्षिक कहानी हिंदी में लिखें।

शैली: तेज गति, रोमांचक, नाटकीय!

आवश्यकताएं:
- अधिकतम {word_count} शब्द
- केवल 3-4 पैराग्राफ
- एक्शन या ड्रामा से शुरू करें
- 2-3 त्वरित संवाद
- रोमांचक - जीवंत क्रियाएं, छोटे वाक्य
- {topic} के बारे में खुलासे के साथ समाप्त

टोन:
- ऊर्जावान और गतिशील
- तनाव के लिए छोटे वाक्य
- नाटकीय विराम के लिए "..."
- उत्साह के लिए "!"

संरचना:
1. हुक (2-3 वाक्य): एक्शन या रहस्य
2. साहसिक (1-2 पैराग्राफ): {topic} की खोज
3. चरमोत्कर्ष (1 पैराग्राफ): खुलासा + सबक

दर्शक: {age_group}, शैली: {genre}

कोई शीर्षक नहीं। सीधे एक्शन में!""",

    "ar": """اكتب قصة تعليمية قصيرة ومثيرة عن "{topic}" بالعربية.

الأسلوب: سريع الإيقاع، مثير، درامي!

المتطلبات:
- {word_count} كلمة كحد أقصى
- 3-4 فقرات فقط
- ابدأ بالحركة أو الدراما
- 2-3 حوارات سريعة
- مثير - أفعال حية، جمل قصيرة
- انتهِ بكشف عن {topic}

النبرة:
- نشيط وديناميكي
- جمل قصيرة للتوتر
- "..." للتوقفات الدرامية
- "!" للإثارة

الهيكل:
1. الخطاف (2-3 جمل): حركة أو لغز
2. المغامرة (1-2 فقرة): اكتشاف {topic}
3. الذروة (فقرة): كشف + درس

الجمهور: {age_group}، النوع: {genre}

بدون عناوين. ابدأ مباشرة!""",

    "pt": """Escreva uma história educacional CURTA e EMOCIONANTE sobre "{topic}" em português.

ESTILO: Ritmo rápido, emocionante, dramático!

REQUISITOS:
- {word_count} palavras MÁXIMO
- Apenas 3-4 parágrafos
- Comece com AÇÃO ou DRAMA
- 2-3 diálogos rápidos
- EMOCIONANTE - verbos vívidos, frases curtas
- Termine com revelação sobre {topic}

TOM:
- Energético e dinâmico
- Frases curtas para tensão
- Use "..." para pausas dramáticas
- Use "!" para emoção

ESTRUTURA:
1. GANCHO (2-3 frases): Ação ou mistério
2. AVENTURA (1-2 parágrafos): Descoberta de {topic}
3. CLÍMAX (1 parágrafo): Revelação + lição

PÚBLICO: {age_group}, GÊNERO: {genre}

Sem títulos. Direto na ação!""",

    "ru": """Напиши КОРОТКУЮ, ЗАХВАТЫВАЮЩУЮ образовательную историю о "{topic}" на русском.

СТИЛЬ: Быстрый темп, захватывающий, драматичный!

ТРЕБОВАНИЯ:
- Максимум {word_count} слов
- Только 3-4 абзаца
- Начни с ДЕЙСТВИЯ или ДРАМЫ
- 2-3 быстрых диалога
- ЗАХВАТЫВАЮЩЕ - яркие глаголы, короткие предложения
- Закончи откровением о {topic}

ТОН:
- Энергичный и динамичный
- Короткие предложения для напряжения
- "..." для драматических пауз
- "!" для волнения

СТРУКТУРА:
1. КРЮЧОК (2-3 предложения): Действие или тайна
2. ПРИКЛЮЧЕНИЕ (1-2 абзаца): Открытие {topic}
3. КУЛЬМИНАЦИЯ (1 абзац): Откровение + урок

АУДИТОРИЯ: {age_group}, ЖАНР: {genre}

Без заголовков. Сразу в действие!""",

    "it": """Scrivi una storia educativa BREVE ed EMOZIONANTE su "{topic}" in italiano.

STILE: Ritmo veloce, emozionante, drammatico!

REQUISITI:
- {word_count} parole MASSIMO
- Solo 3-4 paragrafi
- Inizia con AZIONE o DRAMMA
- 2-3 dialoghi veloci
- EMOZIONANTE - verbi vividi, frasi brevi
- Termina con rivelazione su {topic}

TONO:
- Energico e dinamico
- Frasi brevi per tensione
- "..." per pause drammatiche
- "!" per eccitazione

STRUTTURA:
1. GANCIO (2-3 frasi): Azione o mistero
2. AVVENTURA (1-2 paragrafi): Scoperta di {topic}
3. CLIMAX (1 paragrafo): Rivelazione + lezione

PUBBLICO: {age_group}, GENERE: {genre}

Niente titoli. Dritto all'azione!""",

    # ============== DUTCH ==============
    "nl": """Schrijf een KORT, SPANNEND educatief verhaal over "{topic}" in het Nederlands.

STIJL: Snel tempo, spannend, dramatisch!

VEREISTEN:
- {word_count} woorden MAXIMUM
- Slechts 3-4 paragrafen
- Begin met ACTIE of DRAMA
- 2-3 snelle dialogen
- SPANNEND - levendige werkwoorden, korte zinnen
- Eindig met een onthulling over {topic}

TOON:
- Energiek en dynamisch
- Korte zinnen voor spanning
- "..." voor dramatische pauzes
- "!" voor opwinding

STRUCTUUR:
1. HAAK (2-3 zinnen): Actie of mysterie
2. AVONTUUR (1-2 paragrafen): Ontdekking van {topic}
3. CLIMAX (1 paragraaf): Onthulling + les

DOELGROEP: {age_group}, GENRE: {genre}

Geen titels. Direct actie!""",

    # ============== POLISH ==============
    "pl": """Napisz KRÓTKĄ, EKSCYTUJĄCĄ historię edukacyjną o "{topic}" po polsku.

STYL: Szybkie tempo, ekscytujący, dramatyczny!

WYMAGANIA:
- {word_count} słów MAKSYMALNIE
- Tylko 3-4 akapity
- Zacznij od AKCJI lub DRAMATU
- 2-3 szybkie dialogi
- EKSCYTUJĄCE - żywe czasowniki, krótkie zdania
- Zakończ odkryciem o {topic}

TON:
- Energiczny i dynamiczny
- Krótkie zdania dla napięcia
- "..." dla dramatycznych pauz
- "!" dla emocji

STRUKTURA:
1. HACZYK (2-3 zdania): Akcja lub tajemnica
2. PRZYGODA (1-2 akapity): Odkrycie {topic}
3. KULMINACJA (1 akapit): Objawienie + lekcja

ODBIORCY: {age_group}, GATUNEK: {genre}

Bez tytułów. Prosto do akcji!""",

    # ============== TURKISH ==============
    "tr": """"{topic}" hakkında KISA, HEYECANLI bir eğitici hikaye Türkçe yaz.

STİL: Hızlı tempo, heyecan verici, dramatik!

GEREKSİNİMLER:
- MAKSİMUM {word_count} kelime
- Sadece 3-4 paragraf
- AKSİYON veya DRAMA ile başla
- 2-3 hızlı diyalog
- HEYECANLI - canlı fiiller, kısa cümleler
- {topic} hakkında bir açıklama ile bitir

TON:
- Enerjik ve dinamik
- Gerilim için kısa cümleler
- Dramatik duraklamalar için "..."
- Heyecan için "!"

YAPI:
1. KANCA (2-3 cümle): Aksiyon veya gizem
2. MACERA (1-2 paragraf): {topic}'ın keşfi
3. DORUK (1 paragraf): Açıklama + ders

HEDEF KİTLE: {age_group}, TÜR: {genre}

Başlık yok. Doğrudan aksiyona!""",

    # ============== VIETNAMESE ==============
    "vi": """Viết một câu chuyện giáo dục NGẮN, HẤP DẪN về "{topic}" bằng tiếng Việt.

PHONG CÁCH: Nhịp độ nhanh, hấp dẫn, kịch tính!

YÊU CẦU:
- TỐI ĐA {word_count} từ
- Chỉ 3-4 đoạn văn
- Bắt đầu bằng HÀNH ĐỘNG hoặc KỊCH TÍNH
- 2-3 đoạn hội thoại nhanh
- HẤP DẪN - động từ sống động, câu ngắn
- Kết thúc với sự tiết lộ về {topic}

GIỌNG ĐIỆU:
- Năng động và sôi nổi
- Câu ngắn tạo căng thẳng
- "..." cho những khoảng dừng kịch tính
- "!" cho sự phấn khích

CẤU TRÚC:
1. MỞ ĐẦU (2-3 câu): Hành động hoặc bí ẩn
2. PHIÊU LƯU (1-2 đoạn): Khám phá {topic}
3. CAO TRÀO (1 đoạn): Tiết lộ + bài học

ĐỐI TƯỢNG: {age_group}, THỂ LOẠI: {genre}

Không tiêu đề. Bắt đầu ngay!""",

    # ============== THAI ==============
    "th": """เขียนเรื่องสั้นการศึกษาที่สั้นและน่าตื่นเต้นเกี่ยวกับ "{topic}" เป็นภาษาไทย

สไตล์: จังหวะเร็ว น่าตื่นเต้น ดราม่า!

ข้อกำหนด:
- สูงสุด {word_count} คำ
- เพียง 3-4 ย่อหน้า
- เริ่มด้วยแอคชั่นหรือดราม่า
- บทสนทนาสั้น 2-3 บท
- ตื่นเต้น - คำกริยาสดใส ประโยคสั้น
- จบด้วยการเปิดเผยเกี่ยวกับ {topic}

โทน:
- มีพลังและไดนามิก
- ประโยคสั้นสร้างความตึงเครียด
- "..." สำหรับการหยุดที่ดราม่า
- "!" สำหรับความตื่นเต้น

โครงสร้าง:
1. เปิดเรื่อง (2-3 ประโยค): แอคชั่นหรือปริศนา
2. การผจญภัย (1-2 ย่อหน้า): ค้นพบ {topic}
3. ไคลแม็กซ์ (1 ย่อหน้า): การเปิดเผย + บทเรียน

กลุ่มเป้าหมาย: {age_group}, ประเภท: {genre}

ไม่มีชื่อเรื่อง เริ่มเลย!""",

    # ============== INDONESIAN ==============
    "id": """Tulis cerita pendidikan yang PENDEK dan SERU tentang "{topic}" dalam Bahasa Indonesia.

GAYA: Tempo cepat, seru, dramatis!

PERSYARATAN:
- MAKSIMAL {word_count} kata
- Hanya 3-4 paragraf
- Mulai dengan AKSI atau DRAMA
- 2-3 dialog cepat
- SERU - kata kerja yang hidup, kalimat pendek
- Akhiri dengan pengungkapan tentang {topic}

NADA:
- Energik dan dinamis
- Kalimat pendek untuk ketegangan
- "..." untuk jeda dramatis
- "!" untuk kegembiraan

STRUKTUR:
1. PENGAIT (2-3 kalimat): Aksi atau misteri
2. PETUALANGAN (1-2 paragraf): Penemuan {topic}
3. KLIMAKS (1 paragraf): Pengungkapan + pelajaran

TARGET: {age_group}, GENRE: {genre}

Tanpa judul. Langsung aksi!""",
}


class MultilingualStoryEngine:
    """
    Advanced multilingual story generation engine with prosody support.
    Generates educational narratives in 25+ languages with natural
    speech markers for expressive TTS rendering.
    """

    def __init__(self):
        self.prosody_engine = get_prosody_engine()
        self.default_config = StoryConfig()

    def _get_prompt_for_language(self, language: str) -> str:
        """Get the appropriate story prompt template for a language."""
        lang_code = language.lower().split('-')[0]

        # If we have a native prompt for this language, use it
        if lang_code in STORY_PROMPTS:
            return STORY_PROMPTS[lang_code]

        # For other languages, create a dynamic prompt that explicitly requests
        # the story to be written in the target language
        lang_name = LANGUAGE_NAMES.get(lang_code, language.upper())
        return f"""Write a SHORT, PUNCHY educational story about "{{topic}}" in {lang_name} language.

IMPORTANT: Write the ENTIRE story in {lang_name}. Do NOT write in English.

STYLE: Fast-paced, exciting, dramatic!

REQUIREMENTS:
- {{word_count}} words MAX - be concise!
- 3-4 paragraphs only
- Start with ACTION or DRAMA - hook instantly
- 2-3 quick dialogue exchanges
- EXCITING - vivid verbs, short punchy sentences
- End with a twist or revelation about {{topic}}

TONE:
- Energetic and dynamic
- Short sentences for tension
- Use "..." for dramatic pauses
- Use "!" for excitement

STRUCTURE:
1. HOOK (2-3 sentences): Start mid-action or mystery
2. ADVENTURE (1-2 paragraphs): Quick discovery of {{topic}}
3. CLIMAX (1 paragraph): Dramatic revelation + lesson

TARGET: {{age_group}}, GENRE: {{genre}}

NO titles. Write everything in {lang_name}!"""

    def _translate_age_group(self, age_group: AgeGroup, language: str) -> str:
        """Translate age group description for the prompt."""
        translations = {
            "en": {
                AgeGroup.CHILDREN: "ages 5-8 (simple vocabulary, short sentences)",
                AgeGroup.KIDS: "ages 9-12 (moderate vocabulary)",
                AgeGroup.TEENS: "ages 13-17 (advanced vocabulary)",
                AgeGroup.ADULTS: "adults (sophisticated vocabulary)",
            },
            "es": {
                AgeGroup.CHILDREN: "edades 5-8 (vocabulario simple)",
                AgeGroup.KIDS: "edades 9-12 (vocabulario moderado)",
                AgeGroup.TEENS: "edades 13-17 (vocabulario avanzado)",
                AgeGroup.ADULTS: "adultos (vocabulario sofisticado)",
            },
            "fr": {
                AgeGroup.CHILDREN: "âges 5-8 (vocabulaire simple)",
                AgeGroup.KIDS: "âges 9-12 (vocabulaire modéré)",
                AgeGroup.TEENS: "âges 13-17 (vocabulaire avancé)",
                AgeGroup.ADULTS: "adultes (vocabulaire sophistiqué)",
            },
            "de": {
                AgeGroup.CHILDREN: "Alter 5-8 (einfaches Vokabular)",
                AgeGroup.KIDS: "Alter 9-12 (mittleres Vokabular)",
                AgeGroup.TEENS: "Alter 13-17 (fortgeschrittenes Vokabular)",
                AgeGroup.ADULTS: "Erwachsene (anspruchsvolles Vokabular)",
            },
            "zh": {
                AgeGroup.CHILDREN: "5-8岁（简单词汇）",
                AgeGroup.KIDS: "9-12岁（中等词汇）",
                AgeGroup.TEENS: "13-17岁（高级词汇）",
                AgeGroup.ADULTS: "成人（复杂词汇）",
            },
            "ja": {
                AgeGroup.CHILDREN: "5-8歳（簡単な語彙）",
                AgeGroup.KIDS: "9-12歳（中程度の語彙）",
                AgeGroup.TEENS: "13-17歳（上級語彙）",
                AgeGroup.ADULTS: "大人（洗練された語彙）",
            },
            "ko": {
                AgeGroup.CHILDREN: "5-8세 (간단한 어휘)",
                AgeGroup.KIDS: "9-12세 (중급 어휘)",
                AgeGroup.TEENS: "13-17세 (고급 어휘)",
                AgeGroup.ADULTS: "성인 (정교한 어휘)",
            },
        }
        lang_code = language.lower().split('-')[0]
        lang_translations = translations.get(lang_code, translations["en"])
        return lang_translations.get(age_group, lang_translations[AgeGroup.KIDS])

    def _translate_genre(self, genre: StoryGenre, language: str) -> str:
        """Translate genre for the prompt."""
        translations = {
            "en": {
                StoryGenre.ADVENTURE: "adventure",
                StoryGenre.MYSTERY: "mystery",
                StoryGenre.SCIENCE: "science fiction",
                StoryGenre.HISTORY: "historical",
                StoryGenre.FANTASY: "fantasy",
                StoryGenre.BIOGRAPHY: "biographical",
                StoryGenre.FABLE: "fable/moral story",
                StoryGenre.EDUCATIONAL: "educational",
            },
            "es": {
                StoryGenre.ADVENTURE: "aventura",
                StoryGenre.MYSTERY: "misterio",
                StoryGenre.SCIENCE: "ciencia ficción",
                StoryGenre.HISTORY: "histórico",
                StoryGenre.FANTASY: "fantasía",
                StoryGenre.BIOGRAPHY: "biográfico",
                StoryGenre.FABLE: "fábula",
                StoryGenre.EDUCATIONAL: "educativo",
            },
            "fr": {
                StoryGenre.ADVENTURE: "aventure",
                StoryGenre.MYSTERY: "mystère",
                StoryGenre.SCIENCE: "science-fiction",
                StoryGenre.HISTORY: "historique",
                StoryGenre.FANTASY: "fantasy",
                StoryGenre.BIOGRAPHY: "biographique",
                StoryGenre.FABLE: "fable",
                StoryGenre.EDUCATIONAL: "éducatif",
            },
        }
        lang_code = language.lower().split('-')[0]
        lang_translations = translations.get(lang_code, translations["en"])
        return lang_translations.get(genre, genre.value)

    def generate_story(
        self,
        topic: str,
        language: str = "en",
        genre: Optional[StoryGenre] = None,
        age_group: Optional[AgeGroup] = None,
        word_count: int = 800,
        include_prosody: bool = True
    ) -> dict:
        """
        Generate a multilingual educational story with prosody markers.

        Args:
            topic: The educational topic for the story
            language: Target language code (e.g., 'en', 'es', 'fr')
            genre: Story genre (defaults to EDUCATIONAL)
            age_group: Target age group (defaults to KIDS)
            word_count: Approximate word count (default 800)
            include_prosody: Whether to add SSML prosody markers

        Returns:
            Dictionary with story_text, ssml_text, language, voice, etc.
        """
        # Set defaults
        if genre is None:
            genre = StoryGenre.EDUCATIONAL
        if age_group is None:
            age_group = AgeGroup.KIDS

        # Short and spicy stories - keep them punchy
        word_count = max(word_count, 300)  # Minimum 300 words

        # Validate language
        lang_code = language.lower().split('-')[0]
        if not is_language_supported(lang_code):
            logger.warning(f"[Story] Language '{language}' not fully supported, using English")
            lang_code = "en"

        # Get prompt template
        prompt_template = self._get_prompt_for_language(lang_code)

        # Build the prompt
        prompt = prompt_template.format(
            topic=topic,
            age_group=self._translate_age_group(age_group, lang_code),
            genre=self._translate_genre(genre, lang_code),
            word_count=word_count
        )

        logger.info(f"[Story] Generating {lang_code} story about '{topic}' ({genre.value}, {age_group.value}, {word_count} words)")

        # Generate story with Gemini - use higher token count for complete stories
        # Tokens ≈ words * 1.5, so for 800 words we need ~1200 tokens minimum
        # We use 5x multiplier to ensure complete output
        max_tokens = max(word_count * 5, 4000)
        story_text = generate_text(prompt, max_tokens=max_tokens)

        # Clean up the story
        story_text = self._clean_story_text(story_text)

        # Get appropriate voice
        voice = get_storyteller_voice(lang_code)

        # Generate SSML if requested
        ssml_text = None
        prosody_settings = None
        if include_prosody:
            ssml_text, prosody_settings = self.prosody_engine.create_expressive_narration(
                story_text, style="storytelling"
            )

        result = {
            "story_text": story_text,
            "ssml_text": ssml_text,
            "language": lang_code,
            "language_name": LANGUAGE_NAMES.get(lang_code, lang_code.upper()),
            "voice": voice,
            "genre": genre.value,
            "age_group": age_group.value,
            "topic": topic,
            "word_count": len(story_text.split()),
            "has_prosody": include_prosody,
        }

        if prosody_settings:
            result["prosody"] = {
                "rate": prosody_settings.rate,
                "pitch": prosody_settings.pitch,
                "volume": prosody_settings.volume,
            }

        logger.info(f"[Story] Generated {result['word_count']} words in {result['language_name']}")

        return result

    def _clean_story_text(self, text: str) -> str:
        """Clean and normalize story text."""
        # Remove any markdown headers
        text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)

        # Remove title-like first lines
        lines = text.strip().split('\n')
        if lines and (lines[0].startswith('#') or lines[0].isupper() or
                     'Title:' in lines[0] or 'Story:' in lines[0]):
            lines = lines[1:]

        # Normalize whitespace
        text = '\n'.join(lines).strip()
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def generate_multilingual_versions(
        self,
        topic: str,
        languages: list[str],
        **kwargs
    ) -> list[dict]:
        """
        Generate the same story in multiple languages.

        Args:
            topic: Educational topic
            languages: List of language codes
            **kwargs: Additional generation parameters

        Returns:
            List of story dictionaries for each language
        """
        results = []
        for lang in languages:
            try:
                story = self.generate_story(topic, language=lang, **kwargs)
                results.append(story)
            except Exception as e:
                logger.error(f"[Story] Failed to generate {lang} version: {e}")
                results.append({
                    "language": lang,
                    "error": str(e)
                })

        return results

    def adapt_story_for_culture(
        self,
        story_text: str,
        source_language: str,
        target_language: str,
        topic: str
    ) -> str:
        """
        Culturally adapt a story from one language/culture to another.
        Not just translation - adapts names, references, and contexts.

        Args:
            story_text: Original story text
            source_language: Source language code
            target_language: Target language code
            topic: Original topic

        Returns:
            Culturally adapted story
        """
        target_lang_name = LANGUAGE_NAMES.get(target_language, target_language)

        prompt = f"""Culturally adapt this story for a {target_lang_name}-speaking audience.

ORIGINAL STORY (about {topic}):
{story_text}

ADAPTATION GUIDELINES:
1. Translate to {target_lang_name}
2. Change character names to culturally appropriate names
3. Adapt cultural references, foods, locations to be familiar
4. Preserve the educational content about {topic}
5. Maintain the story structure and emotional beats
6. Keep prosody markers (... — ! *) in place

Write only the adapted story. No explanations."""

        adapted = generate_text(prompt, max_tokens=len(story_text.split()) * 3)
        return self._clean_story_text(adapted)


# -------------------------------------------------------
# Convenience Functions
# -------------------------------------------------------
_engine = None


def get_story_engine() -> MultilingualStoryEngine:
    """Get or create the global story engine instance."""
    global _engine
    if _engine is None:
        _engine = MultilingualStoryEngine()
        logger.info("[Story] Multilingual story engine initialized")
    return _engine


def generate_multilingual_story(
    topic: str,
    language: str = "en",
    genre: str = "educational",
    age_group: str = "kids",
    word_count: int = 400,
    include_prosody: bool = True
) -> dict:
    """
    Generate a multilingual educational story.

    Args:
        topic: Educational topic
        language: Target language code
        genre: Story genre (adventure, mystery, science, etc.)
        age_group: Target age group (children, kids, teens, adults)
        word_count: Approximate target word count
        include_prosody: Whether to generate SSML with prosody

    Returns:
        Dictionary with story content and metadata
    """
    engine = get_story_engine()

    # Convert string genre to enum
    try:
        genre_enum = StoryGenre(genre.lower())
    except ValueError:
        genre_enum = StoryGenre.EDUCATIONAL

    # Convert string age_group to enum
    try:
        age_enum = AgeGroup(age_group.lower())
    except ValueError:
        age_enum = AgeGroup.KIDS

    return engine.generate_story(
        topic=topic,
        language=language,
        genre=genre_enum,
        age_group=age_enum,
        word_count=word_count,
        include_prosody=include_prosody
    )


def get_supported_languages() -> list[dict]:
    """Get list of supported languages for story generation."""
    from services.multilingual_voices import get_available_languages
    return get_available_languages()
