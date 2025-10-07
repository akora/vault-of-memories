"""
Document Metadata Models
Type-safe data structures for document metadata extracted by the document processor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class DocumentType(Enum):
    """Classification of document type."""
    BROCHURE = "brochure"  # 5 pages or fewer
    EBOOK = "ebook"  # More than 5 pages
    OFFICE_DOCUMENT = "office_document"  # Word/Excel/PowerPoint
    TEXT_FILE = "text_file"  # Plain text
    UNKNOWN = "unknown"


class DocumentFormat(Enum):
    """Document format classification."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"  # OpenDocument Text
    ODS = "ods"  # OpenDocument Spreadsheet
    ODP = "odp"  # OpenDocument Presentation
    UNKNOWN = "unknown"


class ScanType(Enum):
    """Document scan type classification."""
    DIGITAL_NATIVE = "digital_native"  # Born-digital document
    SCANNED = "scanned"  # Scanned from physical document
    HYBRID = "hybrid"  # Mix of digital and scanned pages
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence level for classifications."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class DocumentAuthor:
    """Author and creator information."""
    author: Optional[str] = None
    creator: Optional[str] = None  # Application that created the document
    last_modified_by: Optional[str] = None
    company: Optional[str] = None

    def has_author_info(self) -> bool:
        """Check if any author information is present."""
        return bool(self.author or self.creator or self.last_modified_by)


@dataclass
class DocumentProperties:
    """General document properties."""
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None

    def has_properties(self) -> bool:
        """Check if any properties are present."""
        return bool(self.title or self.subject or self.keywords or self.description)


@dataclass
class PDFProperties:
    """PDF-specific properties."""
    page_count: Optional[int] = None
    pdf_version: Optional[str] = None
    is_linearized: bool = False  # Fast web view
    is_encrypted: bool = False
    is_password_protected: bool = False
    has_embedded_files: bool = False
    producer: Optional[str] = None  # PDF producer software

    # Security and permissions
    allows_printing: Optional[bool] = None
    allows_copying: Optional[bool] = None
    allows_modifying: Optional[bool] = None

    def is_brochure(self) -> bool:
        """Check if page count indicates a brochure (≤5 pages)."""
        return self.page_count is not None and self.page_count <= 5

    def is_ebook(self) -> bool:
        """Check if page count indicates an ebook (>5 pages)."""
        return self.page_count is not None and self.page_count > 5


@dataclass
class OfficeProperties:
    """Microsoft Office / OpenDocument specific properties."""
    application: Optional[str] = None  # Creating application
    app_version: Optional[str] = None
    template: Optional[str] = None
    revision_number: Optional[int] = None
    total_editing_time: Optional[int] = None  # In seconds

    # Word-specific
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    paragraph_count: Optional[int] = None
    page_count: Optional[int] = None

    # Excel-specific
    sheet_count: Optional[int] = None
    sheet_names: Optional[List[str]] = None

    # PowerPoint-specific
    slide_count: Optional[int] = None

    def has_office_metadata(self) -> bool:
        """Check if Office metadata is present."""
        return bool(self.application or self.word_count or self.sheet_count or self.slide_count)


@dataclass
class TimestampInfo:
    """Document timestamp information."""
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    accessed_date: Optional[datetime] = None

    # File system timestamps (fallback)
    file_creation_date: Optional[datetime] = None
    file_modification_date: Optional[datetime] = None

    def get_best_creation_date(self) -> Optional[datetime]:
        """Get the best available creation date."""
        return self.creation_date or self.file_creation_date

    def get_best_modification_date(self) -> Optional[datetime]:
        """Get the best available modification date."""
        return self.modification_date or self.file_modification_date


@dataclass
class OCRDetection:
    """OCR and scan detection information."""
    scan_type: ScanType = ScanType.UNKNOWN
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # Detection indicators
    has_embedded_fonts: bool = False
    has_text_layer: bool = False
    image_to_text_ratio: Optional[float] = None  # Higher ratio = more likely scanned

    # Detection reasons
    detection_reason: Optional[str] = None

    def is_scanned(self) -> bool:
        """Check if document is scanned."""
        return self.scan_type == ScanType.SCANNED

    def is_digital_native(self) -> bool:
        """Check if document is digital-native."""
        return self.scan_type == ScanType.DIGITAL_NATIVE


@dataclass
class DocumentClassification:
    """Document classification results."""
    document_type: DocumentType = DocumentType.UNKNOWN
    document_format: DocumentFormat = DocumentFormat.UNKNOWN
    type_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    format_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # Classification reasons
    type_reason: Optional[str] = None
    format_reason: Optional[str] = None

    def is_brochure(self) -> bool:
        """Check if classified as brochure."""
        return self.document_type == DocumentType.BROCHURE

    def is_ebook(self) -> bool:
        """Check if classified as ebook."""
        return self.document_type == DocumentType.EBOOK

    def is_office_document(self) -> bool:
        """Check if classified as office document."""
        return self.document_type == DocumentType.OFFICE_DOCUMENT


@dataclass
class DocumentMetadata:
    """
    Complete metadata extracted from a document file.

    This is the primary data structure returned by the DocumentProcessor.
    """
    # File information
    file_path: Path
    file_name: str
    file_size: int
    mime_type: str
    file_extension: str

    # Author and creator information
    author_info: DocumentAuthor = field(default_factory=DocumentAuthor)

    # General document properties
    properties: DocumentProperties = field(default_factory=DocumentProperties)

    # Format-specific properties
    pdf_properties: Optional[PDFProperties] = None
    office_properties: Optional[OfficeProperties] = None

    # Timestamps
    timestamps: TimestampInfo = field(default_factory=TimestampInfo)

    # OCR detection
    ocr_detection: OCRDetection = field(default_factory=OCRDetection)

    # Classification
    classification: DocumentClassification = field(default_factory=DocumentClassification)

    # Raw metadata (for reference)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    # Processing information
    processing_time_ms: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and derive additional fields."""
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

        if not self.file_name:
            self.file_name = self.file_path.name

        if not self.file_extension:
            self.file_extension = self.file_path.suffix.lstrip('.').lower()

    def is_successful(self) -> bool:
        """Check if metadata extraction was successful."""
        return len(self.extraction_errors) == 0

    def has_author_metadata(self) -> bool:
        """Check if author metadata is present."""
        return self.author_info.has_author_info()

    def has_document_properties(self) -> bool:
        """Check if document properties are present."""
        return self.properties.has_properties()

    def is_password_protected(self) -> bool:
        """Check if document is password protected."""
        if self.pdf_properties:
            return self.pdf_properties.is_password_protected
        return False

    def get_page_count(self) -> Optional[int]:
        """Get page count from appropriate source."""
        if self.pdf_properties and self.pdf_properties.page_count:
            return self.pdf_properties.page_count
        if self.office_properties and self.office_properties.page_count:
            return self.office_properties.page_count
        if self.office_properties and self.office_properties.slide_count:
            return self.office_properties.slide_count
        return None

    def get_creation_date(self) -> Optional[datetime]:
        """Get the best creation date."""
        return self.timestamps.get_best_creation_date()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_extension': self.file_extension,
            'author': {
                'author': self.author_info.author,
                'creator': self.author_info.creator,
                'last_modified_by': self.author_info.last_modified_by,
            } if self.has_author_metadata() else None,
            'properties': {
                'title': self.properties.title,
                'subject': self.properties.subject,
                'keywords': self.properties.keywords,
            } if self.has_document_properties() else None,
            'pdf_info': {
                'page_count': self.pdf_properties.page_count,
                'pdf_version': self.pdf_properties.pdf_version,
                'is_encrypted': self.pdf_properties.is_encrypted,
            } if self.pdf_properties else None,
            'classification': {
                'type': self.classification.document_type.value,
                'format': self.classification.document_format.value,
                'scan_type': self.ocr_detection.scan_type.value,
                'confidence': {
                    'type': self.classification.type_confidence.value,
                    'format': self.classification.format_confidence.value,
                }
            },
            'timestamps': {
                'creation': self.get_creation_date().isoformat() if self.get_creation_date() else None,
                'modification': self.timestamps.get_best_modification_date().isoformat()
                    if self.timestamps.get_best_modification_date() else None,
            },
            'processing': {
                'time_ms': self.processing_time_ms,
                'errors': self.extraction_errors,
                'warnings': self.warnings,
            }
        }
