from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
import re

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
ACCENT = RGBColor(0x8E, 0x26, 0x3E)
INK = RGBColor(0x1F, 0x2A, 0x30)
MUTED = RGBColor(0x5D, 0x69, 0x70)


def clean_doc(document):
    """Remove semicolons and em dashes from every run, keeping the prose readable."""
    for para in document.paragraphs:
        for run in para.runs:
            if run._element.findall('.//' + qn('w:br')):
                continue
            text = run.text
            text = text.replace(" — Requisition", ", Requisition")
            text = text.replace(" — ", ": ")
            text = re.sub(r";\s*([a-z])", lambda m: ". " + m.group(1).upper(), text)
            text = text.replace(";", ".")
            text = text.replace("--", "to")
            run.text = text


def save_doc(document, filename):
    clean_doc(document)
    document.save(os.path.join(OUT, filename))


def set_cell_border(paragraph, color="8E263E", sz="6"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)


def base(doc, margin=0.55):
    sec = doc.sections[0]
    sec.top_margin = Inches(0.45)
    sec.bottom_margin = Inches(0.4)
    sec.left_margin = Inches(margin)
    sec.right_margin = Inches(margin)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(9.8)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(1)
    normal.paragraph_format.line_spacing = 1.0


def section(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text.upper())
    r.bold = True
    r.font.size = Pt(9.2)
    r.font.color.rgb = ACCENT
    r.font.name = "Calibri"
    set_cell_border(p)
    return p


def add_text(paragraph, text, size=10.2):
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        run = paragraph.add_run(part[2:-2] if bold else part)
        run.bold = bold
        run.font.size = Pt(size)


def body(doc, text, bold_lead=None, size=10.2, after=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        r.font.size = Pt(size)
    add_text(p, text, size)
    return p


def bullet(doc, text, bold_lead=None, size=10.0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.first_line_indent = Inches(-0.12)
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        r.font.size = Pt(size)
    add_text(p, text, size)
    return p


def role(doc, title, org, dates):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(7.15), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(10.4)
    p.add_run("\t")
    r = p.add_run(dates)
    r.font.size = Pt(9.3)
    r.font.color.rgb = MUTED
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    r = p2.add_run(org)
    r.italic = True
    r.font.size = Pt(9.4)
    r.font.color.rgb = MUTED


def header(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Narissara Khomkhai")
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = INK
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Associate Director of Operations & Administration · Harvard International Office")
    r.font.size = Pt(9.8)
    r.font.color.rgb = ACCENT
    r.bold = True
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Cambridge, MA · 617-852-9805 · sawatdee@me.com · linkedin.com/in/narissara · U.S. citizen · DSO/ARO eligible")
    r.font.size = Pt(8.5)
    r.font.color.rgb = MUTED
    set_cell_border(p, color="8E263E", sz="8")


# ---------------- RESUME ----------------
doc = Document()
base(doc)
header(doc)

section(doc, "Professional summary")
body(doc, "**Operations and data leader** with **20+ years** in higher-education administration, including advancement services at Phillips Academy and UAMS and governed reporting at Harvard FAS. Builds the controls behind **accurate records**, **reliable systems**, **reconciled billing**, **useful reporting** and a **cross-trained team**. U.S. citizen and DSO/ARO eligible. SEVIS training, shadowing and supervised signing would precede independent case decisions.", size=9.7)

section(doc, "Core capabilities")
body(doc, "**Operations administration** · **Records integrity** · **Data governance** · **Systems and conversions** · **Reporting and BI** · **Billing and reconciliation** · **Team leadership** · **Project and program management** · **Vendor management** · **Data security**", size=9.5)

section(doc, "Selected results")
bullet(doc, "**Three platform conversions:** **Raiser’s Edge** to **SunGard/Ellucian Advance**, **Raiser’s Edge** to **Agilon** and **APEX** to **HART**, including mapping, parallel reconciliation, rollback and user training.", size=9.6)
bullet(doc, "Reconciled **$400M campaign** reporting to the **General Ledger** and maintained audit-ready support for **60,000+ records** and **20,000+ annual gifts**.", size=9.6)
bullet(doc, "Reduced recurring **ad hoc reporting** from **300–400 requests** a year to **under 100** through **SQL**, **Oracle BI/HART** and one definition per measure.", size=9.6)
bullet(doc, "Built **reporting and decision materials** for **50+ departments**, deans, chairs and the **Governing Boards**, with a documented **OGC** release record.", size=9.6)
bullet(doc, "Supervised and **cross-trained teams of three to five** through campaigns, conversions and peak service periods, with named **backups** for every critical process.", size=9.6)

section(doc, "Relevant to HIO")
bullet(doc, "**Records integrity:** audit-ready controls, duplicate prevention and exception logs map to **SEVIS validation** and the rule that no form comes from an unvalidated record.", size=9.5)
bullet(doc, "**Systems ownership:** three conversions with test, parallel run, rollback and training map to **ISSM release gates**, **test registers** and **vendor/HUIT coordination**.", size=9.5)
bullet(doc, "**Reporting and data:** a seven-source **DataHub**, **data dictionary** and reusable views map to the Director’s **dashboard** and one definition per measure.", size=9.5)
bullet(doc, "**Billing and reconciliation:** **$400M campaign-to-GL** work and **20,000+ annual transactions** map to **hospital invoices**, **accruals** and **over-90 controls**.", size=9.5)
bullet(doc, "**Team and program:** 3–5 person **supervision**, **cross-training** and a **90-day plan** with **gates**, **RACI** and **RAID** map to the operations team and program cadence.", size=9.5)

section(doc, "Selected project and program experience")
bullet(doc, "Led **three platform conversions** end to end: **requirements**, **mapping**, **parallel run**, **rollback**, **training** and **hypercare**.", size=9.5)
bullet(doc, "Built **reporting governance** for **50+ departments**: one definition per measure, **data dictionary**, **role-based access** and documented release review.", size=9.5)
bullet(doc, "Supervised **three to five staff** through simultaneous campaign and conversion work, with **cross-training**, **reviews** and named **backups**.", size=9.5)
bullet(doc, "Used **SQL**, **Oracle BI/HART**, **Crystal/SSRS**, **Python** and **R** to replace recurring manual reports with reusable views and repeatable checks.", size=9.5)

section(doc, "Leadership and values")
body(doc, "I lead with **respect** for the person behind every record, **honesty** in the numbers, **excellence** in testing before release, **accountability** for every exception and **bridge-building** across Schools, HUIT, Finance, the hospitals and OGC. The operating model is only credible if those values show up in the daily queue, the batch and the gate pack.", size=9.5)

section(doc, "Selected reporting and controls")
bullet(doc, "Built **duplicate prevention**, **correction logs** and **audit-ready support** for external reviews across gift and faculty records.", size=9.5)
bullet(doc, "Managed monthly **General Ledger tie-outs**, **accrual support** and **over-90 review** with Finance and the Comptroller’s office.", size=9.5)
bullet(doc, "Handled **OGC** and institutional data requests with minimum necessary extract, validation and a documented release record.", size=9.5)
bullet(doc, "Created **role-based access** for confidential records, approved by the Dean of Faculty Affairs and reviewed periodically.", size=9.5)

doc.add_page_break()
section(doc, "Professional experience")
role(doc, "IT Reporting, Data & Business Analyst · Faculty Affairs Data Owner", "Harvard University · FAS Office for Faculty Affairs · Cambridge, MA", "Apr 2019 – Nov 2025")
bullet(doc, "**Governed reporting** and decision materials for **50+ departments**, deans, chairs and the **Governing Boards**, with one definition, owner and source per measure.", size=9.6)
bullet(doc, "Oversaw priorities and quality control for the **Faculty DataHub** pilot across **seven sources**, including **SIS**, **GSAS BI** and the Registrar. Contributed to the **data dictionary** and **role-based access** approved by the Dean.", size=9.6)
bullet(doc, "Cut **ad hoc reporting** from **300–400 requests** a year to **under 100** using **SQL** and **Oracle BI/HART**. Handled **OGC** and institutional data requests with a documented release record.", size=9.6)

role(doc, "Data Analytics & Reporting Practitioner", "Independent practice · remote · concurrent with institutional roles", "2008 – Present")
body(doc, "**SQL**, **Python**, **R** and **BI reporting** for data quality, survey analysis and decision support. Scoped work, documented assumptions and delivered to a named owner.", size=9.6)

role(doc, "Assistant Director of Gift Services & Reporting", "Phillips Academy, Andover, MA · Office of Academy Resources", "Aug 2016 – Apr 2019")
bullet(doc, "Managed **gift administration** and leadership reporting for a **$400M campaign**. Reconciled campaign reporting to the **General Ledger** with the Comptroller’s office.", size=9.6)
bullet(doc, "Led the **Raiser’s Edge to Agilon** conversion: mapping, ten years of history, **parallel reconciliation**, **SOPs** and **user training**.", size=9.6)

role(doc, "Associate Director, Donor Records & Advancement Information Service", "University of Arkansas for Medical Sciences · Little Rock, AR", "May 2008 – Jul 2016")
bullet(doc, "Led information services for **60,000+ records** and **20,000+ annual transactions**. Maintained **duplicate controls**, **audit-ready support** and monthly **GL tie-outs**.", size=9.6)
bullet(doc, "Co-led the **Raiser’s Edge to SunGard/Ellucian Advance** conversion. Piloted and managed **online giving** with **iModules** and **CyberSource**, front end and back end.", size=9.6)
bullet(doc, "Hired, supervised and **cross-trained a team of three**. Built **Oracle SQL** views and reporting used by advancement, finance and foundation staff.", size=9.6)

section(doc, "Earlier experience")
role(doc, "Program Specialist", "UAMS College of Medicine · Little Rock, AR", "Apr 2006 – May 2008")
bullet(doc, "Research program support, **needs assessments**, **survey analysis** and reporting for residency and continuing-education programs.", size=9.4)
role(doc, "Management Project Analyst II", "UAMS College of Pharmacy · Little Rock, AR", "Aug 2005 – Apr 2006")
bullet(doc, "**Program assessment**, web-based delivery, **records** and **accounts reconciliation**.", size=9.4)
role(doc, "International Coordinator", "UNCTAD Trade Point Thailand · Chiang Mai, Thailand", "Sep 2002 – Feb 2005")
bullet(doc, "**Global communications**, **e-commerce** and partner events for small and medium-sized businesses.", size=9.4)

section(doc, "Education and certifications")
body(doc, "B.A., **English, Linguistics and Literature** · Payap University, Chiang Mai, Thailand · Minor in German", size=9.4)
body(doc, "Graduate coursework, **Nonprofit Management** · University of Arkansas at Little Rock · 15 credit hours, not a completed degree", size=9.4)
body(doc, "**QPS Master Expert Certification** in AI Execution · **AI Project Management** · **AI Marketing and Business Development** · **Data Analytics** · **AI for Data Analysis**", size=9.4)

section(doc, "Technical toolkit")
body(doc, "**SQL** (Oracle, SQL Server) · **Python** · **R** · **Excel** · **Oracle BI/HART** · **APEX** · **Crystal Reports** · **SSRS** · **Tableau** · **Power BI** · **Ellucian Advance** · **Raiser’s Edge** · **Agilon** · **iModules** · **CyberSource** · **PeopleSoft** · **Workday** · **Aurora** · **GMAS** · **FROPS** · **SIS**", size=9.4)

section(doc, "Eligibility and planned development")
body(doc, "**U.S. citizen** · eligible for **DSO/ARO** designation · no sponsorship required. Planned on hire: **SEVP school officials training**, **NAFSA F-1/J-1 training**, **DSO/ARO shadowing** and **supervised signing** before independent case decisions.", size=9.4)

save_doc(doc, "Narissara_Khomkhai_Resume_HIO_Associate_Director_Final.docx")

# ---------------- COVER LETTER ----------------
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.7)
sec.bottom_margin = Inches(0.6)
sec.left_margin = Inches(0.8)
sec.right_margin = Inches(0.8)
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.font.color.rgb = INK
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.0

header(doc)
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(10)
p.paragraph_format.space_after = Pt(6)
r = p.add_run("November 25, 2026")
r.font.size = Pt(9.8)
r.font.color.rgb = MUTED

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run("HIO Search Committee")
r.bold = True
r.font.size = Pt(10.2)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(8)
r = p.add_run("Harvard International Office · Cambridge, MA")
r.font.size = Pt(9.8)

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(8)
r = p.add_run("Re: Associate Director of Operations & Administration — Requisition 004436SR")
r.bold = True
r.font.size = Pt(10.2)
r.font.color.rgb = ACCENT

body(doc, "Dear Members of the Search Committee,", size=10.5, after=6)
body(doc, "I am applying for the Associate Director of Operations & Administration role. My career has been spent making the operating system behind higher-education work accurate, testable and easier to run: advancement services at Phillips Academy and UAMS, then governed reporting and cross-unit coordination at Harvard FAS. I would bring the same discipline to HIO’s records, systems, billing, reporting and operations team.", size=10.5, after=6)
body(doc, "At Harvard, I owned reporting, data quality and access governance for 50+ departments, deans, chairs, visiting committees and the Governing Boards. I oversaw priorities and quality control for the Faculty DataHub pilot across seven sources, helped build the data dictionary and access model, and reduced recurring ad-hoc reporting from an estimated 300–400 requests a year to under 100. At Phillips Academy, I reconciled $400M campaign reporting to the General Ledger and led a Raiser’s Edge conversion; at UAMS, I ran information services for 60,000+ records and 20,000+ annual gift transactions while supervising a team of three.", size=10.5, after=6)
body(doc, "HIO’s mission is to support Harvard’s teaching and research by serving international students and scholars and acting as their liaison with federal agencies. I would carry it through the University’s values in daily practice. Respect means every record is a person’s status. Honesty means the numbers must reconcile before they are reported. Excellence means releases and batches are tested before they reach a student. Accountability means every exception, invoice and gate has one owner and one date. Building bonds means Schools, HUIT, Finance, hospitals and OGC share one definition.", size=10.5, after=6)
body(doc, "In the first 90 days I would protect the federal calendar, make School data clean on arrival, give the Director one decision-ready view and build a team that can run the cycle without me. That is how the mission becomes operational rather than a statement on a wall.", size=10.5, after=6)
body(doc, "The attached work sample is my proposed operating model for HIO. It covers eight work areas, a first-90-day plan, a 13-week calendar with every area gate, daily/weekly/monthly reporting, decision rights, RACI, RAID, a service catalog, a cost and vendor model, and a newcomer services queue. It is deliberately built around controls and evidence, not a claim that I already know HIO’s internal systems or case practice.", size=10.5, after=6)
body(doc, "I have not served as a DSO or ARO. I am a U.S. citizen and eligible for designation, and I would complete SEVIS and DSO training, shadow advisors, and sign only under supervision and Director approval before taking independent case decisions. The operations, data, systems, billing, reporting and team leadership are the work I have already done; the SEVIS practice is the part I would learn in the role.", size=10.5, after=6)
body(doc, "The work sample is at https://narissa-pgm.github.io/HIO_Ops/ and my career profile is at https://narissa-pgm.github.io/HIO_Ops/career-profile.html. I would welcome the chance to discuss where the operating model is strong and where HIO would change it.", size=10.5, after=6)
body(doc, "Thank you for your consideration. I would be glad to walk through the operating model, the first 90 days and the team plan with you.", size=10.5, after=6)
body(doc, "Sincerely,", size=10.5, after=16)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(0)
r = p.add_run("Narissara Khomkhai")
r.bold = True
r.font.size = Pt(10.5)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(0)
r = p.add_run("sawatdee@me.com · 617-852-9805")
r.font.size = Pt(9.5)
r.font.color.rgb = MUTED

save_doc(doc, "Narissara_Khomkhai_Cover_Letter_HIO_Associate_Director_Final.docx")
print("saved", OUT)
