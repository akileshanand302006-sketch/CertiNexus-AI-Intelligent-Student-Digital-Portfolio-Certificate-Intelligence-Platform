import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
sys.path.insert(0, os.getcwd())

from app.database.connection import SessionLocal
from app.models.user import User
from app.models.certificate import Certificate
from ml.extraction.document_type import DocumentTypeDetector
from ml.extraction.rule_ner import RuleBasedNER

db = SessionLocal()
cert = db.query(Certificate).filter(Certificate.id == 'f36a0843-30c5-489b-aa86-9b512d1fe021').first()
if cert:
    print('Found cert:', cert.id)
    print('Current document_type:', getattr(cert, 'document_type', None))
    print('Current category:', cert.category)
    print('Current recipient_name:', cert.recipient_name)
    print('Current organization:', cert.organization)
    
    detector = DocumentTypeDetector()
    res = detector.detect(cert.raw_ocr_text or '', cert.original_filename)
    print('Detector result:', res)
    
    ner = RuleBasedNER()
    ner_res = ner.extract(cert.raw_ocr_text or '')
    
    if res['document_type'] == 'resume':
        cert.document_type = 'resume'
        cert.category = 'Resume / CV'
        cert.recipient_name = res.get('candidate_name') or 'Student Scholar'
        cert.organization = None
        cert.event = 'Candidate Curriculum Vitae'
        cert.ai_confidence = res['confidence']
        db.commit()
        print('Successfully updated cert f36a0843 to Resume / CV!')
        print('New recipient:', cert.recipient_name)
        print('New category:', cert.category)
        print('New doc type:', cert.document_type)
else:
    print('Cert f36a0843 not found')

db.close()
