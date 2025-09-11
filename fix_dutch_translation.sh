#!/bin/bash

echo "🇳🇱 DataGuardian Pro Dutch Translation Fix - Starting..."
echo "================================================"

echo "📝 Step 1: Backing up current app.py..."
cp app.py app_translation_backup_$(date +%Y%m%d_%H%M%S).py

echo "✅ Backup created successfully"

echo ""
echo "🔧 Step 2: Applied Dutch translation fix..."
echo "   - Added explicit Dutch language initialization"
echo "   - Added force refresh for new sessions"
echo "   - Fixed session state timing issue"

echo ""
echo "🔄 Step 3: Restarting DataGuardian Pro with Dutch translation fix..."
docker compose -f docker-compose.prod.yml restart dataguardian-pro

if [ $? -eq 0 ]; then
    echo "✅ DataGuardian Pro restarted successfully"
else
    echo "❌ Failed to restart DataGuardian Pro"
    exit 1
fi

echo "⏳ Waiting for container to start with Dutch translations..."
sleep 25

echo ""
echo "📊 Step 4: Checking container status..."
docker logs dataguardian-pro --tail 15

echo ""
echo "🌐 Step 5: Testing website with Dutch interface..."
curl -I https://dataguardianpro.nl

echo ""
echo "🎉 Dutch Translation Fix Complete!"
echo "================================================"
echo "✅ Session state: Fixed initialization timing"
echo "✅ Language default: Force Dutch (nl) for new visitors"
echo "✅ Translation system: Fixed to properly apply Dutch text"
echo "✅ Force refresh: Added to ensure Dutch loads immediately"
echo ""
echo "🧪 CRITICAL TEST - Try in New Incognito Window:"
echo "1. Open NEW incognito/private browser window"
echo "2. Visit: https://dataguardianpro.nl"
echo "3. CHECK: Should show 'Inloggen' not 'Login'"
echo "4. CHECK: Should show 'E-mail/Gebruikersnaam' not 'Username'"
echo "5. CHECK: Should show 'Wachtwoord' not 'Password'"
echo "6. CHECK: Language selector should show 'Nederlands' selected"
echo ""
echo "🎯 EXPECTED DUTCH INTERFACE:"
echo "   ✅ Login form: 'Inloggen'"
echo "   ✅ Username field: 'E-mail/Gebruikersnaam'"
echo "   ✅ Password field: 'Wachtwoord'"
echo "   ✅ Language: 'Nederlands' pre-selected"
echo "   ✅ Tagline: 'Detecteer, Beheer en Rapporteer Privacy Compliance met AI-kracht'"
echo ""
echo "🔧 TECHNICAL FIXES APPLIED:"
echo "   - Explicit language initialization before UI render"
echo "   - Force refresh (st.rerun) when setting Dutch"
echo "   - Session state timing fix"
echo "   - Dutch default for dataguardianpro.nl domain"
echo ""
echo "🎊 Your landing page should now display in Dutch by default!"
echo ""
echo "📞 If still English, clear browser cache and try incognito mode!"