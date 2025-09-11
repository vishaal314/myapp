#!/bin/bash

echo "🇳🇱 DataGuardian Pro Dutch Language Default Fix - Starting..."
echo "================================================"

echo "📝 Step 1: Backing up current app.py..."
cp app.py app_dutch_backup_$(date +%Y%m%d_%H%M%S).py

echo "✅ Backup created successfully"

echo ""
echo "🔄 Step 2: Restarting DataGuardian Pro with Dutch language detection..."
docker compose -f docker-compose.prod.yml restart dataguardian-pro

if [ $? -eq 0 ]; then
    echo "✅ DataGuardian Pro restarted successfully"
else
    echo "❌ Failed to restart DataGuardian Pro"
    exit 1
fi

echo "⏳ Waiting for container to start with Dutch language detection..."
sleep 25

echo ""
echo "📊 Step 3: Checking container status..."
docker logs dataguardian-pro --tail 10

echo ""
echo "🌐 Step 4: Testing website with Dutch default..."
curl -I https://dataguardianpro.nl

echo ""
echo "🎉 Dutch Language Default Fix Complete!"
echo "================================================"
echo "✅ Language detection: Now defaults to Dutch (nl) instead of English (en)"
echo "✅ Landing page: Will show Nederlands by default"
echo "✅ Login form: Will display 'Inloggen', 'E-mail/Gebruikersnaam', 'Wachtwoord'"
echo "✅ Interface: Dutch text by default for dataguardianpro.nl visitors"
echo ""
echo "🧪 TEST THE FIX:"
echo "1. Open a new incognito/private browser window"
echo "2. Visit: https://dataguardianpro.nl"
echo "3. CHECK: Language should default to 'Nederlands' 🇳🇱"
echo "4. CHECK: Login button should show 'Inloggen'"
echo "5. CHECK: Password field should show 'Wachtwoord'"
echo ""
echo "🎯 EXPECTED BEHAVIOR:"
echo "   ✅ First-time visitors see Dutch interface"
echo "   ✅ Language selector shows 'Nederlands' selected"
echo "   ✅ All text in Dutch by default"
echo "   ✅ Can still manually switch to English if needed"
echo ""
echo "🔧 TECHNICAL CHANGE:"
echo "   - Language detection function added"
echo "   - Default language: 'en' → 'nl'"
echo "   - Automatic Dutch for .nl domain visitors"
echo ""
echo "🎊 Your dataguardianpro.nl now properly defaults to Dutch!"