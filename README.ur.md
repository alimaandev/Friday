<div align="center">
  <a name="readme-top"></a>

  <img src="og-image.png" alt="Friday AI — آپ کے ڈیسک ٹاپ کے لیے اوپن سورس JARVIS" width="100%">

  <br><br>

  <h1 align="center">Friday — آپ کے ڈیسک ٹاپ کے لیے اوپن سورس JARVIS</h1>

  <p align="center">
    بولیں، اشارہ کریں، یا ٹائپ کریں — آپ کا AI کمانڈ سینٹر <strong>آپ کی مشین</strong> پر چلتا ہے۔<br>
    کوئی کلاؤڈ لاک‑ان نہیں۔ کوئی سبسکرپشن نہیں۔ آپ کا ڈیٹا، آپ کے قواعد۔
  </p>

  <br>

  <p align="center">
    <a href="https://github.com/alimaandev/Friday/stargazers"><img src="https://img.shields.io/github/stars/alimaandev/Friday?style=for-the-badge&logo=github&color=gold" alt="Stars"></a>
    <a href="https://github.com/alimaandev/Friday/issues"><img src="https://img.shields.io/github/issues/alimaandev/Friday?style=for-the-badge&logo=github" alt="Issues"></a>
    <a href="https://github.com/alimaandev/Friday/actions"><img src="https://img.shields.io/github/actions/workflow/status/alimaandev/Friday/ci.yml?style=for-the-badge&logo=githubactions" alt="CI"></a>
    <a href="https://github.com/alimaandev/Friday/blob/main/LICENSE"><img src="https://img.shields.io/github/license/alimaandev/Friday?style=for-the-badge&color=green" alt="License"></a>
  </p>

  <p align="center">
    <b><a href="README.md">English</a></b>
    ·
    <b>اردو</b>
    ·
    <b><a href="README.hi.md">हिन्दी</a></b>
  </p>
</div>

<br>

<details>
  <summary><kbd>📖 فہرست</kbd></summary>

  - [⚡ فوری آغاز](#-فوری-آغاز)
  - [✨ Friday کیا ہے؟](#-friday-کیا-ہے)
  - [🚀 فیچرز](#-فیچرز)
  - [🤝 تعاون](#-تعاون)
  - [⭐ ستاروں کی تاریخ](#-ستاروں-کی-تاریخ)
  - [💖 سپورٹ](#-سپورٹ)
  - [📄 لائسنس](#-لائسنس)

</details>

<br>

---

## ⚡ فوری آغاز

### 🐳 Docker (تجویز کردہ)

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
cp config/providers.toml.example config/providers.toml
# config/providers.toml میں اپنی OpenRouter API کلید درج کریں
docker compose up -d
```

فرنٹ اینڈ → `http://localhost:5173` · بیک اینڈ → `http://localhost:8080`

### 🔧 دستی سیٹ اپ

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
pip install -r requirements.txt
cp config/providers.toml.example config/providers.toml
cd desktop && python api_server.py &
npm install
npm run dev
```

<br>

---

## ✨ Friday کیا ہے؟

**Friday** آپ کے ڈیسک ٹاپ کو AI کمانڈ سینٹر میں تبدیل کر دیتا ہے — جو Iron Man کے JARVIS انٹرفیس سے متاثر ہے۔ یہ مکمل طور پر اوپن سورس، ریئل‑ٹائم ڈیش بورڈ ہے جو درج ذیل کو یکجا کرتا ہے:

- ایک **3D ری ایکٹیو آرب** جو Friday کی حالت کے مطابق شکل بدلتا ہے
- ایک **لائیو انٹیلیجنس پینل** جس میں 10 ڈیٹا ماڈیولز (خبریں، موسم، اسٹاکس، کرپٹو، خلاء، زلزلے، CVE، GitHub ٹرینڈنگ، عالمی گھڑیاں، الرٹس)
- **وائس ان پٹ/آؤٹ پٹ** ویک ورڈ ڈیٹیکشن کے ساتھ ("Hey Friday")
- **ویب کیم ہاتھ کے اشاروں کا کنٹرول** — کھلی ہتھیلی سے بولیں، مٹھی سے بھیجیں
- **Google Calendar اور Gmail** انٹیگریشن OAuth 2.0 کے ذریعے
- **اسٹریمنگ چیٹ** جو کسی بھی OpenAI‑مطابق LLM (OpenRouter، OpenAI، Ollama، یا کسٹم) سے چلتی ہے

سب کچھ لوکل چلتا ہے۔ آپ کی API کلید، آپ کا LLM، آپ کی پسند۔

<br>

---

## 🚀 فیچرز

### ✨ v4 — "The Orb" میں نیا
- **🧘 Zen Mode** — انتہائی کم UI: ایک مونوکروم آرب + چیٹ؛ `⌘B` سے پورا ڈیش بورڈ
- **🖥️ کمپیوٹر کنٹرول** — ایپس کھولیں، ونڈوز فوکس کریں، ٹائپ کریں، کلک کریں — ہر ایکشن پہلے آپ کی تصدیق مانگتا ہے
- **🧩 پلگ ان مارکیٹ پلیس** — سیٹنگز سے ایک کلک میں کمیونٹی پلگ ان انسٹال/ہٹائیں
- **🛠 کسٹم ٹول بلڈر** — قدرتی زبان میں ٹول بنائیں، کوڈ کی ضرورت نہیں
- **📚 لوکل RAG** — دستاویزات ingest + سیمنٹک تلاش
- **🧠 نالج گراف** — اینٹیٹی/رلیشن نکالنا + سیشن کنٹینیوئٹی
- **🚫 بلیک آؤٹ موڈ** — ایک ٹوگل میں مکمل لوکل پرائیویسی (Ollama، نیٹ ورک ٹولز بلاک)

### 🧠 AI کور
- **اسٹریمنگ چیٹ** — ٹوکن بہ ٹوکن جوابات پلان ویزیولائزیشن اور ٹول‑کال ٹریکنگ کے ساتھ
- **ملٹی سیشن** — گفتگو بنائیں، سوئچ کریں، اور حذف کریں — ہر سیشن کی اپنی میموری
- **کمانڈ پیلیٹ** — `⌘K` / `Ctrl+K` فوری اقدامات کے لیے
- **سجیسشن چپس** — سیاق و سباق کے مطابق ایک کلک پرامپٹس

### 🎨 3D ری ایکٹیو آرب
10 اسٹیٹ‑ڈرائیو اینی میشن پروفائلز: Idle، Listening، Thinking، Reasoning، Speaking، Searching، Coding، Error، Offline۔ اضافی اثرات: ہینڈ ٹریکنگ فالو، آٹو‑پاز، پروسیجرل شیڈرز، Fresnel glow، ہولوگرافک ہیکس شیل، آربیٹل رِنگز۔

### 🌍 لائیو انٹیلیجنس پینل
10 ماڈیولز — خبریں، موسم، اسٹاکس، GitHub ٹرینڈنگ، زلزلے، کرپٹو، خلاء، عالمی گھڑیاں، CVE — سب SSE کے ذریعے ریئل‑ٹائم اپڈیٹ ہوتے ہیں۔

### 🎤 وائس اور جیسچر
وائس انپٹ/آؤٹ پٹ، ویک ورڈ ("Hey Friday")، ہاتھ کے اشارے (کھلی ہتھیلی = سننا، مٹھی = بھیجنا)، تین زبانیں (انگریزی، ہندی، اردو)۔

### 🔌 انٹیگریشنز
Google Calendar، Gmail، اسکرین کیپچر، میموری (TF‑IDF + Jaccard + ویکٹر)، پروایکٹو الرٹس، LLM پرووائیڈرز (OpenRouter، OpenAI، Ollama)۔

<br>

---

## 🤝 تعاون

ہر قسم کے تعاون کا خیر مقدم ہے — ٹائپو فکسس سے لے کر نئی فیچرز تک۔

1. ریپو کو fork کریں
2. فیچر برانچ بنائیں (`git checkout -b feat/amazing`)
3. تبدیلیاں کریں اور commit کریں
4. Push کریں (`git push origin feat/amazing`)
5. Pull Request کھولیں

[اوپن ایشوز](https://github.com/alimaandev/Friday/issues) دیکھیں — خاص طور پر [`good first issue`](https://github.com/alimaandev/Friday/labels/good%20first%20issue) لیبل والے۔

<a href="https://github.com/alimaandev/Friday/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alimaandev/Friday" alt="Contributors" width="600">
</a>

<br>

---

## ⭐ ستاروں کی تاریخ

<a href="https://star-history.com/#alimaandev/Friday&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date&theme=dark">
    <img width="600" src="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date" alt="Star History Chart">
  </picture>
</a>

<br>

---

## 💖 سپورٹ

- ⭐ ریپو کو **Star** کریں
- 🐛 **بگز رپورٹ** کریں یا [issues](https://github.com/alimaandev/Friday/issues) میں فیچر کی درخواست کریں
- 🤝 **کوڈ کا تعاون** کریں [pull requests](https://github.com/alimaandev/Friday/pulls) کے ذریعے
- 💰 **Sponsor** کریں [GitHub Sponsors](https://github.com/sponsors/alimaandev) پر

<br>

---

## 📄 لائسنس

MIT — استعمال کریں، تبدیل کریں، شائع کریں۔ تفصیلات کے لیے [LICENSE](LICENSE) دیکھیں۔

<br>

---

<p align="center">
  <sub>❤️ سے بنایا گیا <a href="https://github.com/alimaandev">alimaandev</a> کے ذریعے · 
  <a href="https://github.com/alimaandev/Friday/discussions">بات چیت</a> · 
  <a href="https://github.com/alimaandev/Friday/issues">مسائل</a></sub>
</p>

<p align="center">
  <a href="#readme-top">▲ اوپر جائیں ▲</a>
</p>