import json
import zipfile
from pathlib import Path
from app.config import SALESPACKS_DIR
from app.models.schemas import AuditResponse

class SalesPackEngine:
    """
    Bundles the complete Digital Growth Pack into a professional ZIP archive.
    """

    @staticmethod
    def build_zip(
        audit_id: str,
        safe_name: str,
        report_pdf_path: Path,
        desktop_preview_path: Path,
        mobile_preview_path: Path,
        quick_win_path: Path,
        sales_brief_path: Path,
        whatsapp_text: str,
        audit_dict: dict
    ) -> Path:
        safe_slug = "".join(c if c.isalnum() else "_" for c in safe_name.lower())[:30]
        zip_path = SALESPACKS_DIR / f"onehive-digital-growth-pack-{safe_slug}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            # 1. Report
            if report_pdf_path and report_pdf_path.exists():
                z.write(report_pdf_path, arcname="digital-growth-pack/report/digital-presence-intelligence-report.pdf")

            # 2. Website Previews
            if desktop_preview_path and desktop_preview_path.exists():
                z.write(desktop_preview_path, arcname="digital-growth-pack/website-preview/desktop-preview.png")
            if mobile_preview_path and mobile_preview_path.exists():
                z.write(mobile_preview_path, arcname="digital-growth-pack/website-preview/mobile-preview.png")

            # 3. Quick Win
            if quick_win_path and quick_win_path.exists():
                z.write(quick_win_path, arcname="digital-growth-pack/quick-win/quick-win.txt")

            # 4. Sales Assets
            if sales_brief_path and sales_brief_path.exists():
                z.write(sales_brief_path, arcname="digital-growth-pack/sales/sales-intelligence-brief.txt")
            
            z.writestr("digital-growth-pack/sales/whatsapp-message.txt", whatsapp_text)

            # 5. Metadata
            z.writestr("digital-growth-pack/metadata/audit.json", json.dumps(audit_dict, indent=2, default=str))

        print(f"[SalesPackEngine] Created complete ZIP pack: {zip_path}")
        return zip_path
