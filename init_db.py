import sqlite3
import os
import random

def init_database():
    db_path = "bank_knowledge.db"
    
    # Remove existing db file if any to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. RBI Circulars
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rbi_circulars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        circular_number TEXT UNIQUE,
        title TEXT,
        issue_date TEXT,
        effective_date TEXT,
        products_affected TEXT,
        content TEXT,
        status TEXT
    )
    """)
    
    # 2. Internal SOPs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internal_sops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sop_code TEXT UNIQUE,
        title TEXT,
        product_type TEXT,
        last_updated TEXT,
        content TEXT
    )
    """)
    
    # 3. Fraud Advisories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fraud_advisories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        advisory_code TEXT UNIQUE,
        title TEXT,
        issue_date TEXT,
        threat_level TEXT,
        content TEXT
    )
    """)
    
    # 4. Loan Applications (Pending / Active)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications (
        application_id TEXT PRIMARY KEY,
        customer_name TEXT,
        product_type TEXT,
        requested_amount REAL,
        submission_date TEXT,
        status TEXT,
        kyc_status TEXT,
        verification_details TEXT
    )
    """)
    
    # --- Generate 55 RBI Circulars with specific product correlations ---
    circular_templates = {
        "Gold Loan": [
            ("Master Direction - Gold Loan LTV Limits and Collateral Valuation", 
             "LTV Ratios for loans against gold ornaments must not exceed 75%. Valuation of gold ornaments must be done by an approved bank appraiser. Storage of gold keys must follow dual-custody verification rules at the branch.")
        ],
        "Home Loan": [
            ("LTV Ratios and Risk Weights for Home Loans and Housing Finance", 
             "For Home Loans up to INR 30 Lakh, the LTV ratio can go up to 90%. For loans between 30 Lakh and 75 Lakh, LTV is capped at 80%. Risk weight of 35% applies to all compliant residential housing loans.")
        ],
        "Personal Loan": [
            ("Digital Lending Guidelines - Mandating direct bank account disbursal", 
             "Personal Loans disbursed online via third-party fintech applications must go directly from the bank's core system into the borrower's verified bank account without passing through escrow/pool accounts of Lending Service Providers (LSPs).")
        ],
        "Education Loan": [
            ("Credit Guarantee Fund Scheme for Education Loans (CGFSEL)", 
             "Education Loans up to INR 7.5 Lakh qualify for the Credit Guarantee Fund. Banks are prohibited from asking for third-party collateral or parents' security for education loans below the 7.5 Lakh threshold.")
        ],
        "Business Loan": [
            ("Prudential Framework for Resolution of Stressed Assets for MSME Business Loans", 
             "MSME and Business Loan accounts showing sign of stress (SMA-1 or SMA-2) must be evaluated for restructuring within 30 days. Handover to recovery agents is strictly prohibited without a 15-day notice.")
        ]
    }
    
    circular_topics = [
        ("KYC Master Directions", "Guidelines on Customer Due Diligence and onboarding security."),
        ("Cyber Security Controls", "Framework for mitigating online transaction risks."),
        ("Microfinance Lending", "Interest rate caps and loan limits for microfinance portfolios."),
        ("Outsourcing of Financial Services", "Compliance requirements for onboarding third-party agents."),
        ("Credit Card Operations", "Rules governing interest rates, billing cycles, and grievance redressals."),
        ("Infrastructure Bond Issuance", "Guidelines for long-term bond raising for infrastructure lending."),
        ("Cooperative Bank Capital Adequacy", "Capital requirement updates for urban cooperative institutions."),
        ("Priority Sector Lending Targets", "Revised goals for agricultural and MSME credit sectors.")
    ]
    
    for i in range(1, 56):
        c_num = f"RBI/2026-27/{i:03d}"
        
        # Inject explicit targeted circulars at specific IDs
        if i == 45:
            title = "Amendment to Master Direction on Video-based Customer Identification Process (V-CIP)"
            content = "Effective July 1, 2026, all non-face-to-face onboarding must utilize Video-based Customer Identification Process (V-CIP). Physical in-person verification is no longer mandatory if V-CIP is completed. The V-CIP session must be live, require real-time geographic location (geo-tagging) verification to ensure the customer is within India, and perform live facial matching against the Aadhaar/PAN database. Any digital accounts opened without live V-CIP or with location mismatches are deemed non-compliant and must be frozen within 7 days of opening."
            products = "Digital Onboarding, Savings Accounts, Personal Loan, Retail Loans"
            status = "ACTIVE"
        elif i == 10:
            title = "Master Direction - KYC (Know Your Customer) Direction, 2021"
            content = "Under the 2021 directives, banks are required to conduct physical, in-person verification (IPV) of customers during account opening. F2F (Face-to-Face) onboarding requires a bank officer to physically inspect the original officially valid documents (OVD) and verify the customer's presence. Digital onboarding is restricted to basic e-KYC accounts with a balance cap of INR 1,00,000."
            products = "All Deposits, Home Loan, Personal Loan, Gold Loan"
            status = "SUPERSEDED"
        elif i % 5 == 0:
            # Map products to circulars systematically
            p_type = list(circular_templates.keys())[(i // 5) % 5]
            template = circular_templates[p_type][0]
            title = f"{template[0]} (Revision {i})"
            content = template[1] + f" [Section {i} compliance reference]."
            products = p_type
            status = "ACTIVE"
        else:
            topic = circular_topics[i % len(circular_topics)]
            title = f"Master Direction - {topic[0]} (Revision {i})"
            content = f"Regulatory guideline detailing the compliance mandates for {topic[0]}. {topic[1]} Regulated Entities are advised to update their internal workflows to adhere to these revisions. Periodic reviews will be conducted by RBI inspection officers."
            products = "All Financial Products"
            status = random.choice(["ACTIVE", "SUPERSEDED", "UNDER_REVIEW"])
            
        cursor.execute("""
        INSERT OR IGNORE INTO rbi_circulars (circular_number, title, issue_date, effective_date, products_affected, content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (c_num, title, f"2026-03-{i%28+1:02d}", f"2026-04-{i%28+1:02d}", products, content, status))

    # --- Generate 55 Internal SOPs ---
    sop_products = ["KYC Onboarding", "Gold Loan", "Personal Loan", "Home Loan", "Business Loan", "Credit Card", "Education Loan", "Branch Security", "Grievance Redressal", "Treasury Operations"]
    for i in range(1, 56):
        sop_code = f"SOP-KYC-{i:03d}"
        prod = sop_products[i % len(sop_products)]
        if i == 1:
            title = "Standard Operating Procedure for Customer Onboarding and KYC Verification"
            content = "Process Workflow: 1. Collect physical photocopy of OVD (Aadhaar/PAN/Passport). 2. A branch officer must perform physical In-Person Verification (IPV) at the customer's address or branch. 3. Sign the physical KYC form with stamp 'Originals Verified'. Note: Remote digital onboarding is not permitted for loans above INR 1,00,000 without branch manager approval and subsequent physical verification within 15 days."
        elif i == 2:
            title = "Retail Personal Loan Processing Guidelines"
            content = "Personal loans are processed via the digital portal. For digital applicants, KYC is initiated through an online document upload. The application is marked as 'KYC-PENDING' until the customer visits a branch or a bank representative goes to their home for physical document verification."
        else:
            title = f"SOP for {prod} Processing (Internal v{i})"
            content = f"Step-by-step operating guidelines for executing {prod} workflows. Follow the standard checks, cross-verify customer signatures, ensure adequate collateral valuation where applicable, and seek branch manager signoff for transactions exceeding regional limits."
            
        cursor.execute("""
        INSERT OR IGNORE INTO internal_sops (sop_code, title, product_type, last_updated, content)
        VALUES (?, ?, ?, ?, ?)
        """, (sop_code, title, prod, f"2025-06-{i%28+1:02d}", content))

    # --- Generate 55 Fraud Advisories ---
    fraud_threats = [
        ("GPS Spoofing", "Applicants utilizing mock location apps to bypass local borders during remote sessions."),
        ("Deepfake Face Matching", "Use of virtual camera software and synthetic deepfake videos to bypass video matching."),
        ("Sim Swap Fraud", "Targeted attacks where fraudsters clone SIM cards to intercept OTP credentials."),
        ("Mule Accounts", "Onboarding of dummy accounts to route laundered cash via digital transfers."),
        ("Document Modification", "Sophisticated editing of PDF utility bills and Aadhaar files using graphic tools.")
    ]
    for i in range(1, 56):
        adv_code = f"ADV-2026-{i:03d}"
        threat = fraud_threats[i % len(fraud_threats)]
        if i == 12:
            title = "Threat Alert: GPS Spoofing and Deepfake Face-Matching in Video KYC"
            content = "We have observed instances of fraud where remote applicants use virtual camera software to feed synthetic deepfake videos during Video KYC sessions. Furthermore, applicants use GPS spoofing applications to bypass geo-fencing checks. Verification officers must verify the live stream for facial micro-expressions and cross-examine the IP location against the reported GPS geo-tag."
            threat_level = "HIGH"
        else:
            title = f"Threat Alert: {threat[0]} Risks in Retail Banking"
            content = f"Vulnerability warning regarding {threat[0]}. {threat[1]} Verification officers and automated security systems must implement verification steps to identify anomalies and flag suspicious onboarding requests immediately."
            threat_level = random.choice(["HIGH", "MEDIUM", "LOW"])
            
        cursor.execute("""
        INSERT OR IGNORE INTO fraud_advisories (advisory_code, title, issue_date, threat_level, content)
        VALUES (?, ?, ?, ?, ?)
        """, (adv_code, title, f"2026-05-{i%28+1:02d}", threat_level, content))

    # --- Generate 55 Loan Applications ---
    names = ["John Doe", "Jane Smith", "Alex Johnson", "Emily Davis", "Michael Brown", "Sarah Miller", "David Wilson", "Taylor Moore", "Chris Taylor", "Jessica Anderson"]
    statuses = ["PENDING_APPROVAL", "UNDER_REVIEW", "APPROVED", "REJECTED"]
    products = ["Personal Loan", "Home Loan", "Gold Loan", "Education Loan", "Business Loan"]
    
    # LAP-213 remains our primary V-CIP violator case
    for i in range(201, 256):
        app_id = f"LAP-{i}"
        prod_type = random.choice(products)
        cust_name = f"{random.choice(names)} ({i})"
        amount = float(random.randint(50000, 5000000))
        
        if i == 213:
            cust_name = "John Doe"
            prod_type = "Personal Loan"
            amount = 250000.00
            status = "PENDING_APPROVAL"
            kyc_status = "DOCUMENT_UPLOADED"
            verification_details = "Customer uploaded scanned Aadhaar and PAN online. No physical verification has been conducted yet. No Video KYC (V-CIP) was performed during the online application submission."
        elif i == 214:
            cust_name = "Jane Smith"
            prod_type = "Home Loan"
            amount = 4500000.00
            status = "UNDER_REVIEW"
            kyc_status = "VERIFIED_PHYSICAL"
            verification_details = "Branch officer visited the residential address and verified original Aadhaar and PAN. Signed physical IPV form attached."
        else:
            # Map products to match generated apps
            if i % 5 == 0:
                prod_type = "Gold Loan"
                amount = float(random.randint(50000, 500000))
            elif i % 5 == 1:
                prod_type = "Home Loan"
                amount = float(random.randint(1500000, 8000000))
            elif i % 5 == 2:
                prod_type = "Personal Loan"
                amount = float(random.randint(50000, 1000000))
            elif i % 5 == 3:
                prod_type = "Education Loan"
                amount = float(random.randint(100000, 1500000))
            else:
                prod_type = "Business Loan"
                amount = float(random.randint(500000, 5000000))
                
            status = random.choice(statuses)
            # Create a mix of digital and physical onboarding cases
            is_digital = random.choice([True, False])
            if is_digital:
                kyc_status = random.choice(["DOCUMENT_UPLOADED", "V_CIP_COMPLETED"])
                if kyc_status == "V_CIP_COMPLETED":
                    verification_details = "Remote Video KYC completed. Aadhaar e-KYC verified. Face matching matched 98.4%. Geo-tag verified within India (Maharashtra)."
                else:
                    verification_details = "Online document upload completed. Video KYC session has not been initiated. Verification pending."
            else:
                kyc_status = "VERIFIED_PHYSICAL"
                verification_details = "Physical IPV completed by branch officer at customer residence. Originals verified."
                
        cursor.execute("""
        INSERT OR IGNORE INTO loan_applications (application_id, customer_name, product_type, requested_amount, submission_date, status, kyc_status, verification_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, cust_name, prod_type, amount, f"2026-06-{i%28+1:02d}", status, kyc_status, verification_details))

    conn.commit()
    conn.close()
    print("Database re-initialized with targeted product-specific RBI circulars.")

if __name__ == "__main__":
    init_database()
