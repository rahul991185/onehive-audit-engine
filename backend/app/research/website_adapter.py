import re
import urllib.parse
from typing import Tuple, Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
from app.models.schemas import BusinessIdentity, EvidenceItem

class WebsiteAdapter:
    """
    Analyzes business websites for:
    - Business identification & title
    - Value proposition & positioning
    - WhatsApp / Enquiry CTAs
    - Contact methods (phone, email)
    - Mobile responsiveness (viewport)
    - Connected social profiles
    - Schema.org structured data
    """

    @staticmethod
    def resolve(url: str) -> Tuple[Optional[BusinessIdentity], List[EvidenceItem], Dict[str, Any]]:
        evidence: List[EvidenceItem] = []
        extra_data: Dict[str, Any] = {
            "social_links": [],
            "instagram_url": None,
            "facebook_url": None,
            "linkedin_url": None,
            "youtube_url": None,
            "whatsapp_link": None,
            "detected_services": [],
            "emails": [],
            "email": None,
            "phones": [],
            "tagline": None,
            "google_maps_url": None
        }

        cleaned_url = url.strip()
        if not cleaned_url.startswith(("http://", "https://")):
            cleaned_url = "https://" + cleaned_url

        try:
            resp = requests.get(
                cleaned_url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                },
                allow_redirects=True
            )
            final_url = resp.url
            html = resp.text
            status_code = resp.status_code
        except Exception as e:
            print(f"[WebsiteAdapter] HTTP Error: {e}")
            return None, [
                EvidenceItem(
                    source="Website",
                    field="Site Reachability",
                    value="Website unreachable or timed out",
                    confidence=0.9,
                    status="FAIL",
                    observation=f"Could not connect to {cleaned_url}. The domain may be inactive or server unreachable."
                )
            ], extra_data

        soup = BeautifulSoup(html, "html.parser")

        # 1. Title & Meta
        title_tag = soup.find("title")
        page_title = title_tag.get_text().strip() if title_tag else ""
        
        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        meta_desc = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""
        if meta_desc:
            sentences = [s.strip() for s in re.split(r"[.!?\n]", meta_desc) if len(s.strip()) > 15]
            if sentences:
                clean_tag = sentences[0]
                if not clean_tag.endswith("."):
                    clean_tag += "."
                if len(clean_tag) > 130:
                    clean_tag = clean_tag[:127] + "..."
                extra_data["tagline"] = clean_tag
            elif len(meta_desc) <= 130:
                extra_data["tagline"] = meta_desc

        # 2. Derive business name
        netloc = urllib.parse.urlparse(final_url).netloc.replace("www.", "")
        domain_name = netloc.split(".")[0].replace("-", " ").replace("_", " ").title()
        
        business_name = domain_name
        if page_title:
            parts = [p.strip() for p in re.split(r"[|\-–—:]", page_title) if p.strip()]
            for part in parts:
                cleaned_part = re.sub(r"\s+", " ", part).strip()
                if 2 < len(cleaned_part) < 45 and not any(k in cleaned_part.lower() for k in ["home", "welcome", "official website", "index", "leading dairy"]):
                    business_name = cleaned_part
                    break

        # Helper: Clean & Validate Phone Number
        def clean_phone(p: str) -> Optional[str]:
            p_strip = p.strip()
            digits = re.sub(r"\D", "", p_strip)
            # Filter out 10-digit unix timestamps (e.g. 1767358679) unless toll-free 1800
            if len(digits) == 10 and (digits.startswith("16") or digits.startswith("17")) and not p_strip.startswith("1800"):
                return None
            if p_strip.startswith("1800") or p_strip.startswith("+91") or (len(digits) == 10 and digits[0] in "6789") or (len(digits) in [10, 11] and digits.startswith("0")):
                return p_strip
            return None

        # Helper: Decode Cloudflare Emails
        def decode_cf_email(cf_hex: str) -> Optional[str]:
            try:
                r = int(cf_hex[:2], 16)
                email = "".join([chr(int(cf_hex[i:i+2], 16) ^ r) for i in range(2, len(cf_hex), 2)])
                if "@" in email and "." in email:
                    return email.lower()
            except Exception:
                pass
            return None

        # 3. Headings & Services / Products (with subpage crawl)
        h1_tags = [re.sub(r"\s+", " ", h.get_text()).strip() for h in soup.find_all("h1") if h.get_text().strip()]
        h2_tags = [re.sub(r"\s+", " ", h.get_text()).strip() for h in soup.find_all("h2") if h.get_text().strip()][:8]
        h3_tags = [re.sub(r"\s+", " ", h.get_text()).strip() for h in soup.find_all("h3") if h.get_text().strip()][:8]

        detected_services = []
        raw_candidates = h2_tags + h3_tags

        # Inspect navigation or product links on homepage
        product_subpages = []
        contact_subpages = []
        for a in soup.find_all("a", href=True):
            t = re.sub(r"\s+", " ", a.get_text()).strip()
            h = a["href"].strip()
            full_sub_url = urllib.parse.urljoin(final_url, h)
            h_low = h.lower()
            if any(k in h_low for k in ["/product", "/service", "/treatment", "/menu", "/range", "/category"]):
                if full_sub_url not in product_subpages and full_sub_url != final_url:
                    product_subpages.append(full_sub_url)
                if 3 < len(t) < 35 and not any(k in t.lower() for k in ["view all", "all product", "more", "explore", "know more"]):
                    raw_candidates.append(t)
            elif any(k in h_low for k in ["/contact", "/reach-us", "/location"]):
                if full_sub_url not in contact_subpages and full_sub_url != final_url:
                    contact_subpages.append(full_sub_url)

        # Fast subpage crawl for product catalog if available
        if product_subpages:
            try:
                sub_resp = requests.get(product_subpages[0], timeout=4, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                if sub_resp.status_code == 200:
                    sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
                    for el in sub_soup.find_all(["h2", "h3", "h4", "a"]):
                        txt = re.sub(r"\s+", " ", el.get_text()).strip(" :.-")
                        if 3 < len(txt) < 35 and not any(k in txt.lower() for k in [
                            "view", "product", "category", "home", "order", "skip", "our", "figure", "numbers", "privacy", "terms", "know more"
                        ]):
                            if not re.match(r"^[\d\s\+\,kKmMbBCr%]+$", txt):
                                raw_candidates.append(txt)
                    # Also check for Cloudflare email on product subpage
                    for cf_el in sub_soup.find_all(attrs={"data-cfemail": True}):
                        cf_dec = decode_cf_email(cf_el["data-cfemail"])
                        if cf_dec and cf_dec not in extra_data["emails"]:
                            extra_data["emails"].append(cf_dec)
            except Exception as se:
                print(f"[WebsiteAdapter] Product subpage crawl note: {se}")

        for cand in raw_candidates:
            cand_clean = cand.strip(" :.-")
            cand_low = cand_clean.lower()
            if 3 < len(cand_clean) < 45 and not any(k in cand_low for k in [
                "contact", "about", "navigation", "subscribe", "footer", "privacy", "terms",
                "career", "sign in", "login", "cookie", "copyright", "home", "search", "menu", "blog",
                "join us", "read more", "insights", "campaigns", "numbers that speak", "in figures",
                "leading dairy", "beacon of", "rooted in", "company of", "company in", "cr+", "k+", "crore", "lakh",
                "farmer initiatives", "knowledge center", "from store to door", "store locator", "products",
                "skip to", "ourcategories", "consumer products", "horeca products", "view product", "view all"
            ]):
                if re.match(r"^[\d\s\+\,kKmMbBCr%]+$", cand_clean):
                    continue
                if cand_clean not in detected_services:
                    detected_services.append(cand_clean)

        extra_data["detected_services"] = detected_services[:6]

        # 4. WhatsApp Links Check
        whatsapp_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if any(p in href.lower() for p in ["wa.me/", "api.whatsapp.com/send", "whatsapp://"]):
                whatsapp_links.append(href)
        
        if whatsapp_links:
            extra_data["whatsapp_link"] = whatsapp_links[0]
            evidence.append(EvidenceItem(
                source="Website",
                field="WhatsApp Instant Bridge",
                value=f"Detected active WhatsApp CTA ({whatsapp_links[0][:35]}...)",
                confidence=0.98,
                status="PASS",
                observation="Visitors have a direct, frictionless route to start an instant conversation."
            ))
        else:
            evidence.append(EvidenceItem(
                source="Website",
                field="WhatsApp Instant Bridge",
                value="No WhatsApp button or link detected on homepage",
                confidence=0.95,
                status="FAIL",
                observation="Mobile visitors must resort to manual form filling or voice calls to initiate an enquiry."
            ))

        # 5. Phone & Email (with Cloudflare decoding & contact page crawl)
        tel_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().startswith("tel:"):
                raw_tel = href[4:].strip()
                cleaned_tel = clean_phone(raw_tel)
                if cleaned_tel:
                    tel_links.append(cleaned_tel)

        mailto_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().startswith("mailto:"):
                clean_mail = href[7:].split("?")[0].strip().lower()
                if "@" in clean_mail and "." in clean_mail:
                    mailto_links.append(clean_mail)

        # Cloudflare email decoding on homepage
        for cf_el in soup.find_all(attrs={"data-cfemail": True}):
            cf_dec = decode_cf_email(cf_el["data-cfemail"])
            if cf_dec and cf_dec not in mailto_links:
                mailto_links.append(cf_dec)

        # If phone or email missing, do quick check on contact subpage
        if (not tel_links or not mailto_links) and contact_subpages:
            try:
                cnt_resp = requests.get(contact_subpages[0], timeout=4, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                if cnt_resp.status_code == 200:
                    cnt_soup = BeautifulSoup(cnt_resp.text, "html.parser")
                    for a in cnt_soup.find_all("a", href=True):
                        h = a["href"].strip()
                        if h.lower().startswith("tel:"):
                            c_p = clean_phone(h[4:].strip())
                            if c_p and c_p not in tel_links:
                                tel_links.append(c_p)
                        elif h.lower().startswith("mailto:"):
                            c_m = h[7:].split("?")[0].strip().lower()
                            if "@" in c_m and "." in c_m and c_m not in mailto_links:
                                mailto_links.append(c_m)
                    for cf_el in cnt_soup.find_all(attrs={"data-cfemail": True}):
                        cf_dec = decode_cf_email(cf_el["data-cfemail"])
                        if cf_dec and cf_dec not in mailto_links:
                            mailto_links.append(cf_dec)
            except Exception as ce:
                print(f"[WebsiteAdapter] Contact subpage crawl note: {ce}")

        # Fallback regex for phone
        phone_matches = re.findall(r"(?:1800[\-\s]?\d{3}[\-\s]?\d{4}|(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}|(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{4})", html)
        validated_matches = [clean_phone(p) for p in phone_matches if clean_phone(p)]
        valid_phones = tel_links if tel_links else [p for p in validated_matches if p][:2]
        
        # Fallback regex for email
        email_matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)
        valid_emails = mailto_links if mailto_links else [e.lower() for e in email_matches if not any(e.endswith(ext) for ext in [".png", ".jpg", ".webp", ".gif", ".svg", ".js", ".css"])][:2]

        extra_data["phones"] = valid_phones
        extra_data["emails"] = valid_emails
        extra_data["email"] = valid_emails[0] if valid_emails else None

        if valid_phones:
            evidence.append(EvidenceItem(
                source="Website",
                field="Voice Phone Visibility",
                value=f"Phone: {valid_phones[0]}",
                confidence=0.92,
                status="PASS",
                observation="Direct telephone contact is visible on the site."
            ))
        else:
            evidence.append(EvidenceItem(
                source="Website",
                field="Phone Visibility",
                value="No direct telephone number visibly displayed on homepage",
                confidence=0.88,
                status="PARTIAL",
                observation="Visitors seeking immediate voice contact have to search for details."
            ))

        # 6. Primary Action Buttons / CTAs
        cta_buttons = []
        for btn in soup.find_all(["button", "a"]):
            text = btn.get_text().strip().lower()
            if any(k in text for k in ["book", "enquire", "contact", "get quote", "schedule", "consult", "appointment", "demo", "order", "buy"]):
                if 2 < len(text) < 30:
                    cta_buttons.append(btn.get_text().strip())
        
        if cta_buttons:
            unique_ctas = list(dict.fromkeys(cta_buttons))[:3]
            evidence.append(EvidenceItem(
                source="Website",
                field="Primary Action Hierarchy",
                value=f"Active CTA detected: '{unique_ctas[0]}'",
                confidence=0.94,
                status="PASS",
                observation=f"Homepage provides direct action triggers ({', '.join(unique_ctas)})."
            ))
        else:
            evidence.append(EvidenceItem(
                source="Website",
                field="Primary Action Hierarchy",
                value="No clear conversion CTA button detected on homepage",
                confidence=0.91,
                status="FAIL",
                observation="Website serves as a passive brochure without prominent conversion pathways."
            ))

        # 7. Mobile Viewport Check
        viewport_tag = soup.find("meta", attrs={"name": "viewport"})
        if viewport_tag:
            evidence.append(EvidenceItem(
                source="Website",
                field="Mobile Viewport Optimization",
                value="Configured for responsive mobile rendering",
                confidence=0.95,
                status="PASS",
                observation="Viewport meta configuration adapts page layout to smartphone screens."
            ))
        else:
            evidence.append(EvidenceItem(
                source="Website",
                field="Mobile Viewport Optimization",
                value="Standard mobile viewport tag missing",
                confidence=0.90,
                status="PARTIAL",
                observation="Page may require manual zooming or pinching on smaller mobile screens."
            ))

        # 8. Connected Social Profiles & External Channels
        social_links = []
        instagram_url = None
        facebook_url = None
        linkedin_url = None
        youtube_url = None
        google_maps_url = None

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            href_lower = href.lower()
            if "instagram.com/" in href_lower and not any(k in href_lower for k in ["share", "intent"]):
                instagram_url = href
                social_links.append(href)
            elif "facebook.com/" in href_lower and not any(k in href_lower for k in ["share", "sharer"]):
                facebook_url = href
                social_links.append(href)
            elif "linkedin.com/company" in href_lower:
                linkedin_url = href
                social_links.append(href)
            elif "youtube.com/" in href_lower:
                youtube_url = href
                social_links.append(href)
            elif ("google.com/maps" in href_lower or "maps.app.goo.gl" in href_lower or "goo.gl/maps" in href_lower):
                google_maps_url = href

        extra_data["social_links"] = list(dict.fromkeys(social_links))
        extra_data["instagram_url"] = instagram_url
        extra_data["facebook_url"] = facebook_url
        extra_data["linkedin_url"] = linkedin_url
        extra_data["youtube_url"] = youtube_url
        extra_data["google_maps_url"] = google_maps_url

        if social_links:
            found_names = []
            if instagram_url: found_names.append("Instagram")
            if facebook_url: found_names.append("Facebook")
            if linkedin_url: found_names.append("LinkedIn")
            if youtube_url: found_names.append("YouTube")
            evidence.append(EvidenceItem(
                source="Website",
                field="Social Ecosystem Integration",
                value=f"{', '.join(found_names)} profile(s) connected",
                confidence=0.95,
                status="PASS",
                observation="Website provides verified bridges to active brand community channels."
            ))
        else:
            evidence.append(EvidenceItem(
                source="Website",
                field="Social Ecosystem Integration",
                value="No active social media links detected on homepage",
                confidence=0.88,
                status="UNKNOWN",
                observation="Cross-channel linking to Instagram or Facebook is not visibly configured."
            ))

        # 9. HTTPS Security Check
        is_https = final_url.startswith("https://")
        evidence.append(EvidenceItem(
            source="Website",
            field="SSL / Security Protocol",
            value="Encrypted HTTPS active" if is_https else "Unencrypted HTTP connection",
            confidence=0.99,
            status="PASS" if is_https else "FAIL",
            observation="Connection security verified." if is_https else "Site triggers security warnings in modern browsers."
        ))

        # 10. Comprehensive Multi-Industry Taxonomy Detection
        combined_text = (page_title + " " + meta_desc + " " + " ".join(h1_tags) + " " + business_name).lower()
        
        if any(k in combined_text for k in ["dental", "dentist", "teeth", "implant", "orthodontic", "ortho"]):
            category = "Dental & Specialty Healthcare"
        elif any(k in combined_text for k in ["clinic", "hospital", "doctor", "health", "physio", "eye care", "ayurved", "pediatric", "pathology", "diagnostics"]):
            category = "Healthcare & Specialty Medical"
        elif any(k in combined_text for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "beverage", "packaged food", "agro"]):
            category = "Food, Dairy & FMCG"
        elif any(k in combined_text for k in ["banquet", "resort", "venue", "marriage hall", "wedding lawn", "convention center", "party hall"]):
            category = "Banquets & Event Venues"
        elif any(k in combined_text for k in ["interior", "architecture", "decor", "design studio", "furnishing", "modular kitchen", "architectural"]):
            category = "Interior Design & Architecture"
        elif any(k in combined_text for k in ["school", "college", "preschool", "academy", "institute", "coaching", "education", "classes", "university"]):
            category = "Education & Academies"
        elif any(k in combined_text for k in ["salon", "spa", "beauty", "hair", "skin", "aesthetic", "makeup", "wellness"]):
            category = "Beauty, Salon & Wellness"
        elif any(k in combined_text for k in ["restaurant", "cafe", "dining", "menu", "bistro", "catering", "bakery", "lounge", "kitchen", "pizzeria"]):
            category = "Hospitality & Dining"
        elif any(k in combined_text for k in ["auto", "car", "detailing", "repair", "vehicle", "mechanic", "garage", "tyre", "wheel"]):
            category = "Automotive Care & Services"
        elif any(k in combined_text for k in ["real estate", "property", "realtor", "builder", "developer", "apartments", "villas", "commercial space"]):
            category = "Real Estate & Property Advisory"
        elif any(k in combined_text for k in ["manufacturing", "industrial", "fabrication", "machinery", "metals", "packaging", "chemicals", "exporter"]):
            category = "Manufacturing & Industrial B2B"
        elif any(k in combined_text for k in ["law", "legal", "advocate", "attorney", "tax", "ca ", "chartered accountant", "consulting", "advisory", "accounting"]):
            category = "Professional & Advisory Services"
        elif any(k in combined_text for k in ["plumbing", "electrical", "hvac", "pest control", "carpenter", "contractor", "roofing", "cleaning"]):
            category = "Home Services & Contracting"
        else:
            category = "Commercial & Local Enterprise"

        identity = BusinessIdentity(
            business_name=business_name,
            category=category,
            address=None,
            city="Local Area",
            phone=valid_phones[0] if valid_phones else None,
            website=final_url,
            source_url=cleaned_url,
            resolved_url=final_url,
            place_id=None,
            rating=None,
            review_count=None,
            identity_confidence=0.95,
            verified=True,
            is_demo=False,
            instagram_url=instagram_url,
            facebook_url=facebook_url,
            whatsapp_url=whatsapp_links[0] if whatsapp_links else None,
            email=valid_emails[0] if valid_emails else None,
            google_maps_url=google_maps_url,
            tagline=extra_data.get("tagline")
        )

        return identity, evidence, extra_data
