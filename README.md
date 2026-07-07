<div align="center">
  <h1>NovaDL</h1>
  <p><strong>أداة تحميل فيديوهات وصوت من الإنترنت</strong></p>
  <p>
    <a href="https://github.com/B5d2z/NovaDL/releases"><img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-%3E%3D3.8-green" alt="Python"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://github.com/B5d2z/NovaDL"><img src="https://img.shields.io/github/stars/B5d2z/NovaDL?style=social" alt="Stars"></a>
  </p>
  <p>YouTube · TikTok · Instagram · Facebook · X · Vimeo · Reddit · Twitch · SoundCloud · <a href="SUPPORTED_SITES.md">1000+</a></p>
</div>

---

### التشغيل السريع

```bash
git clone https://github.com/B5d2z/NovaDL.git
cd novadl
python run.py
```
> **Windows:** انقر مرتين على `NovaDL.bat` — لا يحتاج أوامر.

### المميزات

| | |
|---|---|
| تحميل فيديو وصوت | MP3, M4A, Opus, FLAC, WAV |
| اختيار الجودة | Best → 1080p → 720p → 360p |
| قوائم تشغيل + ترجمة + صور مصغرة | استكمال التحميل عند الانقطاع |
| كوكيز + بروكسي | سجل التحميل + حفظ الإعدادات |
| قائمة تفاعلية بالأرقام | شريط تقدم مع سرعة ووقت متبقي |
| دعم 1000+ موقع | يعمل على Windows, macOS, Linux |

### ساعد في نشر المشروع ✨

```
⭐ نجمة على GitHub — تفرق وتساعد غيرك يلقى المشروع
🍴 Fork — إذا تحب تطور أو تعدل
💬 مشاركة — مع مهتمين بالتقنية
```

إذا استفدت من NovaDL، **حط نجمة** ⭐ على [GitHub](https://github.com/B5d2z/NovaDL). هذا يشجع ويوسع الانتشار.

### المتطلبات

- Python ≥ 3.8
- [FFmpeg](https://ffmpeg.org/) (للاستخراج الصوتي، شغّل `python run.py doctor`)

### الإعدادات

`~/.config/novadl/config.json`

```bash
python run.py config                          # عرض الكل
python run.py config output_dir "~/Videos"    # تغيير مسار الحفظ
```

### الأوامر

| الأمر | الوظيفة |
|-------|---------|
| `download` | تحميل فيديو |
| `audio` | استخراج صوت |
| `info` | معلومات الرابط |
| `config` | إعدادات |
| `update` | تحديث yt-dlp |
| `history` | سجل التحميلات |
| `doctor` | تشخيص النظام |

### هيكل المشروع

```
novadl/
├── run.py            # شغّلني
└── src/novadl/
    ├── cli.py        # 9 أوامر + قائمة تفاعلية
    ├── core.py       # كيانات وحالات استخدام
    ├── infra.py      # yt-dlp + إعدادات + سجل
    ├── ui.py         # واجهة المستخدم
    └── const.py      # ثوابت
```

### الترخيص

MIT — [B5t Alanzi](https://github.com/B5d2z) · [@B5d2z](https://x.com/B5d2z)
