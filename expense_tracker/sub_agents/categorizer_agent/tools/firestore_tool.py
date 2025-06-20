# tools/firestore_tool.py
from google.cloud import firestore

def save_receipt(receipt_data: dict):
    db = firestore.Client()
    doc_ref = db.collection('receipts').add(receipt_data)
    return {'status': 'saved', 'doc_id': doc_ref[1].id}