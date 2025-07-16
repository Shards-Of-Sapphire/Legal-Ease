import os
import logging
import json
import re
import base64
from io import BytesIO
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

# Image processing for OCR
try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

# PDF processing
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# DOCX processing
try:
    from docx import Document
except ImportError:
    Document = None

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    logging.warning(f"NLTK download warning: {e}")

# Initialize summarizer
LANGUAGE = "english"
stemmer = Stemmer(LANGUAGE)
summarizer = LsaSummarizer(stemmer)
summarizer.stop_words = get_stop_words(LANGUAGE)

def extract_text_from_file(filepath):
    """Extract text from PDF, DOCX, or TXT files"""
    file_extension = filepath.lower().split('.')[-1]
    
    if file_extension == 'txt':
        return extract_text_from_txt(filepath)
    elif file_extension == 'pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension == 'docx':
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def extract_text_from_image(image_data):
    """Extract text from image using OCR (Optical Character Recognition)"""
    if Image is None or pytesseract is None:
        raise ImportError("PIL and pytesseract are required for image processing")
    
    try:
        # Handle base64 image data
        if isinstance(image_data, str):
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        else:
            # Handle file path
            image = Image.open(image_data)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using OCR with enhanced settings for legal documents
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()[]{}"-' + "'"
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Clean up the extracted text
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive line breaks
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        if not text:
            raise Exception("No text could be extracted from the image")
        
        return text
        
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

def extract_text_from_txt(filepath):
    """Extract text from TXT file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(filepath, 'r', encoding='latin-1') as file:
            return file.read()

def extract_text_from_pdf(filepath):
    """Extract text from PDF file using PyMuPDF"""
    if fitz is None:
        raise ImportError("PyMuPDF is required for PDF processing")
    
    text = ""
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(filepath):
    """Extract text from DOCX file using python-docx"""
    if Document is None:
        raise ImportError("python-docx is required for DOCX processing")
    
    try:
        doc = Document(filepath)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

def summarize_legal_document(text):
    """Summarize legal document using enhanced extractive summarization"""
    if not text.strip():
        raise Exception("No text provided for summarization")
    
    try:
        # Try advanced summarization first
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Parse the text
            parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
            
            # Calculate appropriate sentence count based on document length
            word_count = len(text.split())
            sentence_count = max(3, min(8, word_count // 100))  # More precise scaling
            
            summary_sentences = summarizer(parser.document, sentence_count)
            summary_text = ' '.join([str(sentence) for sentence in summary_sentences])
            
            # Enhance summary with document type detection
            summary_text = enhance_summary_with_context(summary_text, text)
            
        except Exception as e:
            logging.warning(f"SUMY summarization failed: {e}")
            summary_text = create_intelligent_summary(text)
        
        # Identify key clauses with enhanced detection
        key_clauses = identify_key_clauses_enhanced(text)
        
        return {
            'summary': summary_text,
            'key_clauses': key_clauses
        }
        
    except Exception as e:
        return fallback_summarize(text)

def identify_key_clauses(text):
    """Identify key legal clauses using pattern matching"""
    clauses = []
    
    # Common legal clause patterns
    clause_patterns = {
        'Termination': [
            r'termination', r'terminate', r'end of agreement', r'expiry', r'expire'
        ],
        'Confidentiality': [
            r'confidential', r'non-disclosure', r'proprietary information', r'trade secret'
        ],
        'Governing Law': [
            r'governing law', r'jurisdiction', r'laws of', r'legal system'
        ],
        'Payment Terms': [
            r'payment', r'fee', r'compensation', r'remuneration', r'invoice'
        ],
        'Liability': [
            r'liability', r'damages', r'indemnify', r'liable', r'responsible'
        ],
        'Intellectual Property': [
            r'intellectual property', r'copyright', r'patent', r'trademark', r'proprietary'
        ],
        'Force Majeure': [
            r'force majeure', r'act of god', r'unforeseeable circumstances'
        ],
        'Dispute Resolution': [
            r'dispute', r'arbitration', r'mediation', r'resolution', r'court'
        ]
    }
    
    # Split text into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for clause_type, patterns in clause_patterns.items():
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Ignore very short sentences
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        clauses.append({
                            'type': clause_type,
                            'content': sentence,
                            'explanation': f"This section relates to {clause_type.lower()} provisions in the document."
                        })
                        break
                if len(clauses) >= 8:  # Limit to prevent too many clauses
                    break
    
    return clauses

def enhance_summary_with_context(summary_text, full_text):
    """Add contextual information to make summary more legible"""
    # Detect document type
    doc_type = detect_document_type(full_text)
    
    # Add document type context
    if doc_type != "Legal Document":
        summary_text = f"This {doc_type} contains the following key provisions: {summary_text}"
    
    # Add readability improvements
    summary_text = improve_readability(summary_text)
    
    return summary_text

def detect_document_type(text):
    """Detect the type of legal document"""
    text_lower = text.lower()
    
    document_types = {
        'Non-Disclosure Agreement': ['non-disclosure', 'nda', 'confidential', 'proprietary information'],
        'Employment Agreement': ['employment', 'employee', 'employer', 'job', 'salary', 'benefits'],
        'Service Agreement': ['service', 'services', 'provider', 'client', 'deliverables'],
        'Purchase Agreement': ['purchase', 'buyer', 'seller', 'goods', 'merchandise'],
        'License Agreement': ['license', 'licensing', 'intellectual property', 'software', 'patent'],
        'Lease Agreement': ['lease', 'rent', 'tenant', 'landlord', 'property'],
        'Partnership Agreement': ['partnership', 'partner', 'joint venture', 'collaboration'],
        'Terms of Service': ['terms of service', 'terms and conditions', 'user agreement', 'website']
    }
    
    for doc_type, keywords in document_types.items():
        if any(keyword in text_lower for keyword in keywords):
            return doc_type
    
    return "Legal Document"

def improve_readability(text):
    """Improve text readability and structure"""
    # Remove excessive legal jargon explanations
    text = re.sub(r'\b(hereinafter|whereas|whereby|hereof|thereof)\b', '', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Ensure proper sentence structure
    text = text.strip()
    if not text.endswith('.'):
        text += '.'
    
    return text

def create_intelligent_summary(text):
    """Create an intelligent summary when SUMY fails"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return "Unable to generate summary from the provided text."
    
    # Score sentences based on legal importance
    scored_sentences = []
    for sentence in sentences:
        score = calculate_sentence_importance(sentence)
        scored_sentences.append((sentence, score))
    
    # Sort by score and take top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    top_sentences = [sentence for sentence, score in scored_sentences[:5]]
    
    # Arrange in logical order if possible
    summary_text = '. '.join(top_sentences) + '.'
    
    return improve_readability(summary_text)

def calculate_sentence_importance(sentence):
    """Calculate the importance score of a sentence for legal documents"""
    importance_keywords = {
        'high': ['agreement', 'party', 'shall', 'must', 'required', 'obligation', 'rights', 'liability'],
        'medium': ['may', 'payment', 'termination', 'confidential', 'breach', 'damages'],
        'low': ['including', 'such', 'other', 'any', 'all', 'each']
    }
    
    sentence_lower = sentence.lower()
    score = 0
    
    # High importance keywords
    for keyword in importance_keywords['high']:
        if keyword in sentence_lower:
            score += 3
    
    # Medium importance keywords
    for keyword in importance_keywords['medium']:
        if keyword in sentence_lower:
            score += 2
    
    # Low importance keywords (negative scoring)
    for keyword in importance_keywords['low']:
        if keyword in sentence_lower:
            score -= 1
    
    # Bonus for sentence length (moderate length preferred)
    word_count = len(sentence.split())
    if 10 <= word_count <= 30:
        score += 2
    elif word_count < 5:
        score -= 2
    
    return score

def identify_key_clauses_enhanced(text):
    """Enhanced key clause identification with better accuracy"""
    clauses = []
    
    # More specific and comprehensive clause patterns
    clause_patterns = {
        'Termination': {
            'patterns': [
                r'terminat[ei].*?(?:agreement|contract)',
                r'end.*?(?:agreement|contract)',
                r'expir[ye].*?(?:agreement|contract)',
                r'dissolution.*?(?:agreement|contract)'
            ],
            'description': 'Specifies conditions under which the agreement can be ended'
        },
        'Confidentiality': {
            'patterns': [
                r'confidential.*?information',
                r'non-disclosure',
                r'proprietary.*?information',
                r'trade.*?secret',
                r'disclose.*?information'
            ],
            'description': 'Protects sensitive information from being shared'
        },
        'Payment Terms': {
            'patterns': [
                r'payment.*?(?:due|terms|schedule)',
                r'invoice.*?(?:payment|terms)',
                r'compensation.*?(?:amount|terms)',
                r'fee.*?(?:payment|schedule)',
                r'remuneration'
            ],
            'description': 'Outlines payment obligations and schedules'
        },
        'Liability': {
            'patterns': [
                r'liability.*?(?:limited|excluded|damages)',
                r'damages.*?(?:liable|responsible)',
                r'indemnif[yi].*?(?:party|damages)',
                r'responsible.*?(?:damages|loss)'
            ],
            'description': 'Defines responsibility for damages or losses'
        },
        'Governing Law': {
            'patterns': [
                r'governing.*?law',
                r'jurisdiction.*?(?:court|law)',
                r'laws.*?of.*?(?:state|country)',
                r'legal.*?system'
            ],
            'description': 'Specifies which laws and courts have authority'
        },
        'Intellectual Property': {
            'patterns': [
                r'intellectual.*?property',
                r'copyright.*?(?:ownership|rights)',
                r'patent.*?(?:rights|ownership)',
                r'trademark.*?(?:rights|ownership)',
                r'proprietary.*?rights'
            ],
            'description': 'Addresses ownership of ideas and creative works'
        }
    }
    
    # Split text into paragraphs for better context
    paragraphs = re.split(r'\n\s*\n', text)
    
    for clause_type, clause_info in clause_patterns.items():
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > 50:  # Ignore very short paragraphs
                for pattern in clause_info['patterns']:
                    if re.search(pattern, paragraph, re.IGNORECASE):
                        # Extract relevant sentences from the paragraph
                        sentences = re.split(r'[.!?]+', paragraph)
                        relevant_sentences = []
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if len(sentence) > 20 and re.search(pattern, sentence, re.IGNORECASE):
                                relevant_sentences.append(sentence)
                        
                        if relevant_sentences:
                            clause_content = '. '.join(relevant_sentences[:2]) + '.'
                            clauses.append({
                                'type': clause_type,
                                'content': clause_content,
                                'explanation': clause_info['description']
                            })
                            break
        
        # Limit clauses to avoid overwhelming the user
        if len(clauses) >= 8:
            break
    
    return clauses

def fallback_summarize(text):
    """Fallback summarization when all else fails"""
    try:
        return {
            'summary': create_intelligent_summary(text),
            'key_clauses': identify_key_clauses_enhanced(text)
        }
    except Exception as e:
        word_count = len(text.split())
        return {
            'summary': f"This legal document contains {word_count} words and appears to cover standard legal provisions. The document includes various clauses and terms that would benefit from professional legal review.",
            'key_clauses': []
        }

def explain_legal_clause(clause_text):
    """Provide intelligent, context-aware explanation of legal clauses"""
    if not clause_text.strip():
        raise Exception("No clause text provided")
    
    try:
        clause_lower = clause_text.lower()
        
        # Analyze the clause structure and content
        explanation = analyze_clause_structure(clause_text)
        
        # Add specific interpretations based on legal patterns
        specific_explanation = get_specific_legal_interpretation(clause_text)
        
        # Combine general and specific explanations
        if specific_explanation:
            explanation = f"{specific_explanation}\n\n{explanation}"
        
        # Add practical implications
        practical_impact = get_practical_implications(clause_text)
        if practical_impact:
            explanation += f"\n\nPractical Impact: {practical_impact}"
        
        # Add context about the clause content
        explanation += f"\n\nSpecific Clause Content: \"{clause_text[:300]}{'...' if len(clause_text) > 300 else ''}\""
        
        # Add professional advice notice
        explanation += "\n\nDisclaimer: This explanation is for informational purposes only. For binding legal advice specific to your situation, consult with a qualified attorney."
        
        return explanation
        
    except Exception as e:
        raise Exception(f"Error explaining clause: {str(e)}")

def analyze_clause_structure(clause_text):
    """Analyze the structure and components of a legal clause"""
    clause_lower = clause_text.lower()
    
    # Detect obligation words
    obligation_words = ['shall', 'must', 'required', 'obligation', 'duty']
    permission_words = ['may', 'can', 'permitted', 'allowed']
    prohibition_words = ['shall not', 'cannot', 'prohibited', 'forbidden']
    
    analysis = []
    
    if any(word in clause_lower for word in obligation_words):
        analysis.append("This clause creates binding obligations - someone must do something.")
    
    if any(word in clause_lower for word in permission_words):
        analysis.append("This clause grants permissions - someone is allowed to do something.")
    
    if any(word in clause_lower for word in prohibition_words):
        analysis.append("This clause contains prohibitions - someone is forbidden from doing something.")
    
    # Detect conditions
    if any(word in clause_lower for word in ['if', 'when', 'unless', 'provided that']):
        analysis.append("This clause is conditional - it only applies under certain circumstances.")
    
    # Detect time elements
    if any(word in clause_lower for word in ['within', 'days', 'months', 'years', 'immediately']):
        analysis.append("This clause has time-sensitive elements - specific deadlines or time periods apply.")
    
    if not analysis:
        return "This clause establishes terms and conditions that parties must follow."
    
    return ' '.join(analysis)

def get_specific_legal_interpretation(clause_text):
    """Provide specific interpretations based on legal clause patterns"""
    clause_lower = clause_text.lower()
    
    # Comprehensive legal term interpretations
    interpretations = {
        'termination': {
            'patterns': ['terminat', 'end', 'expir', 'dissolution'],
            'explanation': "Termination Clause: This defines when and how the agreement can be ended. It typically specifies notice periods, conditions that trigger termination, and what happens to obligations after termination."
        },
        'confidentiality': {
            'patterns': ['confidential', 'non-disclosure', 'proprietary', 'trade secret'],
            'explanation': "Confidentiality Clause: This protects sensitive information by legally requiring parties to keep certain information secret and not share it with unauthorized parties."
        },
        'indemnification': {
            'patterns': ['indemnif', 'hold harmless', 'defend'],
            'explanation': "Indemnification Clause: This means one party agrees to protect and compensate the other party for certain types of losses, damages, or legal claims."
        },
        'liability': {
            'patterns': ['liability', 'damages', 'responsible', 'liable'],
            'explanation': "Liability Clause: This defines who is responsible for damages, losses, or injuries, and may limit or exclude certain types of liability."
        },
        'governing law': {
            'patterns': ['governing law', 'jurisdiction', 'laws of'],
            'explanation': "Governing Law Clause: This specifies which state's or country's laws will be used to interpret the agreement and which courts will handle disputes."
        },
        'force majeure': {
            'patterns': ['force majeure', 'act of god', 'unforeseeable'],
            'explanation': "Force Majeure Clause: This excuses performance when extraordinary circumstances beyond anyone's control (like natural disasters or wars) make it impossible to fulfill obligations."
        },
        'assignment': {
            'patterns': ['assign', 'transfer', 'delegate'],
            'explanation': "Assignment Clause: This controls whether and how the rights and obligations under the agreement can be transferred to another party."
        },
        'severability': {
            'patterns': ['severab', 'invalid', 'unenforceable'],
            'explanation': "Severability Clause: This ensures that if one part of the agreement is found to be invalid or unenforceable, the rest of the agreement remains in effect."
        },
        'amendment': {
            'patterns': ['amend', 'modify', 'change'],
            'explanation': "Amendment Clause: This specifies how changes to the agreement can be made, typically requiring written consent from all parties."
        },
        'dispute resolution': {
            'patterns': ['dispute', 'arbitration', 'mediation', 'litigation'],
            'explanation': "Dispute Resolution Clause: This establishes the process for resolving disagreements, which may include negotiation, mediation, arbitration, or court proceedings."
        }
    }
    
    for term, info in interpretations.items():
        if any(pattern in clause_lower for pattern in info['patterns']):
            return info['explanation']
    
    return None

def get_practical_implications(clause_text):
    """Explain the practical implications of a legal clause"""
    clause_lower = clause_text.lower()
    
    implications = []
    
    # Financial implications
    if any(word in clause_lower for word in ['payment', 'fee', 'cost', 'expense', 'penalty']):
        implications.append("This may have financial implications - money may need to be paid or penalties may apply.")
    
    # Time implications
    if any(word in clause_lower for word in ['within', 'days', 'deadline', 'immediately']):
        implications.append("This has time-sensitive requirements - failing to meet deadlines could have consequences.")
    
    # Performance implications
    if any(word in clause_lower for word in ['perform', 'deliver', 'complete', 'fulfill']):
        implications.append("This requires specific actions to be taken - failure to perform could result in breach of contract.")
    
    # Risk implications
    if any(word in clause_lower for word in ['liability', 'damages', 'loss', 'harm']):
        implications.append("This involves risk allocation - it determines who bears responsibility for potential problems.")
    
    # Confidentiality implications
    if any(word in clause_lower for word in ['confidential', 'secret', 'proprietary', 'disclose']):
        implications.append("This affects information sharing - unauthorized disclosure could have legal consequences.")
    
    return ' '.join(implications) if implications else None
