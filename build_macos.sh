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
echo "=================================================="

# -------------------------------------------------------
# 1. Sanal ortamı aktive et
# -------------------------------------------------------
echo ""
echo "▶ Sanal ortam kontrol ediliyor..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "  → Sanal ortam bulunamadı, sistem Python kullanılıyor."
fi

# -------------------------------------------------------
# 2. Bağımlılıkları yükle
# -------------------------------------------------------
echo ""
echo "▶ Bağımlılıklar yükleniyor..."
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

# -------------------------------------------------------
# 3. Önceki build'leri temizle
# -------------------------------------------------------
echo ""
echo "▶ Önceki build klasörleri temizleniyor..."
rm -rf build/ dist/

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
# 7. .dmg oluştur
# -------------------------------------------------------
echo ""
echo "▶ DMG oluşturuluyor..."

DMG_PATH="dist/${DMG_NAME}.dmg"
TMP_DMG="dist/tmp_${DMG_NAME}.dmg"

# hdiutil ile DMG oluştur
hdiutil create \
    -volname "${APP_NAME}" \
    -srcfolder "dist/${APP_NAME}.app" \
    -ov \
    -format UDZO \
    "$TMP_DMG"

# DMG'yi doğru konuma taşı
mv "$TMP_DMG" "$DMG_PATH"

echo "  ✅ DMG oluşturuldu: ${DMG_PATH}"

# -------------------------------------------------------
# 8. Özet
# -------------------------------------------------------
echo ""
echo "=================================================="
echo "  ✅ Build tamamlandı!"
echo ""
echo "  Dosya: dist/${DMG_NAME}.dmg"
FILESIZE=$(du -sh "dist/${DMG_NAME}.dmg" | cut -f1)
echo "  Boyut: ${FILESIZE}"
echo ""
echo "  Test etmek için:"
echo "    open dist/${DMG_NAME}.dmg"
echo "=================================================="
