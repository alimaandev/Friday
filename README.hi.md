<div align="center">
  <a name="readme-top"></a>

  <img src="og-image.png" alt="Friday AI — आपके डेस्कटॉप के लिए ओपन-सोर्स JARVIS" width="100%">

  <br><br>

  <h1 align="center">Friday — आपके डेस्कटॉप के लिए ओपन-सोर्स JARVIS</h1>

  <p align="center">
    बोलें, इशारा करें, या टाइप करें — आपका AI कमांड सेंटर <strong>आपकी मशीन</strong> पर चलता है।<br>
    कोई क्लाउड लॉक‑इन नहीं। कोई सब्सक्रिप्शन नहीं। आपका डेटा, आपके नियम।
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
    <b><a href="README.ur.md">اردو</a></b>
    ·
    <b>हिन्दी</b>
  </p>
</div>

<br>

<details>
  <summary><kbd>📖 विषय सूची</kbd></summary>

  - [⚡ त्वरित आरंभ](#-त्वरित-आरंभ)
  - [✨ Friday क्या है?](#-friday-क्या-है)
  - [🚀 विशेषताएँ](#-विशेषताएँ)
  - [🤝 योगदान](#-योगदान)
  - [⭐ स्टार हिस्ट्री](#-स्टार-हिस्ट्री)
  - [💖 सहयोग](#-सहयोग)
  - [📄 लाइसेंस](#-लाइसेंस)

</details>

<br>

---

## ⚡ त्वरित आरंभ

### 🐳 Docker (अनुशंसित)

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
cp config/providers.toml.example config/providers.toml
# config/providers.toml में अपनी OpenRouter API कुंजी डालें
docker compose up -d
```

फ्रंटएंड → `http://localhost:5173` · बैकएंड → `http://localhost:8080`

### 🔧 मैन्युअल सेटअप

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

## ✨ Friday क्या है?

**Friday** आपके डेस्कटॉप को AI कमांड सेंटर में बदल देता है — जो Iron Man के JARVIS इंटरफ़ेस से प्रेरित है। यह पूरी तरह से ओपन-सोर्स, रीयल‑टाइम डैशबोर्ड है जो निम्नलिखित को जोड़ता है:

- एक **3D रिएक्टिव ऑर्ब** जो Friday की स्थिति के अनुसार आकार बदलता है
- एक **लाइव इंटेलिजेंस पैनल** जिसमें 10 डेटा मॉड्यूल (समाचार, मौसम, स्टॉक्स, क्रिप्टो, अंतरिक्ष, भूकंप, CVE, GitHub ट्रेंडिंग, वैश्विक घड़ियाँ, अलर्ट)
- **वॉइस इनपुट/आउटपुट** वेक वर्ड डिटेक्शन के साथ ("Hey Friday")
- **वेबकैम हाथ के इशारों का नियंत्रण** — खुली हथेली से बोलें, मुट्ठी से भेजें
- **Google Calendar और Gmail** एकीकरण OAuth 2.0 के माध्यम से
- **स्ट्रीमिंग चैट** जो किसी भी OpenAI‑संगत LLM (OpenRouter, OpenAI, Ollama, या कस्टम) से चलती है

सब कुछ लोकल चलता है। आपकी API कुंजी, आपका LLM, आपकी पसंद।

<br>

---

## 🚀 विशेषताएँ

### 🧠 AI कोर
- **स्ट्रीमिंग चैट** — टोकन-दर-टोकन उत्तर प्लान विज़ुअलाइज़ेशन और टूल-कॉल ट्रैकिंग के साथ
- **मल्टी-सेशन** — वार्तालाप बनाएँ, स्विच करें, और हटाएँ — प्रत्येक सेशन की अपनी मेमोरी
- **कमांड पैलेट** — `⌘K` / `Ctrl+K` त्वरित कार्रवाई के लिए
- **सुझाव चिप्स** — संदर्भ-जागरूक एक-क्लिक प्रॉम्प्ट

### 🎨 3D रिएक्टिव ऑर्ब
10 स्थिति-संचालित एनिमेशन प्रोफ़ाइल: Idle, Listening, Thinking, Reasoning, Speaking, Searching, Coding, Error, Offline। अतिरिक्त प्रभाव: हैंड ट्रैकिंग फ़ॉलो, ऑटो-पॉज़, प्रोसीजरल शेडर्स, Fresnel glow, होलोग्राफिक हेक्स शेल, ऑर्बिटल रिंग्स।

### 🌍 लाइव इंटेलिजेंस पैनल
10 मॉड्यूल — समाचार, मौसम, स्टॉक्स, GitHub ट्रेंडिंग, भूकंप, क्रिप्टो, अंतरिक्ष, वैश्विक घड़ियाँ, CVE — सभी SSE के माध्यम से रीयल‑टाइम अपडेट होते हैं।

### 🎤 वॉइस और जेस्चर
वॉइस इनपुट/आउटपुट, वेक वर्ड ("Hey Friday"), हाथ के इशारे (खुली हथेली = सुनना, मुट्ठी = भेजना), तीन भाषाएँ (अंग्रेज़ी, हिंदी, उर्दू)।

### 🔌 एकीकरण
Google Calendar, Gmail, स्क्रीन कैप्चर, मेमोरी (TF‑IDF + Jaccard + वेक्टर), प्रोएक्टिव अलर्ट, LLM प्रदाता (OpenRouter, OpenAI, Ollama)।

<br>

---

## 🤝 योगदान

हम सभी प्रकार के योगदानों का स्वागत करते हैं — टाइपो सुधार से लेकर नई सुविधाओं तक।

1. रेपो को fork करें
2. फीचर ब्रांच बनाएँ (`git checkout -b feat/amazing`)
3. बदलाव करें और commit करें
4. Push करें (`git push origin feat/amazing`)
5. Pull Request खोलें

[ओपन इश्यूज़](https://github.com/alimaandev/Friday/issues) देखें — विशेष रूप से [`good first issue`](https://github.com/alimaandev/Friday/labels/good%20first%20issue) लेबल वाले।

<a href="https://github.com/alimaandev/Friday/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alimaandev/Friday" alt="Contributors" width="600">
</a>

<br>

---

## ⭐ स्टार हिस्ट्री

<a href="https://star-history.com/#alimaandev/Friday&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date&theme=dark">
    <img width="600" src="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date" alt="Star History Chart">
  </picture>
</a>

<br>

---

## 💖 सहयोग

- ⭐ रेपो को **Star** करें
- 🐛 **बग्स रिपोर्ट** करें या [issues](https://github.com/alimaandev/Friday/issues) में फीचर का अनुरोध करें
- 🤝 **कोड योगदान** दें [pull requests](https://github.com/alimaandev/Friday/pulls) के माध्यम से
- 💰 **Sponsor** करें [GitHub Sponsors](https://github.com/sponsors/alimaandev) पर

<br>

---

## 📄 लाइसेंस

MIT — उपयोग करें, संशोधित करें, प्रकाशित करें। विवरण के लिए [LICENSE](LICENSE) देखें।

<br>

---

<p align="center">
  <sub>❤️ से बनाया गया <a href="https://github.com/alimaandev">alimaandev</a> द्वारा · 
  <a href="https://github.com/alimaandev/Friday/discussions">चर्चा</a> · 
  <a href="https://github.com/alimaandev/Friday/issues">मुद्दे</a></sub>
</p>

<p align="center">
  <a href="#readme-top">▲ ऊपर जाएँ ▲</a>
</p>