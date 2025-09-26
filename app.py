# --- Verify Certificate ---
elif menu == "🔍 Verify Certificate":
    st.header("🔍 Verify Student Certificate")
    student_to_verify = st.text_input("Enter Student Name")
    
    if st.button("Verify"):
        if student_to_verify:
            results = bc.verify_certificate(student_to_verify)
            
            if results:
                st.success(f"Found {len(results)} certificate(s) for {student_to_verify}:")
                
                for cert in results:
                    st.markdown(f"""
                        <div style="padding:15px; border:2px solid #4B0082; border-radius:10px; margin-bottom:10px; background-color:#f0f8ff;">
                        <h4 style="color:#4B0082;">🎓 Certificate ID: {cert['Certificate ID']}</h4>
                        <p><b>Student Name:</b> {cert['Student']}</p>
                        <p><b>Course:</b> {cert['Course']}</p>
                        <p><b>University:</b> {cert['University']}</p>
                        <p><b>University ID:</b> {cert['University ID']}</p>
                        <p><b>Issue Date:</b> {cert['Issue Date']}</p>
                        <p><b>Block:</b> {cert['Block']}</p>
                        <p><b>Timestamp:</b> {cert['Timestamp']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show image preview or PDF download
                    if cert['File Bytes']:
                        if cert['Certificate File'].lower().endswith((".jpg", ".jpeg", ".png")):
                            st.image(cert['File Bytes'], caption=cert['Certificate File'], use_container_width=True)
                        elif cert['Certificate File'].lower().endswith(".pdf"):
                            st.download_button(
                                label=f"Download {cert['Certificate File']}",
                                data=cert['File Bytes'],
                                file_name=cert['Certificate File'],
                                mime='application/pdf'
                            )
                    
                    # Download certificate details as JSON
                    cert_json = json.dumps({k: v for k, v in cert.items() if k != "File Bytes"}, indent=4)
                    st.download_button(
                        label="Download Certificate Details (JSON)",
                        data=cert_json,
                        file_name=f"certificate_{cert['Certificate ID']}.json",
                        mime="application/json"
                    )
            else:
                st.warning("No certificates found for this student.")
        else:
            st.error("Please enter a student name to verify.")
