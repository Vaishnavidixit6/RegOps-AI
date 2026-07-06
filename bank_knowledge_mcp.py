import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bank-knowledge")

def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect("bank_knowledge.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@mcp.tool()
def search_sops(query: str) -> str:
    """Search internal bank Standard Operating Procedures (SOPs) and policies.
    
    Args:
        query: Search term (e.g., 'KYC', 'Personal Loan', 'Gold Loan').
    """
    sql = "SELECT sop_code, title, product_type, last_updated, content FROM internal_sops WHERE title LIKE ? OR content LIKE ?"
    term = f"%{query}%"
    results = query_db(sql, (term, term))
    if not results:
        return f"No SOPs found matching query: {query}"
    
    output = []
    for r in results:
        output.append(f"SOP Code: {r['sop_code']}\nTitle: {r['title']}\nProduct Type: {r['product_type']}\nLast Updated: {r['last_updated']}\nContent: {r['content']}\n" + "-"*40)
    return "\n\n".join(output)

@mcp.tool()
def search_fraud_advisories(query: str) -> str:
    """Search bank fraud advisories and security threat alerts.
    
    Args:
        query: Search term (e.g., 'Deepfake', 'Spoofing', 'GPS').
    """
    sql = "SELECT advisory_code, title, issue_date, threat_level, content FROM fraud_advisories WHERE title LIKE ? OR content LIKE ?"
    term = f"%{query}%"
    results = query_db(sql, (term, term))
    if not results:
        return f"No fraud advisories found matching query: {query}"
    
    output = []
    for r in results:
        output.append(f"Advisory Code: {r['advisory_code']}\nTitle: {r['title']}\nIssue Date: {r['issue_date']}\nThreat Level: {r['threat_level']}\nContent: {r['content']}\n" + "-"*40)
    return "\n\n".join(output)

@mcp.tool()
def get_loan_application(application_id: str) -> str:
    """Retrieve details of a specific loan application by its ID.
    
    Args:
        application_id: The unique loan application ID (e.g., 'LAP-213').
    """
    sql = "SELECT application_id, customer_name, product_type, requested_amount, submission_date, status, kyc_status, verification_details FROM loan_applications WHERE application_id = ?"
    results = query_db(sql, (application_id,))
    if not results:
        return f"No loan application found with ID: {application_id}"
    
    r = results[0]
    return f"Application ID: {r['application_id']}\nCustomer Name: {r['customer_name']}\nProduct Type: {r['product_type']}\nRequested Amount: {r['requested_amount']}\nSubmission Date: {r['submission_date']}\nStatus: {r['status']}\nKYC Status: {r['kyc_status']}\nVerification Details: {r['verification_details']}"

@mcp.tool()
def list_pending_loan_applications() -> str:
    """List all pending loan applications currently undergoing review with their KYC status and verification details."""
    sql = "SELECT application_id, customer_name, product_type, requested_amount, status, kyc_status, verification_details FROM loan_applications WHERE status = 'PENDING_APPROVAL' OR status = 'UNDER_REVIEW'"
    results = query_db(sql)
    if not results:
        return "No pending loan applications found."
    
    output = []
    for r in results:
        output.append(f"Application ID: {r['application_id']} | Customer: {r['customer_name']} | Product: {r['product_type']} | Amount: {r['requested_amount']} | Status: {r['status']} | KYC: {r['kyc_status']} | Verification: {r['verification_details']}")
    return "\n".join(output)

@mcp.tool()
def search_rbi_circulars(query: str) -> str:
    """Search for past and present RBI circulars.
    
    Args:
        query: Search term (e.g., 'V-CIP', 'KYC', 'Master Direction').
    """
    sql = "SELECT circular_number, title, issue_date, effective_date, products_affected, content, status FROM rbi_circulars WHERE title LIKE ? OR content LIKE ?"
    term = f"%{query}%"
    results = query_db(sql, (term, term))
    if not results:
        return f"No RBI circulars found matching query: {query}"
    
    output = []
    for r in results:
        output.append(f"Circular Number: {r['circular_number']}\nTitle: {r['title']}\nIssue Date: {r['issue_date']}\nEffective Date: {r['effective_date']}\nProducts Affected: {r['products_affected']}\nStatus: {r['status']}\nContent: {r['content']}\n" + "-"*40)
    return "\n\n".join(output)

if __name__ == "__main__":
    mcp.run()
