import re

with open('utils/scanners/sustainability_scanner.py', 'r') as file:
    content = file.read()

# Replace recommendation expanders with markdown headers
pattern1 = r"with st\.expander\(f\"\{i\+1\}\. \{rec\.get\('title', 'Recommendation'\)\}\"\):"
replacement1 = "# Use markdown header instead of expander\n            st.markdown(f\"#### {i+1}. {rec.get('title', 'Recommendation')}\")"
content = re.sub(pattern1, replacement1, content)

# Replace Show Raw Scan Data expander with a simple button
pattern2 = r"with st\.expander\(\"Show Raw Scan Data\"\):"
replacement2 = "if st.button(\"Show/Hide Raw Scan Data\"):"
content = re.sub(pattern2, replacement2, content)

# Fix indentation issues from removed "with" blocks
content = content.replace("\n                st.write", "\n            st.write")
content = content.replace("\n                    st.write", "\n                st.write")
content = content.replace("\n                    for step", "\n                for step")
content = content.replace("\n                        st.write", "\n                    st.write")

# Write the modified content back to the file
with open('utils/scanners/sustainability_scanner.py', 'w') as file:
    file.write(content)

print("Expanders replaced successfully!")
