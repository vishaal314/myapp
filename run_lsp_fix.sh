#!/bin/bash
# Run LSP Error Fix for DataGuardian Pro

echo "🔧 DataGuardian Pro - LSP Error Fix Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "Please run this script from the DataGuardian Pro root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# Run the LSP fix
echo "🚀 Running comprehensive LSP error fix..."
python3 fix_all_lsp_errors.py

# Check the result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ LSP fix completed successfully!"
    
    # Optional: Restart workflows if available
    if command -v streamlit &> /dev/null; then
        echo ""
        echo "🔄 Restarting Streamlit server..."
        pkill -f "streamlit run"
        sleep 2
        nohup streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true > /dev/null 2>&1 &
        echo "✅ Streamlit server restarted"
    fi
    
    echo ""
    echo "🎯 All LSP errors should now be resolved!"
    echo "📋 Verify by checking LSP diagnostics"
    
else
    echo ""
    echo "❌ LSP fix failed"
    echo "🔍 Check the error messages above"
    echo "📋 Manual fixes may be required"
    exit 1
fi