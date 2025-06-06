from db import SessionLocal
from models import InternalDoc

def seed():
    db = SessionLocal()

    if db.query(InternalDoc).first():
        print("✅ Data sudah ada, tidak perlu seeding.")
        return

    db.add_all([
        InternalDoc(title="HR Policy", content="Jatah cuti tahunan: 12 hari kerja per tahun.\nProbation: 3 bulan."),
        InternalDoc(title="Reimbursement", content="Transportasi bisa direimburse hingga Rp100.000/hari."),
        InternalDoc(title="Formulir", content="Form cuti: https://example.com/form-cuti.pdf\nForm reimb: https://example.com/form-reimbursement.pdf"),
    ])
    db.commit()
    db.close()
    print("🌱 Seeding selesai.")

if __name__ == "__main__":
    seed()
