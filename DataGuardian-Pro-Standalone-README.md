# DataGuardian Pro - Standalone Windows Package

## Ready-to-Use Standalone Package

This package contains everything you need to run DataGuardian Pro on Windows without any installation or dependencies.

### What's Included:
- **DataGuardian Pro.exe** - Self-contained executable (~150-200MB)
- **Start DataGuardian Pro.bat** - Easy startup script
- **README.txt** - Quick start guide
- **config/** - Configuration files
- **documentation/** - User guides and documentation

### Quick Start:
1. Extract the ZIP file to any folder
2. Double-click **"Start DataGuardian Pro.bat"**
3. Wait 10-20 seconds for startup
4. Browser opens automatically to http://localhost:5000
5. Start scanning for GDPR compliance!

### Features:
✅ **No Installation Required** - Works from any folder
✅ **No Dependencies** - Everything included in one package
✅ **Portable** - Run from USB drive or network share
✅ **Self-Contained Database** - Uses SQLite, no PostgreSQL needed
✅ **Offline Capable** - Most features work without internet
✅ **Professional Reports** - HTML and PDF export

### System Requirements:
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Modern web browser (Chrome, Edge, Firefox)

### Building Your Own Executable

If you want to build the executable yourself on Windows:

1. **Install Python 3.11** from python.org
2. **Clone the repository:**
   ```batch
   git clone https://github.com/yourusername/dataguardian-pro.git
   cd dataguardian-pro
   ```

3. **Run the build script:**
   ```batch
   build_windows_package.bat
   ```

4. **Find your executable in:**
   ```
   DataGuardian-Pro-Windows/DataGuardian Pro.exe
   ```

### Advanced Configuration

**Database Options:**
- **SQLite (Default)** - No setup required
- **PostgreSQL** - Edit config/.env file
- **Redis Caching** - Edit config/.env file

**Port Configuration:**
- Default: http://localhost:5000
- Change in config/.env: `STREAMLIT_SERVER_PORT=8501`

**Memory Settings:**
- Low Memory Mode: Edit config/.env
- Add: `STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50`

### Troubleshooting

**Common Issues:**
1. **"Port 5000 is busy"** → Edit config/.env, change port to 8501
2. **Antivirus warning** → Add DataGuardian Pro folder to exclusions
3. **Slow startup** → Close unnecessary programs, ensure 4GB+ RAM
4. **Browser doesn't open** → Manually go to http://localhost:5000

**Performance Tips:**
- Use SSD storage for better performance
- Close unnecessary applications
- Ensure 8GB+ RAM for large scans
- Use Chrome or Edge browser for best experience

### Scanner Types Available:

1. **Code Scanner** - Source code security and PII detection
2. **Website Scanner** - GDPR cookie and privacy compliance
3. **Document Scanner** - PDF, Word, and text file analysis
4. **Image Scanner** - OCR-based PII detection in images
5. **Database Scanner** - Direct database PII scanning
6. **API Scanner** - REST API security assessment
7. **AI Model Scanner** - AI/ML model privacy compliance
8. **SOC2 Scanner** - SOC2 compliance validation
9. **DPIA Scanner** - Data Protection Impact Assessment
10. **Sustainability Scanner** - Environmental impact analysis

### Netherlands-Specific Features:

- **UAVG Compliance** - Dutch privacy law requirements
- **BSN Detection** - Dutch social security number identification
- **AP Authority** - Dutch DPA compliance requirements
- **EU AI Act 2025** - Latest AI regulation compliance
- **Dutch Language** - Full interface translation

### Enterprise Features:

- **Role-Based Access** - 7 different user roles
- **Professional Reports** - Branded HTML/PDF exports
- **Compliance Certificates** - Green/Yellow/Red status
- **Audit Trails** - Complete scan history
- **Batch Processing** - Multiple file scanning
- **API Integration** - REST API for automation

### Support:

- **Documentation** - Complete user guides included
- **Community** - GitHub discussions and issues
- **Professional Support** - Available for enterprise users
- **Updates** - Regular releases with new features

### License:

This standalone package is licensed for evaluation and non-commercial use. For commercial deployment, please contact us for licensing terms.

### Security Note:

This standalone executable is digitally signed and safe to use. If Windows Defender or antivirus software shows warnings, it's due to the executable being new. You can safely add it to your antivirus exclusions.

---

**Version**: 1.0.0  
**Built**: July 14, 2025  
**Platform**: Windows 10/11 (64-bit)  
**Size**: ~200MB (compressed: ~80MB)  

Ready to scan for GDPR compliance! 🚀