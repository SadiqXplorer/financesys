from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


OUT = Path("Finance_Management_System_Presentation.pptx")


SLIDES = [
    {
        "title": "Finance Management System",
        "bullets": [
            "A full-stack DBMS project for managing personal finance records.",
            "Built with Python, SQLite, HTML, CSS, and JavaScript.",
            "Includes dashboard, reports, admin, and login pages.",
        ],
    },
    {
        "title": "Project Overview",
        "bullets": [
            "Purpose: help users track income, expenses, budgets, and account balances.",
            "Focus: database-driven financial record management.",
            "Suitable for DBMS mini project demo, viva, and documentation.",
        ],
    },
    {
        "title": "Objectives",
        "bullets": [
            "Store and manage financial records efficiently.",
            "Provide a simple user interface for daily transaction entry.",
            "Generate summaries and reports for analysis.",
            "Demonstrate DBMS concepts using a real application.",
        ],
    },
    {
        "title": "Technology Stack",
        "bullets": [
            "Frontend: HTML, CSS, JavaScript",
            "Backend: Python HTTP server",
            "Database: SQLite",
            "Architecture: browser UI connected to REST-style API endpoints",
        ],
    },
    {
        "title": "Main Modules",
        "bullets": [
            "Dashboard: balance, income, expense, and savings summary",
            "Transactions: add income and expense records",
            "Budgets: create monthly spending limits",
            "Accounts and Categories: manage master data",
            "Reports: category-wise and monthly analysis",
        ],
    },
    {
        "title": "Database Tables",
        "bullets": [
            "users",
            "accounts",
            "categories",
            "transactions",
            "budgets",
        ],
    },
    {
        "title": "Database Relationships",
        "bullets": [
            "One user can have multiple accounts.",
            "One user can create multiple categories.",
            "Each transaction belongs to one account and one category.",
            "Each budget belongs to one expense category for a month.",
        ],
    },
    {
        "title": "Key Features",
        "bullets": [
            "Add and manage accounts with opening balances.",
            "Record income and expense transactions.",
            "Assign categories to each transaction.",
            "Track budgets and spending progress.",
            "View recent transactions and expense breakdown.",
        ],
    },
    {
        "title": "System Workflow",
        "bullets": [
            "User opens the application.",
            "User adds accounts and categories.",
            "User records income and expense transactions.",
            "System updates balances and stores data in SQLite.",
            "Dashboard and reports display summarized information.",
        ],
    },
    {
        "title": "User Interface Pages",
        "bullets": [
            "Dashboard page",
            "Reports page",
            "Admin page",
            "Login page",
            "Responsive design for desktop and mobile",
        ],
    },
    {
        "title": "Advantages",
        "bullets": [
            "Easy to use and lightweight.",
            "Centralized financial data management.",
            "Fast local database access with SQLite.",
            "Good demonstration of CRUD operations and DBMS design.",
        ],
    },
    {
        "title": "Future Enhancements",
        "bullets": [
            "User authentication with passwords in the database.",
            "Export reports to PDF or Excel.",
            "Graphs and charts for visual analytics.",
            "Cloud deployment and multi-user support.",
        ],
    },
    {
        "title": "Conclusion",
        "bullets": [
            "The Finance Management System is a practical DBMS project.",
            "It combines frontend, backend, and database concepts in one application.",
            "It helps users manage finances efficiently and demonstrates real-world database usage.",
        ],
    },
]


def emu(value):
    return str(value)


def paragraph_xml(text, level=0):
    return (
        f'<a:p><a:pPr lvl="{level}"/><a:r>'
        f'<a:rPr lang="en-US" sz="2200"/>'
        f'<a:t>{escape(text)}</a:t></a:r><a:endParaRPr lang="en-US" sz="2200"/></a:p>'
    )


def slide_xml(title, bullets):
    bullet_paragraphs = "".join(paragraph_xml(text) for text in bullets)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
 <p:cSld>
  <p:spTree>
   <p:nvGrpSpPr>
    <p:cNvPr id="1" name=""/>
    <p:cNvGrpSpPr/>
    <p:nvPr/>
   </p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm>
     <a:off x="0" y="0"/>
     <a:ext cx="0" cy="0"/>
     <a:chOff x="0" y="0"/>
     <a:chExt cx="0" cy="0"/>
    </a:xfrm>
   </p:grpSpPr>
   <p:sp>
    <p:nvSpPr>
     <p:cNvPr id="2" name="Title 1"/>
     <p:cNvSpPr/>
     <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
     <a:xfrm><a:off x="457200" y="274320"/><a:ext cx="8229600" cy="914400"/></a:xfrm>
    </p:spPr>
    <p:txBody>
     <a:bodyPr/>
     <a:lstStyle/>
     <a:p>
      <a:r>
       <a:rPr lang="en-US" sz="2800" b="1"/>
       <a:t>{escape(title)}</a:t>
      </a:r>
      <a:endParaRPr lang="en-US" sz="2800"/>
     </a:p>
    </p:txBody>
   </p:sp>
   <p:sp>
    <p:nvSpPr>
     <p:cNvPr id="3" name="Content Placeholder 2"/>
     <p:cNvSpPr/>
     <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
     <a:xfrm><a:off x="640080" y="1463040"/><a:ext cx="7924800" cy="4306320"/></a:xfrm>
    </p:spPr>
    <p:txBody>
     <a:bodyPr wrap="square"/>
     <a:lstStyle/>
     {bullet_paragraphs}
    </p:txBody>
   </p:sp>
  </p:spTree>
 </p:cSld>
 <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def slide_rels_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''


def content_types_xml(slide_count):
    slide_overrides = "\n".join(
        f' <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
 <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
 <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
 <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
 <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
 <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
 {slide_overrides}
</Types>'''


def root_rels_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def app_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
 <Application>Microsoft Office PowerPoint</Application>
 <PresentationFormat>On-screen Show (4:3)</PresentationFormat>
 <Slides>13</Slides>
 <Notes>0</Notes>
 <HiddenSlides>0</HiddenSlides>
 <MMClips>0</MMClips>
 <ScaleCrop>false</ScaleCrop>
 <HeadingPairs>
  <vt:vector size="2" baseType="variant">
   <vt:variant><vt:lpstr>Theme</vt:lpstr></vt:variant>
   <vt:variant><vt:i4>1</vt:i4></vt:variant>
  </vt:vector>
 </HeadingPairs>
 <TitlesOfParts>
  <vt:vector size="1" baseType="lpstr">
   <vt:lpstr>Office Theme</vt:lpstr>
  </vt:vector>
 </TitlesOfParts>
 <Company>OpenAI</Company>
 <LinksUpToDate>false</LinksUpToDate>
 <SharedDoc>false</SharedDoc>
 <HyperlinksChanged>false</HyperlinksChanged>
 <AppVersion>16.0000</AppVersion>
</Properties>'''


def core_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>Finance Management System</dc:title>
 <dc:subject>DBMS Project Presentation</dc:subject>
 <dc:creator>Codex</dc:creator>
 <cp:keywords>finance, dbms, project</cp:keywords>
 <dc:description>Presentation for Finance Management System project</dc:description>
 <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
 <dcterms:created xsi:type="dcterms:W3CDTF">2026-04-16T00:00:00Z</dcterms:created>
 <dcterms:modified xsi:type="dcterms:W3CDTF">2026-04-16T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def presentation_xml(slide_count):
    sld_ids = "\n".join(
        f'  <p:sldId id="{256 + i}" r:id="rId{i + 1}"/>'
        for i in range(slide_count)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
 saveSubsetFonts="1" autoCompressPictures="0">
 <p:sldMasterIdLst>
  <p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/>
 </p:sldMasterIdLst>
 <p:sldIdLst>
{sld_ids}
 </p:sldIdLst>
 <p:sldSz cx="9144000" cy="6858000" type="screen4x3"/>
 <p:notesSz cx="6858000" cy="9144000"/>
 <p:defaultTextStyle>
  <a:defPPr>
   <a:defRPr lang="en-US"/>
  </a:defPPr>
  <a:lvl1pPr marL="342900" indent="-342900"/>
 </p:defaultTextStyle>
</p:presentation>'''


def presentation_rels_xml(slide_count):
    slide_rels = "\n".join(
        f' <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{slide_rels}
 <Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
</Relationships>'''


def slide_master_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
 <p:cSld name="Office Theme">
  <p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>
  <p:spTree>
   <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
   </p:grpSpPr>
  </p:spTree>
 </p:cSld>
 <p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>
 <p:sldLayoutIdLst>
  <p:sldLayoutId id="1" r:id="rId1"/>
 </p:sldLayoutIdLst>
 <p:txStyles>
  <p:titleStyle/>
  <p:bodyStyle/>
  <p:otherStyle/>
 </p:txStyles>
</p:sldMaster>'''


def slide_master_rels_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>'''


def slide_layout_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="titleAndContent" preserve="1">
 <p:cSld name="Title and Content">
  <p:spTree>
   <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
   </p:grpSpPr>
  </p:spTree>
 </p:cSld>
 <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''


def slide_layout_rels_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''


def theme_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
 <a:themeElements>
  <a:clrScheme name="Office">
   <a:dk1><a:srgbClr val="000000"/></a:dk1>
   <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
   <a:dk2><a:srgbClr val="1F497D"/></a:dk2>
   <a:lt2><a:srgbClr val="EEECE1"/></a:lt2>
   <a:accent1><a:srgbClr val="4F81BD"/></a:accent1>
   <a:accent2><a:srgbClr val="C0504D"/></a:accent2>
   <a:accent3><a:srgbClr val="9BBB59"/></a:accent3>
   <a:accent4><a:srgbClr val="8064A2"/></a:accent4>
   <a:accent5><a:srgbClr val="4BACC6"/></a:accent5>
   <a:accent6><a:srgbClr val="F79646"/></a:accent6>
   <a:hlink><a:srgbClr val="0000FF"/></a:hlink>
   <a:folHlink><a:srgbClr val="800080"/></a:folHlink>
  </a:clrScheme>
  <a:fontScheme name="Office">
   <a:majorFont><a:latin typeface="Calibri"/></a:majorFont>
   <a:minorFont><a:latin typeface="Calibri"/></a:minorFont>
  </a:fontScheme>
  <a:fmtScheme name="Office">
   <a:fillStyleLst>
    <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
   </a:fillStyleLst>
   <a:lnStyleLst>
    <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
   </a:lnStyleLst>
   <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
   <a:bgFillStyleLst>
    <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
   </a:bgFillStyleLst>
  </a:fmtScheme>
 </a:themeElements>
</a:theme>'''


def build():
    with ZipFile(OUT, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(len(SLIDES)))
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("ppt/presentation.xml", presentation_xml(len(SLIDES)))
        zf.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(len(SLIDES)))
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml())
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml())
        zf.writestr("ppt/theme/theme1.xml", theme_xml())
        for idx, slide in enumerate(SLIDES, start=1):
            zf.writestr(f"ppt/slides/slide{idx}.xml", slide_xml(slide["title"], slide["bullets"]))
            zf.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels_xml())


if __name__ == "__main__":
    build()
    print(f"Created {OUT.resolve()}")
