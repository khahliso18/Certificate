import streamlit as st
import hashlib
import json
import time
from typing import List, Dict, Any
from io import BytesIO
from fpdf import FPDF

# -----------------------
# Blockchain Class
# -----------------------
class CertificateBlockchain:
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_certificates: List[Dict[str, Any]] = []
        self.certificate_counter = 0
        self.new_block(proof=100, previous_hash="1")

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        block_certificates = [tx.copy() for tx in self.pending_certificates]
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "certificates": block_certificates,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_certificates = []
        block["hash"] = self.hash(block)
        self.chain.append(block)
        return block

    def add_certificate(self, student_name: str, course: str, university: str,
                        university_id: str, issue_date: str, file_bytes: bytes, file_name: str) -> int:
        self.certificate_counter += 1
        cert = {
            "certificate_id": self.certificate_counter,
            "student_name": student_name,
            "course": course,
            "university": university,
            "university_id": university_id,
            "issue_date": issue_date,
            "file_bytes": file_bytes,
            "file_name": file_name,
            "timestamp": time.time()
        }
        self.pending_certificates.append(cert)
        return self.certificate_counter

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        for cert in block_copy.get("certificates", []):
            if "file_bytes" in cert:
                cert["file_bytes"] = None
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def verify_certificate(self, student_name: str) -> List[Dict[str, Any]]:
        results = []
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["student_name"].lower() == student_name.lower():
                    results.append(cert)
        return results

# -----------------------
# PDF Generation Function
# -----------------------
def create_certificate(student_name, course, university, university_id, issue_date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "Certificate of Completion", ln=True, align="C")
    pdf.set_font("Arial", '', 16)
    pdf.ln(20)
    pdf.multi_cell(0, 10, f"This is to certify that {student_name} has successfully completed the course {course} at {university}.\n\nUniversity ID: {university_id}\nIssue Date: {issue_date}", align="C")
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_bytes = pdf_output.getvalue()
    pdf_output.close()
    return pdf_bytes

# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="🎓 Blockchain Certificate System", layout="wide", page_icon="🎓")

# Initialize blockchain
if "cert_chain" not in st.session_state:
    st.session_state.cert_chain = CertificateBlockchain()

bc = st.session_state.cert_chain

# Sidebar navigation
st.sidebar.title("🎓 Certificate System")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "🆕 Issue Certificate", "🔍 Verify Certificate", "📊 Ledger"])

# --- Home ---
if menu == "🏠 Home":
    st.title("🎓 Blockchain-Based Student Certificate Verification")
    st.markdown("""
    This system allows universities to issue tamper-proof certificates using blockchain technology.
    - Input student details to generate a certificate.
    - Certificates are stored in blocks to prevent tampering.
    - Verify authenticity of certificates by student name.
    - Dashboard shows blockchain ledger block-by-block.
    """)
    st.image("https://images.unsplash.com/photo-1606813909315-7f82e8f30c12?auto=format&fit=crop&w=800&q=80",
             use_container_width=True)

# --- Issue Certificate ---
elif menu == "🆕 Issue Certificate":
    st.header("🆕 Issue New Certificate")
    with st.form("issue_cert_form"):
        student_name = st.text_input("Student Name")
        course = st.selectbox("Course", ["BBA-FINTECH", "BBA-BA", "BBA-LSCM", "BBA-DM", "BBA-HR"])
        university = st.text_input("University")
        university_id = st.text_input("University ID")
        issue_date = st.date_input("Issue Date")
        submitted = st.form_submit_button("Generate Certificate")
        
        if submitted:
            if student_name and university and university_id:
                pdf_bytes = create_certificate(student_name, course, university, university_id, issue_date)
                file_name = f"{student_name.replace(' ','_')}_certificate.pdf"
                
                cert_id = bc.add_certificate(student_name, course, university, university_id, str(issue_date), pdf_bytes, file_name)
                bc.new_block(proof=123)
                
                st.success(f"✅ Certificate #{cert_id} issued for {student_name}.")
                st.download_button("📄 Download Certificate", pdf_bytes, file_name, "application/pdf")
            else:
                st.error("Please fill in all required fields.")

# --- Verify Certificate ---
elif menu == "🔍 Verify Certificate":
    st.header("🔍 Verify Certificate by Student Name")
    student_to_verify = st.text_input("Enter Student Name")
    
    if st.button("Verify"):
        if student_to_verify:
            results = bc.verify_certificate(student_to_verify)
            if results:
                st.success(f"Found {len(results)} certificate(s) for {student_to_verify}.")
                for cert in results:
                    st.markdown(f"""
                        <div style="padding:15px; border:2px solid #4B0082; border-radius:10px; margin-bottom:10px; background-color:#f0f8ff;">
                        <h4 style="color:#4B0082;">🎓 Certificate ID: {cert['certificate_id']}</h4>
                        <p><b>Student:</b> {cert['student_name']}</p>
                        <p><b>Course:</b> {cert['course']}</p>
                        <p><b>University:</b> {cert['university']}</p>
                        <p><b>University ID:</b> {cert['university_id']}</p>
                        <p><b>Issue Date:</b> {cert['issue_date']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button(f"📄 Download Certificate {cert['certificate_id']}", cert['file_bytes'], cert['file_name'], "application/pdf")
            else:
                st.warning("No certificates found for this student.")
        else:
            st.error("Please enter a student name.")

# --- Ledger ---
elif menu == "📊 Ledger":
    st.header("📊 Blockchain Ledger Overview")
    if not bc.chain:
        st.info("No blocks in the blockchain yet.")
    else:
        for block in bc.chain:
            st.markdown(f"""
                <div style="padding:10px; border:3px solid #4B0082; border-radius:10px; margin-bottom:20px; background-color:#e6e6fa;">
                <h3 style="color:#4B0082;">🧱 Block {block['index']}</h3>
                <p><b>Proof:</b> {block['proof']} | <b>Previous Hash:</b> {block['previous_hash']}</p>
                <p><b>Timestamp:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block['timestamp']))}</p>
            """, unsafe_allow_html=True)
            
            if block["certificates"]:
                for cert in block["certificates"]:
                    st.markdown(f"""
                        <div style="padding:10px; border:2px solid #4B0082; border-radius:8px; margin-bottom:10px; background-color:#f8f8ff;">
                        <h5 style="color:#4B0082;">🎓 Certificate ID: {cert['certificate_id']}</h5>
                        <p><b>Student:</b> {cert['student_name']}</p>
                        <p><b>Course:</b> {cert['course']}</p>
                        <p><b>University:</b> {cert['university']}</p>
                        <p><b>University ID:</b> {cert['university_id']}</p>
                        <p><b>Issue Date:</b> {cert['issue_date']}</p>
                        <p><b>Certificate File:</b> {cert['file_name']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
