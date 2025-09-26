import streamlit as st
import hashlib
import json
import time
from typing import List, Dict, Any
import pandas as pd

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
                        university_id: str, issue_date: str, file_name: str) -> int:
        self.certificate_counter += 1
        cert = {
            "certificate_id": self.certificate_counter,
            "student_name": student_name,
            "course": course,
            "university": university,
            "university_id": university_id,
            "issue_date": issue_date,
            "file_name": file_name,
            "timestamp": time.time()
        }
        self.pending_certificates.append(cert)
        return self.certificate_counter

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr["previous_hash"] != prev["hash"]:
                return False
            if curr["hash"] != self.hash(curr):
                return False
        return True

    def verify_certificate(self, student_name: str) -> List[Dict[str, Any]]:
        results = []
        for block in self.chain:
            for cert in block["certificates"]:
                if cert["student_name"].lower() == student_name.lower():
                    results.append({
                        "Block": block["index"],
                        "Certificate ID": cert["certificate_id"],
                        "Student": cert["student_name"],
                        "Course": cert["course"],
                        "University": cert["university"],
                        "University ID": cert["university_id"],
                        "Issue Date": cert["issue_date"],
                        "Certificate File": cert["file_name"],
                        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S",
                                                   time.localtime(cert["timestamp"]))
                    })
        return results

    def all_certificates_summary(self) -> pd.DataFrame:
        rows = []
        for block in self.chain:
            for cert in block["certificates"]:
                rows.append({
                    "Certificate ID": cert["certificate_id"],
                    "Student": cert["student_name"],
                    "Course": cert["course"],
                    "University": cert["university"],
                    "University ID": cert["university_id"],
                    "Issue Date": cert["issue_date"],
                    "Certificate File": cert["file_name"],
                    "Block": block["index"],
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime(cert["timestamp"]))
                })
        return pd.DataFrame(rows)


# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="🎓 Blockchain Certificate Verification", layout="wide")

if "cert_chain" not in st.session_state:
    st.session_state.cert_chain = CertificateBlockchain()

bc: CertificateBlockchain = st.session_state.cert_chain

st.sidebar.title("🎓 Certificate System")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "🆕 Issue Certificate", "🔍 Verify Certificate", "📊 Ledger"])

# --- Issue Certificate ---
if menu == "🆕 Issue Certificate":
    st.header("🆕 Issue New Certificate")
    with st.form("cert_form", clear_on_submit=True):
        student_name = st.text_input("Student Name")
        course = st.selectbox("Course", ["BBA-FINTECH", "BBA-BA", "BBA-LSCM", "BBA-DM", "BBA-HR"])
        university = st.text_input("University")
        university_id = st.text_input("University ID")
        issue_date = st.date_input("Issue Date")
        file = st.file_uploader("Upload Certificate (PDF/JPG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Issue Certificate")
        if submitted and student_name and university and university_id:
            file_name = file.name if file else "Not Provided"
            cert_id = bc.add_certificate(student_name, course, university, university_id,
                                         str(issue_date), file_name)
            block = bc.new_block(proof=123)
            st.success(f"✅ Certificate #{cert_id} issued to {student_name} in Block {block['index']}.")
