#!/usr/bin/env bash
# =============================================================================
# build_macos.sh — RFID Stock System macOS Build Script
# Kullanım: bash build_macos.sh [version]
# Örnek:    bash build_macos.sh 1.0.0
# =============================================================================

set -e  # Hata olursa dur

VERSION=${1:-"1.0.0"}
APP_NAME="RFID Stock System"
DMG_NAME="RFID-Stock-System-v${VERSION}"

echo "=================================================="
echo "  RFID Stock System — macOS Build"
echo "  Versiyon: v${VERSION}"
echo "  Python: $(python3 --version 2>&1)"
echo "=================================================="

# -------------------------------------------------------
# 1. Sanal ortamı aktive et (.venv öncelikli)
# -------------------------------------------------------
echo ""
echo "▶ Sanal ortam kontrol ediliyor..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "  → .venv aktive edildi ($(python3 --version))"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "  → venv aktive edildi ($(python3 --version))"
else
    echo "  → Sanal ortam bulunamadı, sistem Python kullanılıyor."
fi

# -------------------------------------------------------
# 2. Bağımlılıkları yükle
# -------------------------------------------------------
echo ""
echo "▶ Bağımlılıklar yükleniyor..."
pip3 install -r requirements.txt --quiet
pip3 install pyinstaller --quiet
echo "  → Tüm bağımlılıklar hazır."

# -------------------------------------------------------
# 3. Önceki build'leri temizle
# -------------------------------------------------------
echo ""
echo "▶ Önceki build klasörleri temizleniyor..."
rm -rf build/ dist/
echo "  → Temizlendi."

# -------------------------------------------------------
# 4. PyInstaller ile .app oluştur
# -------------------------------------------------------
echo ""
echo "▶ PyInstaller build başlıyor..."
pyinstaller rfid_stock_system.spec \
    --noconfirm \
    --clean

# -------------------------------------------------------
# 5. .app'i doğrula
# -------------------------------------------------------
APP_PATH="dist/${APP_NAME}.app"
if [ ! -d "$APP_PATH" ]; then
    echo "❌ HATA: .app oluşturulamadı: ${APP_PATH}"
    exit 1
fi
echo "  ✅ .app oluşturuldu: ${APP_PATH}"

# -------------------------------------------------------
# 6. Ad-hoc codesign (Gatekeeper uyarısını azaltır)
# -------------------------------------------------------
echo ""
echo "▶ Ad-hoc codesign uygulanıyor..."
codesign --deep --force --sign - "$APP_PATH" 2>/dev/null && \
    echo "  ✅ Codesign tamamlandı." || \
    echo "  ⚠️  Codesign atlandı (Xcode CLI tools olmayabilir)."

# -------------------------------------------------------
# 7. Gatekeeper karantinasını kaldır (yerel test için)
# -------------------------------------------------------
echo ""
echo "▶ Karantina özelliği kaldırılıyor (yerel test için)..."
xattr -cr "$APP_PATH" 2>/dev/null && \
    echo "  ✅ Karantina kaldırıldı." || \
    echo "  ⚠️  xattr komutu başarısız oldu."

# -------------------------------------------------------
# 8. .dmg oluştur
# -------------------------------------------------------
echo ""
echo "▶ DMG oluşturuluyor..."

DMG_PATH="dist/${DMG_NAME}.dmg"
TMP_DMG="dist/tmp_${DMG_NAME}.dmg"

# Geçici DMG oluştur
hdiutil create \
    -volname "${APP_NAME}" \
    -srcfolder "${APP_PATH}" \
    -ov \
    -format UDZO \
    "$TMP_DMG"

# DMG'yi doğru konuma taşı
mv "$TMP_DMG" "$DMG_PATH"

echo "  ✅ DMG oluşturuldu: ${DMG_PATH}"

# -------------------------------------------------------
# 9. Özet
# -------------------------------------------------------
echo ""
echo "=================================================="
echo "  ✅ Build tamamlandı!"
echo ""
echo "  .app  : ${APP_PATH}"
echo "  .dmg  : dist/${DMG_NAME}.dmg"
FILESIZE=$(du -sh "dist/${DMG_NAME}.dmg" | cut -f1)
echo "  Boyut : ${FILESIZE}"
echo ""
echo "  Test etmek için:"
echo "    open \"${APP_PATH}\""
echo ""
echo "  DMG'yi açmak için:"
echo "    open dist/${DMG_NAME}.dmg"
echo "=================================================="
