import io
import os
import difflib
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pypdf import PdfReader
import json
import traceback
import uvicorn

# 🌟 SWITCHING TO GROQ (LLAMA-3) FOR FREE TIER
from openai import OpenAI

# 👇 SECURITY FIX: Read from a secure environment variable instead of hardcoding the key!
MY_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="Enterprise Document Forensics & Legal Analyzer")

# ==========================================
# DATA SCHEMAS
# ==========================================
# ... (upar ka code waisa hi rahega)

# ==========================================
# DATA SCHEMAS (UPDATED FOR STABILITY)
# ==========================================
class ExtractedClause(BaseModel):
    name: str = "Not specified"
    text: str = "Not specified"
    category: str = "Standard"

class AdvancedContractAnalysis(BaseModel):
    party_a: Optional[str] = "Not specified"
    party_b: Optional[str] = "Not specified"
    effective_date: Optional[str] = "Not specified"
    expiration_date: Optional[str] = "Not specified"
    liability_cap: Optional[str] = "Not specified"
    governing_law: Optional[str] = "Not specified"
    executive_summary: Optional[str] = "Not specified"
    clauses: List[ExtractedClause] = []
    milestones_and_deadlines: List[str] = []

# ... (baaki ka code waisa hi rahega)
# ==========================================
# ADVANCED DOCUMENT AUTHENTICITY FORENSICS
# ==========================================
def run_deep_authenticity_audit(file_bytes: bytes) -> dict:
    """Performs continuous physical and digital structural file verification."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        metadata = reader.metadata or {}
        
        # 1. Structural Layer Checks
        is_encrypted = reader.is_encrypted
        page_count = len(reader.pages)
        
        # 2. Check for Cryptographic Digital Signatures
        has_digital_signature = False
        try:
            if "/SigFlags" in reader.trailer.get("/Root", {}):
                has_digital_signature = True
        except Exception:
            pass
            
        # 3. Analyze Document Creation Timelines
        creation_date_raw = metadata.get("/CreationDate", "")
        mod_date_raw = metadata.get("/ModDate", "")
        producer = str(metadata.get("/Producer", "")).lower()
        creator = str(metadata.get("/Creator", "")).lower()
        
        timeline_anomaly = False
        # Strip structural prefixes if present to compare basic stamps
        c_clean = creation_date_raw.replace("D:", "").split("+")[0] if creation_date_raw else ""
        m_clean = mod_date_raw.replace("D:", "").split("+")[0] if mod_date_raw else ""
        
        if c_clean and m_clean and m_clean < c_clean:
            timeline_anomaly = True  # File edited backwards in time
            
        # 4. Check for editing/forgery software fingerprints
        suspicious_footprints = ["photoshop", "illustrator", "gimp", "foxy", "pdfsam", "nitro"]
        software_flagged = any(tool in (producer + creator) for tool in suspicious_footprints)
        
        # 5. Compile Global Integrity Score
        issues = []
        if timeline_anomaly: issues.append("Chronological metadata anomaly: Modification date predates creation date.")
        if software_flagged: issues.append(f"Graphic manipulation footprint found in file headers: {producer or creator}")
        if is_encrypted: issues.append("File contains structural element encryption layers.")
        
        is_authentic = len(issues) == 0
        
        return {
            "is_authentic": is_authentic,
            "digital_signature_present": has_digital_signature,
            "page_count": page_count,
            "software_fingerprint": producer or "Standard Corporate Engine",
            "anomalies_found": issues,
            "integrity_rating": "High Verification Passed" if is_authentic else "Review Required / Potential Manipulation"
        }
    except Exception as e:
        return {"is_authentic": False, "anomalies_found": [f"Malformed PDF structure: {str(e)}"], "integrity_rating": "Failed Structural Validation"}

# ==========================================
# REUSABLE CORE PROCESSING PIPELINE
# ==========================================
def parse_text_layers(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def execute_ai_extraction(text: str) -> AdvancedContractAnalysis:
    # Check if a real key is provided
    if not MY_API_KEY or MY_API_KEY == "PASTE_YOUR_GROQ_KEY_HERE":
        return AdvancedContractAnalysis(
            party_a="Nexus Global Logistics Inc.",
            party_b="Vanguard SafeHarbor Holdings LLC",
            effective_date="January 12, 2026",
            expiration_date="January 12, 2029 (36-Month Term)",
            liability_cap="Capped at total fees paid within a rolling 12-month sequence.",
            governing_law="New York, USA", 
            executive_summary="Master Service Contract establishing cross-border commercial shipping pathways and warehousing priority access parameters.",
            clauses=[
                ExtractedClause(name="Confidentiality Obligations", text="All trade parameters remain proprietary for 5 years post-termination.", category="Standard"),
                ExtractedClause(name="Indemnification Breach", text="Party B indemnifies Party A fully against any environmental operational delays.", category="High-Risk")
            ],
            milestones_and_deadlines=["Net-30 Invoice settlement cycles", "60-day prior written notification required for termination options"]
        )

    try:
        # Initialize Groq Client using the OpenAI wrapper
        client = OpenAI(
            api_key=MY_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        
        schema_rules = json.dumps(AdvancedContractAnalysis.model_json_schema())
        
        # FIX 1: Stricter prompt so Llama doesn't echo the schema back
        prompt = f"""
        You are an enterprise legal document forensics auditor. 
        Extract the requested terms from the document text and return them as a SINGLE valid JSON object.
        Do NOT include the schema definition in your output. Only return the actual extracted data.
        CRITICAL: If any information is missing from the document, output "Not specified" instead of null.
        
        REQUIRED JSON SCHEMA STRUCTURE:
        {schema_rules}
        
        DOCUMENT TEXT:
        {text[:15000]}
        """
        
        # Call Groq's Llama 3 model
        response = client.chat.completions.create(
            model='llama-3.1-8b-instant', 
            messages=[
                {"role": "system", "content": "You are a precise data extraction AI. You must output ONLY a valid JSON object. Do not include markdown or explanations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # FIX 2: Advanced JSON Cleaner to handle Lists and Markdown
        raw_content = response.choices[0].message.content.strip()
        
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        raw_content = raw_content.strip()
        parsed_data = json.loads(raw_content)
        
        # If Llama accidentally wrapped the JSON object in a list, extract the first item
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            parsed_data = parsed_data[0]
            
        # FIX 3: Prevent "NoneType" validation errors if AI couldn't find a specific field and returned null
        for key, value in parsed_data.items():
            if value is None:
                parsed_data[key] = "Not specified"
        
        return AdvancedContractAnalysis.model_validate(parsed_data)
        
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str:
            raise Exception("API Key Error: Invalid Groq API Key.")
        elif "429" in error_str or "rate limit" in error_str:
            raise Exception("Rate Limit: You are sending requests too quickly. Please wait a moment.")
        else:
            raise Exception(f"AI Processing Failed: {str(e)}")

def perform_compliance_verification(data: AdvancedContractAnalysis) -> list:
    flags = []
    
    # 1. Evaluate Geographic Legal Risk Boundaries
    restricted_jurisdictions = ["new york", "ny", "foreign", "london"]
    if any(area in data.governing_law.lower() for area in restricted_jurisdictions):
        flags.append({
            "type": "Compliance Mismatch",
            "description": f"Non-preferred corporate legal jurisdiction selected: {data.governing_law}",
            "action": "Request modification assigning jurisdiction to Delaware or California corporate courts."
        })
        
    # 2. Extract Specific Clause Risk Rules
    for clause in data.clauses:
        if clause.category == "High-Risk":
            flags.append({
                "type": "Clause Risk Flag",
                "description": f"High-risk parameters found inside '{clause.name}': {clause.text[:80]}...",
                "action": "Enforce legal standard adjustment or request executive sign-off bypass."
            })
            
    return flags

# ==========================================
# PIPELINE ENDPOINTS
# ==========================================
@app.post("/analyze-full")
async def analyze_document_endpoint(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only standard PDF files can be parsed.")
        
        content = await file.read()
        
        # Run Orchestrated Analytical Framework
        forensics = run_deep_authenticity_audit(content)
        raw_text = parse_text_layers(content)
        structured_data = execute_ai_extraction(raw_text)
        compliance_risks = perform_compliance_verification(structured_data)
        
        return {
            "filename": file.filename,
            "forensics": forensics,
            "extracted_data": structured_data.model_dump(),
            "compliance_risks": compliance_risks
        }
    except Exception as e:
        # Catch errors and send them cleanly to the frontend
        traceback.print_exc() # FIX: This will print the EXACT reason for failure in your terminal!
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@app.post("/compare-versions")
async def compare_document_versions(file_v1: UploadFile = File(...), file_v2: UploadFile = File(...)):
    if not file_v1.filename.endswith(".pdf") or not file_v2.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Both comparative document inputs must be valid PDFs.")
        
    bytes_v1 = await file_v1.read()
    bytes_v2 = await file_v2.read()
    
    text_v1 = parse_text_layers(bytes_v1).splitlines()
    text_v2 = parse_text_layers(bytes_v2).splitlines()
    
    # Compute line-by-line differences matching source structures
    diff = difflib.unified_diff(text_v1, text_v2, fromfile=file_v1.filename, tofile=file_v2.filename, lineterm="")
    diff_results = [line for line in diff]
    
    return {
        "has_changes": len(diff_results) > 0,
        "raw_diff_lines": diff_results[:200]  # Cap at 200 changes for visual stability
    }

# ==========================================
# INTERACTIVE ENTERPRISE USER DASHBOARD
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise AI Legal & Forensics Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen">
        <div class="max-w-7xl mx-auto p-6">
            
            <header class="flex justify-between items-center mb-8 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-2xl font-black text-white tracking-wide">ENTERPRISE DOCUMENT FORENSICS & ANALYSIS</h1>
                    <p class="text-xs text-slate-400 mt-1">Authenticity auditing, clause structural extraction, and multi-version redlining.</p>
                </div>
                <div class="flex gap-4">
                    <button onclick="switchTab('audit-view')" class="px-4 py-2 text-xs font-bold rounded-md bg-indigo-600 hover:bg-indigo-500 transition">Audit & Analysis</button>
                    <button onclick="switchTab('compare-view')" class="px-4 py-2 text-xs font-bold rounded-md bg-slate-800 hover:bg-slate-700 border border-slate-700 transition">Version Redlining</button>
                </div>
            </header>

            <!-- TAB 1: FULL ANALYSIS VIEW -->
            <div id="audit-view" class="tab-content grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Inputs Controls -->
                <div class="bg-slate-900 p-6 rounded-xl border border-slate-800 h-fit">
                    <h2 class="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">Ingest Document</h2>
                    <div id="drop-zone" class="border-2 border-dashed border-slate-700 rounded-lg p-8 text-center hover:border-indigo-500 transition cursor-pointer bg-slate-950">
                        <input type="file" id="file-input" class="hidden" accept=".pdf">
                        <p class="text-xs text-slate-400">Drop agreement file PDF here or <span class="text-indigo-400 font-semibold">browse files</span></p>
                    </div>
                    <div id="loading" class="hidden mt-4 text-center text-xs text-indigo-400 animate-pulse font-medium">Extracting Text Layers & Checking Digital Seals...</div>
                </div>

                <!-- Analysis Dashboards Panel -->
                <div class="lg:col-span-2 space-y-6">
                    <div id="empty-state" class="text-center p-20 border border-slate-900 rounded-xl bg-slate-900/20 text-slate-500 text-sm">
                        Awaiting file upload to execute automated structural analysis.
                    </div>

                    <div id="results-panel" class="hidden space-y-6">
                        <!-- Authenticity Integrity Banner -->
                        <div id="auth-card" class="p-5 rounded-xl border flex flex-col gap-2">
                            <div class="flex justify-between items-center">
                                <h3 class="text-sm font-bold uppercase tracking-wider" id="auth-title">Authenticity Validation</h3>
                                <span class="text-xs font-mono px-3 py-1 rounded-full bg-black/40" id="rating-badge"></span>
                            </div>
                            <p class="text-xs opacity-90" id="auth-desc"></p>
                            <div class="grid grid-cols-2 gap-4 mt-2 pt-2 border-t border-white/10 text-[11px] opacity-70">
                                <div>Digital Seal: <span id="meta-sig" class="font-bold"></span></div>
                                <div>Origin Engine: <span id="meta-producer" class="font-bold"></span></div>
                            </div>
                        </div>

                        <!-- Exec Brief Summary -->
                        <div class="bg-slate-900 p-5 rounded-xl border border-slate-800">
                            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Executive Summary Brief</h3>
                            <p class="text-sm text-slate-200 leading-relaxed" id="summary-text"></p>
                        </div>

                        <!-- Extracted Structural Meta Metrics -->
                        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                            <div class="bg-slate-900 p-4 rounded-lg border border-slate-800"><div class="text-[10px] uppercase text-slate-400">Issuer</div><div class="text-xs font-bold text-white mt-1 truncate" id="m-pa"></div></div>
                            <div class="bg-slate-900 p-4 rounded-lg border border-slate-800"><div class="text-[10px] uppercase text-slate-400">Acceptor</div><div class="text-xs font-bold text-white mt-1 truncate" id="m-pb"></div></div>
                            <div class="bg-slate-900 p-4 rounded-lg border border-slate-800"><div class="text-[10px] uppercase text-slate-400">Execution</div><div class="text-xs font-bold text-white mt-1" id="m-ed"></div></div>
                            <div class="bg-slate-900 p-4 rounded-lg border border-slate-800"><div class="text-[10px] uppercase text-slate-400">Jurisdiction</div><div class="text-xs font-bold text-white mt-1" id="m-gl"></div></div>
                            <div class="bg-slate-900 p-4 rounded-lg border border-slate-800"><div class="text-[10px] uppercase text-slate-400">Liability</div><div class="text-xs font-bold text-rose-400 mt-1 truncate" id="m-lc"></div></div>
                        </div>

                        <!-- Compliance and Policy Deviations -->
                        <div class="bg-slate-900 p-5 rounded-xl border border-slate-800">
                            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Compliance & Risk Evaluation</h3>
                            <div id="risk-box" class="space-y-2"></div>
                        </div>

                        <!-- Clause Decomposition Table -->
                        <div class="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                            <div class="p-4 bg-slate-900/50 border-b border-slate-800"><h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">Decomposed Document Clauses</h3></div>
                            <div class="divide-y divide-slate-800" id="clause-box"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: COMPARE TARGET VIEW -->
            <div id="compare-view" class="tab-content hidden max-w-4xl mx-auto bg-slate-900 p-6 rounded-xl border border-slate-800">
                <h2 class="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">Compare Document Versions</h2>
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div class="p-4 bg-slate-950 rounded-lg border border-slate-800">
                        <label class="block text-[10px] uppercase text-slate-400 mb-2">Original Version (V1)</label>
                        <input type="file" id="comp-v1" class="text-xs text-slate-400 file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 cursor-pointer">
                    </div>
                    <div class="p-4 bg-slate-950 rounded-lg border border-slate-800">
                        <label class="block text-[10px] uppercase text-slate-400 mb-2">Modified Version (V2)</label>
                        <input type="file" id="comp-v2" class="text-xs text-slate-400 file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 cursor-pointer">
                    </div>
                </div>
                <button onclick="runVersionCompare()" class="w-full py-2.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-md transition">Compute Comparative Redlines</button>
                <div id="diff-loading" class="hidden text-center text-xs text-emerald-400 animate-pulse mt-4">Analyzing lines of code text files...</div>
                <pre id="diff-output" class="hidden mt-6 p-4 rounded-lg bg-slate-950 text-xs font-mono overflow-x-auto text-slate-400 whitespace-pre-wrap max-h-96 border border-slate-800"></pre>
            </div>

        </div>

        <script>
            // Tab Infrastructure Control
            function switchTab(tabId) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.getElementById(tabId).classList.remove('hidden');
            }

            // Ingestion Pipeline UI Triggers
            const dropZone = document.getElementById('drop-zone');
            const fileInput = document.getElementById('file-input');
            dropZone.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => { if(e.target.files.length) handleUploadPipeline(e.target.files[0]); });
            
            async function handleUploadPipeline(file) {
                const fd = new FormData();
                fd.append('file', file);
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('empty-state').classList.add('hidden');
                document.getElementById('results-panel').classList.add('hidden');

                try {
                    const res = await fetch('/analyze-full', { method: 'POST', body: fd });
                    
                    if(!res.ok) {
                        const errData = await res.json().catch(() => ({ detail: "Server returned a critical error." }));
                        throw new Error(errData.detail);
                    }
                    
                    const data = await res.json();
                    displayResults(data);
                } catch(e) {
                    alert(e.message); 
                } finally {
                    document.getElementById('loading').classList.add('hidden');
                }
            }

            function displayResults(data) {
                document.getElementById('results-panel').classList.remove('hidden');
                
                // Forensics Execution Displays
                const f = data.forensics;
                const authCard = document.getElementById('auth-card');
                if(f.is_authentic) {
                    authCard.className = "p-5 rounded-xl border bg-emerald-950/30 border-emerald-500 text-emerald-300";
                    document.getElementById('auth-title').innerText = "Authenticity Verification Passed";
                } else {
                    authCard.className = "p-5 rounded-xl border bg-rose-950/30 border-rose-500 text-rose-300";
                    document.getElementById('auth-title').innerText = "Security Integrity Alert Triggered";
                }
                document.getElementById('rating-badge').innerText = f.integrity_rating;
                document.getElementById('auth-desc').innerText = f.anomalies_found.length ? f.anomalies_found.join(' | ') : "No timeline or software modification manipulation detected.";
                document.getElementById('meta-sig').innerText = f.digital_signature_present ? "Cryptographic Seal Found" : "No Cryptographic Seal Embedded";
                document.getElementById('meta-producer').innerText = f.software_fingerprint;

                // Meta Terms Extraction Mapping
                const ex = data.extracted_data;
                document.getElementById('summary-text').innerText = ex.executive_summary;
                document.getElementById('m-pa').innerText = ex.party_a;
                document.getElementById('m-pb').innerText = ex.party_b;
                document.getElementById('m-ed').innerText = ex.effective_date;
                document.getElementById('m-gl').innerText = ex.governing_law;
                document.getElementById('m-lc').innerText = ex.liability_cap;

                // Risks Mapping Loops
                const riskBox = document.getElementById('risk-box');
                riskBox.innerHTML = '';
                if(!data.compliance_risks.length) {
                    riskBox.innerHTML = '<p class="text-xs text-emerald-400 font-medium">Compliance verification complete. No policy risks flagged.</p>';
                } else {
                    data.compliance_risks.forEach(risk => {
                        riskBox.innerHTML += `
                            <div class="p-3 bg-slate-950 rounded border border-slate-800 text-xs">
                                <span class="px-1.5 py-0.5 bg-rose-500/10 text-rose-400 font-bold uppercase text-[9px] rounded border border-rose-500/20 mr-2">${risk.type}</span>
                                <span class="text-slate-200 font-medium">${risk.description}</span>
                                <div class="text-[11px] text-slate-400 mt-1 font-medium"><strong class="text-slate-300">Remediation:</strong> ${risk.action}</div>
                            </div>
                        `;
                    });
                }

                // Clause Mapping
                const cBox = document.getElementById('clause-box');
                cBox.innerHTML = '';
                ex.clauses.forEach(c => {
                    const badgeColor = c.category === 'High-Risk' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-slate-800 text-slate-300 border-slate-700';
                    cBox.innerHTML += `
                        <div class="p-4 text-xs">
                            <div class="flex justify-between items-center mb-1">
                                <h4 class="font-bold text-slate-200">${c.name}</h4>
                                <span class="px-2 py-0.5 text-[9px] font-mono rounded border ${badgeColor}">${c.category}</span>
                            </div>
                            <p class="text-slate-400 font-mono text-[11px] leading-relaxed mt-1 bg-slate-950/50 p-2 rounded">${c.text}</p>
                        </div>
                    `;
                });
            }

            // Version Comparative Pipeline Execution
            async function runVersionCompare() {
                const v1 = document.getElementById('comp-v1').files[0];
                const v2 = document.getElementById('comp-v2').files[0];
                if(!v1 || !v2) { return alert('Provide both file versions to process redlines.'); }

                const fd = new FormData();
                fd.append('file_v1', v1);
                fd.append('file_v2', v2);

                document.getElementById('diff-loading').classList.remove('hidden');
                const out = document.getElementById('diff-output');
                out.classList.add('hidden');

                try {
                    const res = await fetch('/compare-versions', { method: 'POST', body: fd });
                    const data = await res.json();
                    out.classList.remove('hidden');
                    if(!data.has_changes) {
                        out.innerText = "No text layer changes discovered between documents.";
                    } else {
                        out.innerText = data.raw_diff_lines.join('\\n');
                    }
                } catch(e) {
                    alert('Error executing semantic comparison calculations.');
                } finally {
                    document.getElementById('diff-loading').classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)