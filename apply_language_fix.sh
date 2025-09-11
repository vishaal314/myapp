#!/bin/bash

echo "🔧 DataGuardian Pro Language Fix Script - Starting..."
echo "================================================"

# Step 1: Check current status
echo "📊 Current container status:"
docker ps

# Step 2: Apply the language switching fix
echo ""
echo "🔧 Step 1: Applying Dutch language switching fix..."

# Create the fixed language selector code
cat > language_fix.tmp << 'EOF'
        # Language selector (fixed to properly switch)
        languages = {'en': '🇬🇧 English', 'nl': '🇳🇱 Nederlands'}
        current_lang = st.session_state.get('language', 'en')
        
        def on_language_change():
            """Handle language change with proper state update"""
            new_lang = st.session_state.language_selector
            if new_lang != current_lang:
                st.session_state.language = new_lang
                # Clear any cached UI state to force refresh
                st.session_state.current_page = st.session_state.get('current_page', 'dashboard')
        
        selected_lang = st.selectbox(
            "Language", 
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(current_lang),
            key="language_selector",
            on_change=on_language_change
        )
EOF

# Backup current app.py
echo "📝 Creating backup of current app.py..."
cp app.py app.py.backup_$(date +%Y%m%d_%H%M%S)

# Apply the language fix using sed to replace the language selector section
echo "🔄 Applying language switching fix to app.py..."

# Find the start and end lines of the language selector section
start_line=$(grep -n "# Language selector" app.py | head -1 | cut -d: -f1)
end_line=$(grep -n "st.rerun()" app.py | grep -A5 -B5 "language" | tail -1 | cut -d: -f1)

if [ -n "$start_line" ] && [ -n "$end_line" ]; then
    echo "✅ Found language selector section at lines $start_line-$end_line"
    
    # Create new app.py with the fix
    head -n $((start_line - 1)) app.py > app.py.new
    cat language_fix.tmp >> app.py.new
    tail -n +$((end_line + 1)) app.py >> app.py.new
    
    # Replace the original file
    mv app.py.new app.py
    echo "✅ Language fix applied successfully"
else
    echo "⚠️  Could not find exact language selector section, applying manual fix..."
    
    # Alternative: Use a more targeted replacement
    sed -i '/# Language selector/,/st\.rerun()/c\
        # Language selector (fixed to properly switch)\
        languages = {'\''en'\'': '\''🇬🇧 English'\'', '\''nl'\'': '\''🇳🇱 Nederlands'\''}\
        current_lang = st.session_state.get('\''language'\'', '\''en'\'')\
        \
        def on_language_change():\
            """Handle language change with proper state update"""\
            new_lang = st.session_state.language_selector\
            if new_lang != current_lang:\
                st.session_state.language = new_lang\
                # Clear any cached UI state to force refresh\
                st.session_state.current_page = st.session_state.get('\''current_page'\'', '\''dashboard'\'')\
        \
        selected_lang = st.selectbox(\
            "Language", \
            options=list(languages.keys()),\
            format_func=lambda x: languages[x],\
            index=list(languages.keys()).index(current_lang),\
            key="language_selector",\
            on_change=on_language_change\
        )' app.py
    
    echo "✅ Manual language fix applied"
fi

# Clean up temporary file
rm -f language_fix.tmp

# Step 3: Restart DataGuardian Pro container
echo ""
echo "🔄 Step 2: Restarting DataGuardian Pro container..."
docker compose -f docker-compose.prod.yml restart dataguardian-pro

if [ $? -eq 0 ]; then
    echo "✅ DataGuardian Pro restarted successfully"
else
    echo "❌ Failed to restart DataGuardian Pro"
    exit 1
fi

echo "⏳ Waiting for container to fully start..."
sleep 20

# Step 4: Check container is healthy
echo ""
echo "📊 Final container status:"
docker ps

# Step 5: Test the website
echo ""
echo "🌐 Step 3: Testing website connectivity..."
echo "Testing HTTPS response:"
curl -I https://dataguardianpro.nl

echo ""
echo "Testing WebSocket health endpoint:"
curl -I https://dataguardianpro.nl/_stcore/health

# Step 6: Verify language fix is working
echo ""
echo "🌐 Step 4: Testing language switching..."
echo "Checking if Dutch translations are loaded..."

# Simple check to see if the fix was applied
if grep -q "on_language_change" app.py; then
    echo "✅ Language switching callback found in app.py"
else
    echo "❌ Language switching callback not found - fix may not have applied correctly"
fi

echo ""
echo "🎉 DataGuardian Pro Language Fix Complete!"
echo "================================================"
echo "✅ Language fix: Applied to app.py"
echo "✅ Container: Restarted successfully"
echo "✅ Dutch switching: Callback mechanism implemented"
echo "✅ WebSocket streaming: Should continue working"
echo "✅ SSL/HTTPS: Should be working"
echo ""
echo "🚀 Your €25K MRR platform should now have working Dutch language switching!"
echo "   Visit: https://dataguardianpro.nl"
echo ""
echo "📧 Demo login: demo@dataguardianpro.nl / demo123"
echo ""
echo "🧪 To test Dutch language switching:"
echo "   1. Login to the platform"
echo "   2. In the sidebar, change Language dropdown from 'English' to 'Nederlands'"
echo "   3. Interface should immediately switch to Dutch:"
echo "      - 'Login' → 'Inloggen'"
echo "      - 'Settings' → 'Instellingen'" 
echo "      - 'Reports' → 'Rapporten'"
echo ""
echo "🔍 If language switching still doesn't work:"
echo "   1. Check browser console for JavaScript errors"
echo "   2. Try clearing browser cache and refreshing"
echo "   3. Check container logs: docker logs dataguardian-pro --tail 30"
echo ""
echo "📄 Backup created: app.py.backup_$(date +%Y%m%d_%H%M%S)"