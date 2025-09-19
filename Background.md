EyeCite is a Python package designed for the high-performance extraction of legal citations from text. Developed by the Free Law Project in collaboration with Harvard's Caselaw Access Project and CourtListener, it is used to process millions of legal documents. The tool addresses a critical need for open-source software in legal citation extraction, which has historically relied on proprietary data or ad-hoc scripts, thereby increasing scholarly transparency and consistency, and enabling new methods of citation analysis, such as machine learning applications.
EyeCite recognizes a wide variety of citations commonly found in American legal documents, including full and short case citations, statutory, law journal, supra, and id. citations. It also provides functionalities for pre-processing text, aggregating citations with common references, and annotating citations with custom markup.
I. Project Background and Core Functionalities
EyeCite's capabilities are built upon two foundational research projects, Courts-DB and Reporters-DB, which are also open-source Python packages from the Free Law Project. These provide the essential data that allows EyeCite to identify valid case citations and determine the courts and reporters associated with them.
Core Functions of EyeCite:
• Extraction: Recognizes and extracts various citation types from text, utilizing a database trained on over 55 million existing citations. This process involves consuming raw text, parsing it into discrete tokens using Hyperscan and its regular expression database, and then extracting meaningful metadata into unified objects.
• Aggregation: Resolves short case, supra, and id citations to their logical antecedents, linking them to common "Resource" objects.
• Annotation: Inserts custom markup, such as HTML links, around identified citations in the text. This feature can reconcile differences between original and cleaned text using the diff-match-patch library.
• Cleaning: Pre-processes and cleans citation-laden text to standardize formatting (e.g., whitespace, quotes, hyphens) and remove unwanted elements like HTML tags or OCR errors.
Performance and Underlying Technologies: EyeCite is designed for performance, leveraging the Hyperscan library for efficient tokenization and parsing. Hyperscan allows EyeCite to apply thousands of finely tuned regular expressions to match idiosyncratic citation formats without a loss of performance, parsing typical legal text at approximately 10MB/second. The comprehensive regular expression database is built from various sources including the Caselaw Access Project, CourtListener, Cardiff Index to Legal Abbreviations, Indigo Book, and LexisNexis and Westlaw databases.
Limitations: Currently, EyeCite primarily recognizes American legal citations, as it was developed for U.S. court cases. It does not offer worst-case performance guarantees, and certain tools may take exponentially long on worst-case inputs, thus recommending external time limits for potentially malicious inputs. EyeCite's approach relies on a collection of regular expressions, and alternative parser-based or machine-learning-based methods have not been explored as primary extraction strategies, though EyeCite serves as a strong baseline for comparison.
II. Developer Contribution Workflow
The standard process for contributing to the freelawproject/eyecite repository on GitHub is as follows:
1. Fork the repository to your own GitHub account.
2. Clone your fork to your local machine.
3. Create a new branch for your changes (e.g., git checkout -b feature/add-new-reporter).
4. Make your changes and add your tests.
5. Submit a Pull Request (PR) from your branch back to the main freelawproject/eyecite repository, clearly explaining the purpose of your changes.
III. Overarching Integration Process (Phased Approach)
Integrating new citation types and identifiers into the EyeCite system is a structured, multi-phase process:
Phase 1: Create New Data Models The initial technical step involves creating new Python data models in eyecite/models_extended.py. These models are dataclass objects that serve as structured containers for parsed citation data, inheriting from a BaseCitation class.
• BaseCitation: A base class for new citation types, including full_cite and metadata fields.
• ConstitutionCitation: For citations to constitutions, including jurisdiction, article, section, clause, amendment, part, and paragraph.
• RegulationCitation: For citations to regulations, including jurisdiction, reporter, volume, title, page, section, rule, and chapter.
• CourtRuleCitation: For citations to court rules, including jurisdiction, rule_num, rule_type, and court.
• LegislativeBillCitation: For citations to unenacted legislative bills, including jurisdiction, chamber, bill_num, congress_num, session_info, and year.
• SessionLawCitation: For citations to enacted session laws, including jurisdiction, year, volume, page, chapter_num, act_num, and law_num.
• JournalArticleCitation: For citations to law journal articles, including volume, reporter (journal name), page, year, and pincite.
• ScientificIdentifierCitation: For citations to scientific or academic identifiers, including id_type (e.g., "DOI", "PMID", "ISBN") and id_value.
Phase 2: Implement New Tokenizers This phase involves creating a new file, eyecite/tokenizers_extended.py, to house the parsing logic.
1. Regex Pattern Creation Strategy: Regular expressions (regex) are developed to match the new citation types.
    ◦ Duplicate Capture Group Names: A critical problem is that Python's re module will error if a single regex pattern contains multiple capture groups with the same name (e.g., (?P<article>...) for both Georgia and Maine).
    ◦ Unique Capture Group Names: To solve this, each raw pattern's capture groups must be given a unique name, typically by appending the state's abbreviation (e.g., (?P<article_ga>...), (?P<article_me>...)).
    ◦ Combining and Compiling Regex: For categories with many variations (like state-specific citations), uniquely named patterns are joined into a single, combined regex string using the | (OR) operator. More specific patterns should be placed at the beginning of the list to ensure they are matched first. The combined string is then compiled using re.compile with re.IGNORECASE and re.VERBOSE flags, wrapped in a non-capturing group (?:...) for good practice.
    ◦ Scientific & Academic Identifiers: These typically have unique, non-overlapping formats and are not combined into a single large regex. Instead, each identifier (e.g., DOI, PMID) usually has its own specific regex pattern within a map (IDENTIFIER_REGEX_MAP) or a dedicated tokenizer class.
2. Create New Tokenizer Classes: For each new citation category, a dedicated tokenizer class is created, inheriting from BaseTokenizer, to store the compiled regex pattern.
3. Implement find_all_citations Method: Within each tokenizer class, this method iterates through text, finds matches using its regex, and uses post-processing logic (often involving checking which unique capture groups were matched via match.groupdict()) to extract relevant data and yield new citation objects (e.g., ConstitutionCitation, JournalArticleCitation, ScientificIdentifierCitation).
Phase 3: Create Comprehensive Tests This is considered the most important step to ensure correctness. New test files are created in the tests/ directory (e.g., tests/test_journals.py, tests/test_identifiers.py). These tests use the get_citations function to verify that the new tokenizers correctly identify and parse citations from example text, asserting that extracted fields match expected values. Developers should write tests for every single identifier and state variation. Factory functions are available for convenience in creating mock citation objects.
Phase 4: Final Integration To activate the new parsers, they must be added to EyeCite's main processing pipeline. This involves:
1. Navigating to the eyecite/__init__.py file.
2. Importing the new tokenizer classes from eyecite.tokenizers_extended.
3. Adding instances of these new tokenizer classes to the DEFAULT_TOKENIZERS list (or similar central list of tokenizers).
Deployment Process:
1. Update CHANGES.md.
2. Update version info in pyproject.toml.
3. Commit and create a pull request.
4. Tag the merged commit with the new version number (e.g., v1.2.3).
5. Push the tag to trigger the automated deployment process, which publishes the new version to PyPI and builds the documentation.
IV. Detailed Citation Formats and Regex Patterns
A. General Enhancements & Handling
1. Citation Ranges (e.g., §§ 13-18)
    ◦ Detection: The regex for any tokenizer that uses a section symbol should be modified to match one or two section symbols (§{1,2}). This allows matching both single sections and ranges.
    ◦ Post-processing: After a range is matched, the tokenizer should be modified to yield two separate citation objects: one for the start of the range and one for the end. This avoids the complexity of generating all intermediate citations but captures the full scope of the reference.
2. Parallel Citations
    ◦ Some states have multiple valid citation formats for their statutes due to subject-matter codes (e.g., Texas, California, New York, Maryland), official vs. unofficial compilations (e.g., Pennsylvania), or historical versions.
    ◦ EyeCite's regex for these states must be flexible, often using broad capture groups for reporter names (e.g., (?P<reporter>[\w\s&;]+?) in Texas's regex) to recognize various subject-matter codes.
3. Abbreviations
    ◦ EyeCite does not use a universal dictionary for expanding legal abbreviations.
    ◦ Instead, its knowledge of abbreviations is implicitly embedded within its pattern-matching logic and specific regex patterns. For example, Fed.\sR.\sCiv.\sP. is explicitly looked for as that exact sequence of abbreviated terms, which is more reliable than a general dictionary.
4. Law Journal Articles
    ◦ EyeCite does not maintain a specific list of law journal abbreviations. Instead, it uses a universal regex pattern designed to recognize the consistent structure of journal citations.
    ◦ Core Structure: Typically includes a volume number, the abbreviated journal title, a page number, and the year in parentheses.
    ◦ Universal Regex Pattern: (?P<volume>\d+)\s+(?P<reporter>[\w\s.&;']+?)\s+(?P<page>\d+)(?:,\s+(?P<pincite>[\d-]+))?\s+\((?P<year>\d{4})\).
    ◦ How it works: Captures the volume (\d+), reporter (flexible [\w\s.&;']+?), page (\d+), optional pincite ((?:,\s+(?P<pincite>[\d-]+))?), and year in parentheses (\((?P<year>\d{4})\)).
    ◦ Integration: This universal regex is implemented in a dedicated JournalArticleTokenizer class, added to the main list of tokenizers, and thoroughly tested.
B. Specific Citation Categories (BlueBook Formats & Regex)
1. Constitutions
    ◦ Data Model: ConstitutionCitation.
    ◦ Federal Constitution:
        ▪ Main Body:
            • Format: U.S. CONST. art. I, § 9, cl. 2
            • Regex: U\.S\.\sCONST\.\sart\.\s(?P<article>[IVXLCDM]+),\s§\s(?P<section>\d+)(?:,\scl\.\s(?P<clause>\d+))?
        ▪ Amendments:
            • Format: U.S. CONST. amend. XIV, § 1
            • Regex: U\.S\.\sCONST\.\samend\.\s(?P<amendment>[IVXLCDM]+)(?:,\s§\s(?P<section>\d+))?
    ◦ State Constitutions:
        ▪ Combined Regex (STATE_CONSTITUTIONS_REGEX): (?:Ga\.\sCONST\.\sart\.\s(?P<article_ga>[\w\d]+),\s§\s(?P<section_ga>[\w\d]+),\spara\.\s(?P<paragraph_ga>[\w\d]+)|Me\.\sCONST\.\sart\.\s(?P<article_me>[\w\d]+),\spt\.\s(?P<part_me>[\d\w]+),\s§\s(?P<section_me>[\d\w]+)|Mass\.\sCONST\.\spt\.\s(?P<part_ma>\d+),\sart\.\s(?P<article_ma>[\d\w]+)|N\.H\.\sCONST\.\spt\.\s(?P<part_nh>\d+),\sart\.\s(?P<article_nh>[\d\w]+)|(?P<state_abbr>(?:[A-Z]\.){2,}|[A-Z][a-z]+\.)\sCONST\.\sart\.\s(?P<article_std>[\w\d]+)(?:,\s§\s(?P<section_std>[\d\w]+))?). Specific patterns for states like Georgia, Maine, Massachusetts, and New Hampshire are placed first, followed by a standard pattern for other states.
        ▪ Standard Pattern (Most States):
            • Format Examples: VA. CONST. art. IV, § 14 or CAL. CONST. art. I, § 7
            • Regex: (?P<state_abbr>(?:[A-Z]\.){2,}|[A-Z][a-z]+\.)\sCONST\.\sart\.\s(?P<article>[\w\d]+)(?:,\s§\s(?P<section>[\d\w]+))?. This pattern is flexible for various state abbreviations and optional section numbers.
        ▪ Georgia (Specific Variation):
            • Format: GA. CONST. art. I, § 1, para. I.
            • Regex: Ga\.\sCONST\.\sart\.\s(?P<article>[\w\d]+),\s§\s(?P<section>[\w\d]+),\spara\.\s(?P<paragraph>[\w\d]+).
        ▪ Maine (Specific Variation):
            • Format: ME. CONST. art. IV, pt. 3, § 1
            • Regex: Me\.\sCONST\.\sart\.\s(?P<article>[\w\d]+),\spt\.\s(?P<part>[\d\w]+),\s§\s(?P<section>[\d\w]+).
        ▪ Massachusetts (Specific Variation):
            • Format: MASS. CONST. pt. 1, art. 12
            • Regex: Mass\.\sCONST\.\spt\.\s(?P<part>\d+),\sart\.\s(?P<article>[\d\w]+).
        ▪ New Hampshire (Specific Variation):
            • Format: N.H. CONST. pt. 1, art. 2
            • Regex: N\.H\.\sCONST\.\spt\.\s(?P<part>\d+),\sart\.\s(?P<article>[\d\w]+).
        ▪ Tokenizer: StateConstitutionTokenizer.
2. Administrative Regulations
    ◦ Data Model: RegulationCitation.
    ◦ Federal Regulations:
        ▪ Code of Federal Regulations (C.F.R.):
            • Format: 42 C.F.R. § 438.6
            • Regex: (?P<title_num>\d+)\s+C\.F\.R\.\s+§\s+(?P<section_num>[\d.]+)
        ▪ Federal Register (Fed. Reg.):
            • Format: 88 Fed. Reg. 13,793
            • Regex: (?P<volume_num>\d+)\s+Fed\.\s+Reg\.\s+(?P<page_num>[\d,]+)
    ◦ State Administrative Regulations:
        ▪ Combined Regex (STATE_REGULATIONS_REGEX): A developer would join the full list of 50 state regex patterns with the | operator, placing more unique patterns first.
        ▪ Representative Sample of State Formats and Regex:
            • Alabama: ALA. ADMIN. CODE r. [rule number] - Regex: Ala\.\sAdmin\.\sCode\sr\.\s(?P<rule_num>[\d-]+)
            • Alaska: ALASKA ADMIN. CODE tit. [title], § [section] - Regex: Alaska\sAdmin\.\sCode\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>[\d.]+)\b
            • Arizona: ARIZ. ADMIN. CODE § [section] - Regex: Ariz\.\sAdmin\.\sCode\s§\s(?P<section_num>R\d+-\d+-\d+)
            • Arkansas: CODE ARK. R. [code number] - Regex: Code\sArk\.\sR\.\s(?P<rule_num>[\d\s.]+)
            • California: CAL. CODE REGS. tit. [title], § [section] - Regex: Cal\.\sCode\sRegs\.?\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>\d+)
            • Colorado: CODE COLO. REGS. § [section] - Regex: Code\sColo\.\sRegs\.?\s§\s(?P<section_num>[\d\s.-]+)
            • Connecticut: REGS. CONN. STATE AGENCIES § [section] - Regex: Regs\.?\sConn\.\sState\sAgencies\s§\s(?P<section_num>[\d\w-]+)
            • Delaware: DEL. ADMIN. CODE [code number] - Regex: Del\.\sAdmin\.\sCode\s(?P<rule_num>[\d\s-]+)
            • District of Columbia: D.C. MUN. REGS. tit. [title], § [section] - Regex: D\.C\.\sMun\.\sRegs\.?\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>[\d.]+)
            • Florida: FLA. ADMIN. CODE ANN. r. [rule] - Regex: Fla\.\sAdmin\.\sCode\sAnn\.?\sr\.\s(?P<rule_num>[\d\w-]+)
            • Georgia: GA. COMP. R. & REGS. [rule] - Regex: Ga\.\sComp\.\sR\.\s&\sRegs\.?\s(?P<rule_num>[\d-]+)
            • Hawaii: HAW. ADMIN. RULES § [section] - Regex: Haw\.\sAdmin\.\sRules\s§\s(?P<section_num>[\d-]+)
            • Idaho: IDAPA [code] - Regex: IDAPA\s(?P<rule_num>[\d\s.]+)
            • Illinois: ILL. ADMIN. CODE tit. [title], § [section] - Regex: Ill\.\sAdmin\.\sCode\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>[\d.]+)
            • Indiana: IND. ADMIN. CODE tit. [title], r. [rule] - Regex: Ind\.\sAdmin\.\sCode\stit\.\s(?P<title_num>\d+),\sr\.\s(?P<rule_num>[\d-]+)
            • Iowa: IOWA ADMIN. CODE r. [rule] - Regex: Iowa\sAdmin\.\sCode\sr\.\s(?P<rule_num>[\d\w()-]+)
            • Kansas: KAN. ADMIN. REGS. § [section] - Regex: Kan\.\sAdmin\.\sRegs\.?\s§\s(?P<section_num>[\d-]+)
            • Kentucky: [title] KY. ADMIN. REGS. [chapter]:[regulation] - Regex: (?P<title_num>\d+)\sKy\.\sAdmin\.\sRegs\.?\s(?P<rule_num>[\d:]+)
            • Louisiana: LA. ADMIN. CODE tit. [title], § [section] - Regex: La\.\sAdmin\.\sCode\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>\d+)
            • Maine: CODE ME. R. § [section] - Regex: Code\sMe\.\sR\.?\s§\s(?P<section_num>[\d\s-]+)
            • Maryland: CODE MD. REGS. [code] - Regex: Code\sMd\.\sRegs\.?\s(?P<rule_num>[\d\s.]+)
            • Massachusetts: [code] CODE MASS. REGS. [section] - Regex: (?P<title_num>\d+)\sCode\sMass\.\sRegs\.?\s(?P<section_num>[\d.]+)
            • Michigan: MICH. ADMIN. CODE r. [rule] - Regex: Mich\.\sAdmin\.\sCode\sr\.\s(?P<rule_num>[\d.]+)
            • Minnesota: MINN. R. [rule] - Regex: Minn\.\sR\.\s(?P<rule_num>[\d.]+)
            • Mississippi: MISS. CODE R. § [section] - Regex: Miss\.\sCode\sR\.\s§\s(?P<section_num>[\d\s-]+)
            • Missouri: MO. CODE REGS. ANN. tit. [title], § [section] - Regex: Mo\.\sCode\sRegs\.?\sAnn\.?\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>[\d-]+)
            • Montana: ADMIN. R. MONT. [rule] - Regex: Admin\.\sR\.\sMont\.?\s(?P<rule_num>[\d.]+)
            • Nebraska: NEB. ADMIN. R. & REGS. [rule] - Regex: Neb\.\sAdmin\.\sR\.\s&\sRegs\.?\s(?P<rule_num>[\d\s-]+)
            • Nevada: NEV. ADMIN. CODE § [section] - Regex: Nev\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d.]+)
            • New Hampshire: N.H. CODE ADMIN. R. [rule] - Regex: N\.H\.\sCode\sAdmin\.\sR\.\s(?P<rule_num>[\w\s.]+)
            • New Jersey: N.J. ADMIN. CODE § [section] - Regex: N\.J\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d:-]+)
            • New Mexico: N.M. ADMIN. CODE § [section] - Regex: N\.M\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d.]+)
            • New York: N.Y. COMP. CODES R. & REGS. tit. [title], § [section] - Regex: N\.Y\.\sComp\.\sCodes\sR\.\s&\sRegs\.?\stit\.\s(?P<title_num>\d+),\s§\s(?P<section_num>[\d.]+)
            • North Carolina: N.C. ADMIN. CODE tit. [title], r. [rule] - Regex: N\.C\.\sAdmin\.\sCode\stit\.\s(?P<title_num>\d+),\sr\.\s(?P<rule_num>[\d.]+)
            • North Dakota: N.D. ADMIN. CODE § [section] - Regex: N\.D\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d.-]+)
            • Ohio: OHIO ADMIN. CODE § [section] - Regex: Ohio\sAdmin\.\sCode\s§\s(?P<section_num>[\d:-]+)
            • Oklahoma: OKLA. ADMIN. CODE § [section] - Regex: Okla\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d:-]+)
            • Oregon: OR. ADMIN. R. [rule] - Regex: Or\.\sAdmin\.\sR\.\s(?P<rule_num>[\d-]+)
            • Pennsylvania: [title] PA. CODE § [section] - Regex: (?P<title_num>\d+)\sPa\.\sCode\s§\s(?P<section_num>[\d.]+)
            • Rhode Island: CODE R.I. R. § [section] - Regex: Code\sR\.I\.\sR\.?\s§\s(?P<section_num>[\d-]+)
            • South Carolina: S.C. CODE REGS. [regulation] - Regex: S\.C\.\sCode\sRegs\.?\s(?P<rule_num>[\d-]+)
            • South Dakota: S.D. ADMIN. R. [rule] - Regex: S\.D\.\sAdmin\.\sR\.\s(?P<rule_num>[\d:]+)
            • Tennessee: TENN. COMP. R. & REGS. [rule] - Regex: Tenn\.\sComp\.\sR\.\s&\sRegs\.?\s(?P<rule_num>[\d-]+)
            • Texas: [title] TEX. ADMIN. CODE § [section] - Regex: (?P<title_num>\d+)\sTex\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d.]+)
            • Utah: UTAH ADMIN. CODE r. [rule] - Regex: Utah\sAdmin\.\sCode\sr\.\s(?P<rule_num>[\d-]+)
            • Vermont: CODE VT. R. [rule] - Regex: Code\sVt\.\sR\.\s(?P<rule_num>[\d\s-]+)
            • Virginia: [title] VA. ADMIN. CODE [section] - Regex: (?P<title_num>\d+)\sVa\.\sAdmin\.\sCode\s(?P<section_num>[\d.-]+)
            • Washington: WASH. ADMIN. CODE § [section] - Regex: Wash\.\sAdmin\.\sCode\s§\s(?P<section_num>[\d-]+)
            • West Virginia: W. VA. CODE R. § [section] - Regex: W\.\sVa\.\sCode\sR\.\s§\s(?P<section_num>[\d-]+)
            • Wisconsin: WIS. ADMIN. CODE [code] § [section] - Regex: Wis\.\sAdmin\.\sCode\s(?P<reporter>[\w]+)\s§\s(?P<section_num>[\d.]+)
            • Wyoming: [agency code] WYO. CODE R. § [section] - Regex: (?P<title_num>\d+)\sWyo\.\sCode\sR\.\s§\s(?P<section_num>\d+)
3. Court Rules
    ◦ Data Model: CourtRuleCitation.
    ◦ Federal Court Rules:
        ▪ Federal Rules of Civil Procedure:
            • Format: FED. R. CIV. P. 56
            • Regex: Fed\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ Federal Rules of Criminal Procedure:
            • Format: FED. R. CRIM. P. 16
            • Regex: Fed\.\sR\.\sCrim\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ Federal Rules of Evidence:
            • Format: FED. R. EVID. 803
            • Regex: Fed\.\sR\.\sEvid\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ Federal Rules of Appellate Procedure:
            • Format: FED. R. APP. P. 28
            • Regex: Fed\.\sR\.\sApp\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ Federal Rules of Bankruptcy Procedure:
            • Format: FED. R. BANKR. P. 3007
            • Regex: Fed\.\sR\.\sBankr\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ Rules of the Supreme Court of the United States:
            • Format: SUP. CT. R. 10
            • Regex: Sup\.\sCt\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
        ▪ General Federal Pattern:
            • Format: FED. R. CIV. P. 56
            • Regex: FED\.\sR\.\s(?P<rule_type>[\w\d\s\.]+)\s(?P<rule_num>[\d\w\.]+)
    ◦ State-Specific Court Rules:
        ▪ Combined Regex (STATE_COURT_RULES_REGEX): (?:Conn\.\sPrac\.\sBook\s§\s(?P<rule_num_ct>[\w\d.-]+)|La\.\sCode\sCiv\.\sProc\.\sAnn\.?\sart\.\s(?P<rule_num_la>[\w\d.()-]+)|N\.Y\.\sC\.P\.L\.R\.\s(?P<rule_num_ny>[\w\d.()-]+)|Va\.\sSup\.\sCt\.\sR\.\s(?P<rule_num_va>[\d:]+)|Ala\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_al>[\w\d.()-]+)|Alaska\sR\.\sCiv\.\sP\.\s(?P<rule_num_ak>[\w\d.()-]+)|Ariz\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_az>[\w\d.()-]+)|Ark\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_ar>[\w\d.()-]+)|Cal\.\sR\.\sCt\.\s(?P<rule_num_ca>[\w\d.()-]+)|Colo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_co>[\w\d.()-]+)|Del\.\sSuper\.\sCt\.\sCiv\.\sR\.\s(?P<rule_num_de>[\w\d.()-]+)|D\.C\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_dc>[\w\d.()-]+)|Fla\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_fl>[\w\d.()-]+)|Ga\.\sCode\sAnn\.?\s§\s(?P<rule_num_ga>[\d-]+)|Haw\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_hi>[\w\d.()-]+)|Idaho\sR\.\sCiv\.\sP\.\s(?P<rule_num_id>[\w\d.()-]+)|Ill\.\sSup\.\sCt\.\sR\.\s(?P<rule_num_il>[\w\d.()-]+)|Ind\.\sR\.\sTrial\sP\.\s(?P<rule_num_in>[\w\d.()-]+)|Iowa\sR\.\sCiv\.\sP\.\s(?P<rule_num_ia>[\w\d.()-]+)|Kan\.\sStat\.?\sAnn\.?\s§\s(?P<rule_num_ks>[\d-]+)|Ky\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_ky>[\w\d.()-]+)|Me\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_me>[\w\d.()-]+)|Md\.\sR\.\s(?P<rule_num_md>[\d-]+)|Mass\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_ma>[\w\d.()-]+)|Mich\.\sCt\.\sR\.\s(?P<rule_num_mi>[\w\d.()-]+)|Minn\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_mn>[\w\d.()-]+)|Miss\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_ms>[\w\d.()-]+)|Mo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_mo>[\w\d.()-]+)|Mont\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_mt>[\w\d.()-]+)|Neb\.\sCt\.\sR\.\s(?P<rule_num_ne>[\w\d.()-]+)|Nev\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_nv>[\w\d.()-]+)|N\.H\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_nh>[\w\d.()-]+)|N\.J\.\sCt\.\sR\.\s(?P<rule_num_nj>[\d:-]+)|N\.M\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_nm>[\w\d.()-]+)|N\.C\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_nc>[\w\d.()-]+)|N\.D\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_nd>[\w\d.()-]+)|Ohio\sR\.\sCiv\.\sP\.\s(?P<rule_num_oh>[\w\d.()-]+)|Okla\.\sStat\.?\stit\.\s(?P<title_num_ok>\d+),\s§\s(?P<rule_num_ok>[\w\d.()-]+)|Or\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_or>[\w\d.()-]+)|Pa\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_pa>[\w\d.()-]+)|R\.I\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_ri>[\w\d.()-]+)|S\.C\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_sc>[\w\d.()-]+)|S\.D\.\sCodified\sLaws\s§\s(?P<rule_num_sd>[\d-]+)|Tenn\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_tn>[\w\d.()-]+)|Tex\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_tx>[\w\d.()-]+)|Utah\sR\.\sCiv\.\sP\.\s(?P<rule_num_ut>[\w\d.()-]+)|Vt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_vt>[\w\d.()-]+)|Wash\.\sSuper\.\sCt\.\sCiv\.\sR\.\s(?P<rule_num_wa>[\w\d.()-]+)|W\.\sVa\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_wv>[\w\d.()-]+)|Wis\.\sStat\.?\s§\s(?P<rule_num_wi>[\d.]+)|Wyo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num_wy>[\w\d.()-]+)). Specific states with unique formats are placed early in the combined regex.
        ▪ General State Pattern:
            • Format: CAL. R. CT. 3.110
            • Regex: (?P<state_abbr>[A-Z]{2,4}\.)\sR\.\s(?P<court_abbr>[\w\d\s\.]+)\s(?P<rule_num>[\d\w\.]+)
        ▪ Representative Sample of State Formats and Regex:
            • Alabama: ALA. R. CIV. P. [rule] - Regex: Ala\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Alaska: ALASKA R. CIV. P. [rule] - Regex: Alaska\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Arizona: ARIZ. R. CIV. P. [rule] - Regex: Ariz\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Arkansas: ARK. R. CIV. P. [rule] - Regex: Ark\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • California: CAL. R. CT. [rule] - Regex: Cal\.\sR\.\sCt\.\s(?P<rule_num>[\w\d.()-]+)
            • Colorado: COLO. R. CIV. P. [rule] - Regex: Colo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Connecticut: CONN. PRAC. BOOK § [section] - Regex: Conn\.\sPrac\.\sBook\s§\s(?P<rule_num>[\w\d.-]+)
            • Delaware: DEL. SUPER. CT. CIV. R. [rule] - Regex: Del\.\sSuper\.\sCt\.\sCiv\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
            • District of Columbia: D.C. SUPER. CT. R. CIV. P. [rule] - Regex: D\.C\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Florida: FLA. R. CIV. P. [rule] - Regex: Fla\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Georgia: GA. CODE ANN. § [section] (Rules are part of statutes) - Regex: Ga\.\sCode\sAnn\.?\s§\s(?P<rule_num>[\d-]+)
            • Hawaii: HAW. R. CIV. P. [rule] - Regex: Haw\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Idaho: IDAHO R. CIV. P. [rule] - Regex: Idaho\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Illinois: ILL. SUP. CT. R. [rule] - Regex: Ill\.\sSup\.\sCt\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
            • Indiana: IND. R. TRIAL P. [rule] - Regex: Ind\.\sR\.\sTrial\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Iowa: IOWA R. CIV. P. [rule] - Regex: Iowa\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Kansas: KAN. STAT. ANN. § [section] (Rules are part of statutes) - Regex: Kan\.\sStat\.?\sAnn\.?\s§\s(?P<rule_num>[\d-]+)
            • Kentucky: KY. R. CIV. P. [rule] - Regex: Ky\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Louisiana: LA. CODE CIV. PROC. ANN. art. [article] - Regex: La\.\sCode\sCiv\.\sProc\.\sAnn\.?\sart\.\s(?P<rule_num>[\w\d.()-]+)
            • Maine: ME. R. CIV. P. [rule] - Regex: Me\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Maryland: MD. R. [rule] - Regex: Md\.\sR\.\s(?P<rule_num>[\d-]+)
            • Massachusetts: MASS. R. CIV. P. [rule] - Regex: Mass\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Michigan: MICH. CT. R. [rule] - Regex: Mich\.\sCt\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
            • Minnesota: MINN. R. CIV. P. [rule] - Regex: Minn\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Mississippi: MISS. R. CIV. P. [rule] - Regex: Miss\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Missouri: MO. R. CIV. P. [rule] - Regex: Mo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Montana: MONT. R. CIV. P. [rule] - Regex: Mont\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Nebraska: NEB. CT. R. [rule] - Regex: Neb\.\sCt\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
            • Nevada: NEV. R. CIV. P. [rule] - Regex: Nev\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • New Hampshire: N.H. SUPER. CT. R. CIV. P. [rule] - Regex: N\.H\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • New Jersey: N.J. CT. R. [rule] - Regex: N\.J\.\sCt\.\sR\.\s(?P<rule_num>[\d:-]+)
            • New Mexico: N.M. R. CIV. P. [rule] - Regex: N\.M\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • New York: N.Y. C.P.L.R. [rule] - Regex: N\.Y\.\sC\.P\.L\.R\.\s(?P<rule_num>[\w\d.()-]+)
            • North Carolina: N.C. R. CIV. P. [rule] - Regex: N\.C\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • North Dakota: N.D. R. CIV. P. [rule] - Regex: N\.D\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Ohio: OHIO R. CIV. P. [rule] - Regex: Ohio\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Oklahoma: OKLA. STAT. tit. [title], § [section] (Rules are part of statutes) - Regex: Okla\.\sStat\.?\stit\.\s(?P<title_num>\d+),\s§\s(?P<rule_num>[\w\d.()-]+)
            • Oregon: OR. R. CIV. P. [rule] - Regex: Or\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Pennsylvania: PA. R. CIV. P. [rule] - Regex: Pa\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Rhode Island: R.I. SUPER. CT. R. CIV. P. [rule] - Regex: R\.I\.\sSuper\.\sCt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • South Carolina: S.C. R. CIV. P. [rule] - Regex: S\.C\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • South Dakota: S.D. CODIFIED LAWS § [section] (Rules are part of statutes) - Regex: S\.D\.\sCodified\sLaws\s§\s(?P<rule_num>[\d-]+)
            • Tennessee: TENN. R. CIV. P. [rule] - Regex: Tenn\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Texas: TEX. R. CIV. P. [rule] - Regex: Tex\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Utah: UTAH R. CIV. P. [rule] - Regex: Utah\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Vermont: VT. R. CIV. P. [rule] - Regex: Vt\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Virginia: VA. SUP. CT. R. [rule] - Regex: Va\.\sSup\.\sCt\.\sR\.\s(?P<rule_num>[\d:]+)
            • Washington: WASH. SUPER. CT. CIV. R. [rule] - Regex: Wash\.\sSuper\.\sCt\.\sCiv\.\sR\.\s(?P<rule_num>[\w\d.()-]+)
            • West Virginia: W. VA. R. CIV. P. [rule] - Regex: W\.\sVa\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
            • Wisconsin: WIS. STAT. § [section] (Rules are part of statutes) - Regex: Wis\.\sStat\.?\s§\s(?P<rule_num>[\d.]+)
            • Wyoming: WYO. R. CIV. P. [rule] - Regex: Wyo\.\sR\.\sCiv\.\sP\.\s(?P<rule_num>[\w\d.()-]+)
4. Legislation (Uncodified: Bills & Session Laws)
    ◦ Data Models: LegislativeBillCitation, SessionLawCitation.
    ◦ Federal Legislation:
        ▪ House of Representatives Bills:
            • Format: H.R. 25, 118th Cong. (2023)
            • Regex: H\.R\.\s(?P<bill_num>\d+),\s(?P<congress_num>\d+)th\sCong\.
        ▪ Senate Bills:
            • Format: S. 123, 118th Cong. (2023)
            • Regex: S\.\s(?P<bill_num>\d+),\s(?P<congress_num>\d+)th\sCong\.
        ▪ Federal Session Laws (Statutes at Large):
            • Format: Pub. L. No. 94-579, § 102, 90 Stat. 2743
            • Regex: Pub\.\sL\.\sNo\.\s(?P<law_num>[\d-]+),\s(?:§\s(?P<section_num>[\d\w-]+),)?\s(?P<volume_num>\d+)\sStat\.\s(?P<page_num>[\d,\s]+)
    ◦ State-Specific Legislation (Bills & Session Laws):
        ▪ Combined Regex for State Session Laws (STATE_SESSION_LAWS_REGEX): Mentioned as being combined using the | operator for all 50 state session law regex patterns.
        ▪ Generic State Bill Pattern:
            • Format Example: Va. H.B. 145, 118th Gen. Assemb., Reg. Sess. (2025)
            • Regex: (?P<state_abbr>[A-Z]{2,4}\.\s)?(?P<bill_type>H\.B\.|S\.B\.|A\.B\.|H\.F\.|S\.F\.)\s(?P<bill_num>\d+)(?:,\s(?P<session_info>[\w\s\d.-]+))?\s\((?P<year>\d{4})\). This pattern aims to capture common structures but may miss variations and incur false positives.
        ▪ Generic State Session Law Pattern:
            • Format Example (Virginia): 2025 Va. Acts 45
            • Regex (Virginia Example): (?P<year>\d{4})\sVa\.\sActs\s(?P<chapter_num>[\d\w-]+)
        ▪ Representative Sample of State Session Law Formats and Regex:
            • Alabama: [year] Ala. Acts [act number] - Regex: (?P<year>\d{4})\sAla\.\sActs\s(?P<act_num>[\d\w-]+)
            • Alaska: [year] Alaska Sess. Laws [chapter number] - Regex: (?P<year>\d{4})\sAlaska\sSess\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Arizona: [year] Ariz. Sess. Laws [chapter number] - Regex: (?P<year>\d{4})\sAriz\.\sSess\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Arkansas: [year] Ark. Acts [act number] - Regex: (?P<year>\d{4})\sArk\.\sActs\s(?P<act_num>[\d\w-]+)
            • California: [year] Cal. Stat. [page number] - Regex: (?P<year>\d{4})\sCal\.\sStat\.\s(?P<page_num>[\d\w-]+)
            • Colorado: [year] Colo. Sess. Laws [page number] - Regex: (?P<year>\d{4})\sColo\.\sSess\.\sLaws\s(?P<page_num>[\d\w-]+)
            • Connecticut: [year] Conn. Acts [act number] - Regex: (?P<year>\d{4})\sConn\.\sActs\s(?P<act_num>[\d\w-]+)
            • Delaware: [volume] Del. Laws [chapter number] ([year]) - Regex: (?P<volume>\d+)\sDel\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Florida: [year] Fla. Laws [chapter number] - Regex: (?P<year>\d{4})\sFla\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Georgia: [year] Ga. Laws [page number] - Regex: (?P<year>\d{4})\sGa\.\sLaws\s(?P<page_num>[\d\w-]+)
            • Hawaii: [year] Haw. Sess. Laws [page number] - Regex: (?P<year>\d{4})\sHaw\.\sSess\.\sLaws\s(?P<page_num>[\d\w-]+)
            • Idaho: [year] Idaho Sess. Laws [page number] - Regex: (?P<year>\d{4})\sIdaho\sSess\.\sLaws\s(?P<page_num>[\d\w-]+)
            • Illinois: [year] Ill. Laws [public act number] - Regex: (?P<year>\d{4})\sIll\.\sLaws\s(?P<act_num>[\d\w-]+)
            • Indiana: [year] Ind. Acts [public law number] - Regex: (?P<year>\d{4})\sInd\.\sActs\s(?P<law_num>[\d\w-]+)
            • Iowa: [year] Iowa Acts [chapter number] - Regex: (?P<year>\d{4})\sIowa\sActs\s(?P<chapter_num>[\d\w-]+)
            • Kansas: [year] Kan. Sess. Laws [page number] - Regex: (?P<year>\d{4})\sKan\.\sSess\.\sLaws\s(?P<page_num>[\d\w-]+)
            • Kentucky: [year] Ky. Acts [chapter number] - Regex: (?P<year>\d{4})\sKy\.\sActs\s(?P<chapter_num>[\d\w-]+)
            • Louisiana: [year] La. Acts [act number] - Regex: (?P<year>\d{4})\sLa\.\sActs\s(?P<act_num>[\d\w-]+)
            • Maine: [year] Me. Laws [chapter number] - Regex: (?P<year>\d{4})\sMe\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Maryland: [year] Md. Laws [chapter number] - Regex: (?P<year>\d{4})\sMd\.\sLaws\s(?P<chapter_num>[\d\w-]+)
            • Massachusetts: [year] Mass. Acts [chapter number] - Regex: (?P<year>\d{4})\sMass\.\sActs\s(?P<chapter_num>[\d\w-]+)
            • Michigan: [year] Mich. Pub. Acts [public act number] - Regex: (?P<year>\d{4})\sMich\.\sPub\.\sActs\s(?P<act_num>[\d\w-]+)
            • Minnesota: [year] Minn. Laws [chapter number] - Regex: (?P<year>\d{4})\sMinn\.\sLaws\s(?P<chapter_num>[\d\w-]+)
