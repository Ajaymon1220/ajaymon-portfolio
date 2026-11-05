"""Ajaymon's portfolio content. Edit this file, then run `python3 build_ajay.py`.

Text in a paragraph may be a plain string or a list mixing strings and
("hl", "highlighted text") tuples, which render with the site's marker highlight.
Image paths are relative to the archive profile folder and are copied into dist/profile/work/.
"""

CONTACT_EMAIL = "aj.design.mon@gmail.com"  # where "leave me a note" messages are delivered (via formsubmit.co)

SITE = None  # set to your deployed origin (e.g. "https://example.com") to emit canonical/og:url tags

PROJECTS = [
    {
        "slug": "karbon-invoice-flow",
        "title": "Karbon Invoice Flow",
        "summary": "Bringing invoice creation, review and payment reminders into one guided flow for exporters getting paid through Karbon.",
        "details": [("Role", "Product Designer"), ("Client", "Karbon Business"), ("Services", "Product Design, Interaction Design"), ("Year", "2024")],
        "services": ["Product Design", "Interaction Design"],
        "cover": ("invoice/overview.png", 2048, 1004, "Karbon’s invoice confirmation screen: the finished invoice beside the amount, due date and a shareable payment link"),
        "slides": ["invoice/overview.png", "invoice/flow.png", "invoice/details.png"],
        "sections": [
            ("Getting paid meant switching tools", [
                "Exporters using Karbon were creating invoices in a separate tool, uploading the PDF, typing the payment details in again and then chasing their customers by hand.",
                "The problem was bigger than a long form. People were juggling commercial details, unfamiliar purpose codes and the question of what their customer would actually receive.",
                ["The redesign brings those scattered steps into ", ("hl", "one guided flow"), ": choose the type of request, add customer and payment details, review the invoice beside the form, and set up reminders before you finish."],
            ]),
            ("One flow, three priorities", [
                "Freelancers wanted a quick way to request money without heavy invoice setup. Finance teams needed accurate details and a clearer place to handle purpose codes. Operations leads wanted recurring requests and reminders that cut down repetitive follow-up.",
                "Conversations with users kept coming back to the same three themes: invoices created elsewhere, uncertainty around purpose codes, and manual follow-ups. Those themes shaped the flow.",
            ]),
            ("Start with what they want to send", [
                "One-time invoices, recurring invoices and payment links serve different needs, so the flow opens by asking which one you’re after. Knowing the intent first gives every later step a clearer job.",
                ("figure", "invoice/flow.png", 2048, 1294, "The first step of the flow: choosing between a one-time invoice, a recurring series and a payment link, with the invoice preview alongside", "Intent first. The preview sits beside the choice from the very first step."),
            ]),
            ("Review while you create", [
                ["A split screen keeps the document next to the inputs, so people can ", ("hl", "check customer details and amounts as they go"), " instead of discovering the invoice only after they submit it."],
                "Payment details and purpose codes live in separate steps. Grouping amounts apart from regulatory information means fewer unrelated decisions compete for attention on a single screen.",
                ("figure", "invoice/details.png", 2048, 1375, "Invoice setup screen with customer, line items and payment terms on the left and the invoice taking shape on the right", "Customer, line items and terms on one side; the invoice your customer will see on the other."),
            ]),
            ("Follow-up as part of setup", [
                "Reminder scheduling comes at the end of the flow, with options around the due date. It answers the manual chasing operations teams described, without interrupting invoice entry.",
                "The next thing I’d test is whether people understand that a payment link doesn’t produce an invoice. The proposed fix: change the preview title and drop invoice-only fields when that option is chosen, then watch whether people notice the change.",
            ]),
        ],
    },
    {
        "slug": "taxos",
        "title": "TaxOS",
        "summary": "AI-assisted tax preparation for Payvio: a client portal and a CPA workspace that turn scattered documents into a clear starting point.",
        "details": [("Role", "Product Designer"), ("Client", "Payvio Ltd."), ("Services", "Product Design, Prototyping"), ("Year", "2025–2026")],
        "services": ["Product Design", "Prototyping"],
        "cover": ("taxos/overview.png", 2048, 1362, "The TaxOS CPA workspace listing client accounts, return types, preparation progress and status"),
        "slides": ["taxos/overview.png", "taxos/dashboard.png", "taxos/workflow.png"],
        "sections": [
            ("The work started long before the return", [
                "Offshore teams preparing US tax returns were losing time before the real work began. Clients received requests in separate messages and were left guessing what was still missing. CPAs received files that still had to be matched against task lists and re-entered into Excel before preparation could start.",
                ["A client has the files. A CPA needs the facts. ", ("hl", "I designed the workflow that connects them.")],
            ]),
            ("Two sides of the same handoff", [
                "The CPA needs to find what’s missing and get started. The client wants to know exactly what’s needed from them. The firm lead needs the whole team moving through tax season.",
                "Discovery pointed to one shared bottleneck: collecting and organising information before preparation could begin. Research, domain mapping with a tax consultant and engineering were team efforts; my part was the interface and the prototype.",
            ]),
            ("Two doors, one workflow", [
                "Clients provide information; CPAs prepare the work. Each gets a focused space. On the client side, adaptive intake asks only the questions that matter and links each answer to the documents they need to upload.",
                "On the CPA side, assisted matching and extraction bring received files and preparation requirements together, so the work starts from organised inputs instead of a folder of attachments.",
                ("figure", "taxos/dashboard.png", 2048, 1362, "A TaxOS client account in the CPA workspace, with received documents grouped by type and their review status", "The CPA workspace: every document has a place and a status."),
            ]),
            ("Make it work before building it", [
                ["I turned the Figma designs into a ", ("hl", "functional prototype"), ", using Claude Code for the backend logic, GitHub for version control and Vercel for deployment. Mock tax data let CPAs try the flow before production development."],
                "The prototype was for testing interactions and workflow. It doesn’t establish the accuracy of AI-generated tax information, which is a separate question for the product team.",
                ("figure", "taxos/workflow.png", 2048, 1024, "The TaxOS home dashboard with total returns, active clients, a client status chart and an agenda", "The prototype’s dashboard, running on mock tax data."),
            ]),
            ("From prototype to a second version", [
                "Market research and high-fidelity exploration set the direction. Version one went into beta with the CPA network recruited during discovery. Version two refined the dynamic questionnaire and bulk document matching ahead of the commercial launch.",
                "My takeaway: the useful role for AI starts with a clear workflow. Faster generation only helps when the next person can understand, review and act on the result.",
            ]),
        ],
    },
    {
        "slug": "swift-code-finder",
        "title": "SWIFT Code Finder",
        "summary": "A focused search and validation tool that helps people find, or double-check, the right bank code for an international transfer.",
        "details": [("Role", "UX Research & Product Design"), ("Services", "Research, Interaction Design"), ("Year", "2025")],
        "services": ["Research", "Interaction Design"],
        "cover": ("project-2-0.png", 2747, 1624, "A Karbon web tool asking “How much will you receive?”, with currency and amount fields and a result panel"),
        "slides": ["project-2-0.png", "project-2-1.png", "project-2-2.png"],
        "sections": [
            ("A small code, a lot of uncertainty", [
                "People preparing an international transfer need the right bank identifier, or need to check one they already have. Searching across websites leaves them comparing unfamiliar bank and branch details with no consistent way to tell which result fits.",
                ["The direction was simple: ", ("hl", "choose a country, a bank and a branch"), ", review the matching details, and copy the result with clear feedback. People who already have a code get their own path to check it."],
            ]),
            ("The needs behind the interface", [
                "Finding a code calls for a guided search that narrows the options without assuming prior knowledge. Checking a code calls for a direct way to inspect one. Either way, people need enough context to connect the result to the bank they meant.",
                "I looked at how people find SWIFT codes, what frustrates them and how they read the parts of a code. Trust, speed and support for double-checking shaped the priorities.",
                ("figure", "project-2-1.png", 2560, 656, "A user journey map with rows for actions, task list, feelings and improvement opportunities across each stage of finding a SWIFT code", "Mapping the journey: what people do, how they feel and where the design can help."),
            ]),
            ("Four decisions", [
                "Guide the search in steps: country, bank and branch give a clear order to follow. Give known codes a separate path, so validation doesn’t get in the way of searching.",
                ["Explain without interrupting: short notes sit beside results, so the main task stays finding and using the code. And make the result usable, with a ", ("hl", "one-tap copy"), " right next to it and clear feedback that it worked."],
                ("figure", "project-2-2.png", 7072, 3000, "A user flow diagram branching from the entry point into the search path and the validation path, ending in result states", "The flow: search and validation split early and meet again at the result."),
            ]),
            ("What I’d test next", [
                "Can people tell the difference between finding a code and checking one they already have? I’d make both entry points explicit, keep the identifying bank details beside every result, and give participants one task of each kind to see which path they pick first.",
            ]),
        ],
    },
    {
        "slug": "karbon-design-system",
        "title": "Karbon Design System",
        "summary": "Reusable components and shared foundations that keep Karbon’s growing fintech products consistent.",
        "details": [("Role", "Product Designer"), ("Client", "Karbon Business"), ("Services", "Design Systems, Component Design"), ("Year", "2024–Present")],
        "services": ["Design Systems", "Component Design"],
        "cover": ("project-3-0.png", 3840, 1920, "The Karbon Design System Kit cover beside a type specimen of Poppins styles and a colour palette"),
        "slides": ["project-3-0.png", "project-3-1.png", "project-3-2.png"],
        "sections": [
            ("As the product grew, the patterns drifted", [
                "Similar components were being rebuilt feature by feature, and visual differences kept surfacing during handoff. It was getting harder for design and development to keep the product coherent.",
                ["The goal was to give those repeated decisions ", ("hl", "a shared foundation"), ": common typography, spacing and colour, reusable components and patterns, and documentation that sits right beside them."],
            ]),
            ("Who it needed to work for", [
                "Designers need building blocks that make consistent screens easier to create. Developers need components and documentation that map onto how they actually build. And the people using Karbon need things to behave the same way as they move between workflows.",
                "I audited the existing UI, found the opportunities for consistency and reuse, and worked with developers on the components and their documentation.",
                ("figure", "project-3-1.png", 3489, 2781, "A laptop on a dark surface displaying a Karbon product screen built from the design system", "Components in context, inside a Karbon product screen."),
            ]),
            ("Four decisions", [
                ["Start from the existing interface, so the foundations reflect what the product really needs. Connect design to development: Figma components line up with ", ("hl", "Tailwind CSS, shadcn and Lucide"), " on the engineering side."],
                "Make reuse understandable with guidelines alongside every component. And keep feedback part of the system: a component has to work across the product’s use cases, not just look consistent on one screen.",
                ("figure", "project-3-2.png", 3210, 2268, "A laptop showing a grid of Karbon interface components and states", "A shared library spanning typography, spacing, colour and interface patterns."),
            ]),
            ("What I’d test next", [
                "Can another designer pick and configure the right component without asking its author? I’d add short usage examples and document the relevant states, then ask a teammate to build a small screen and note every detached component or unclear guideline.",
            ]),
        ],
    },
    {
        "slug": "karbon-business",
        "title": "Karbon Business",
        "summary": "A clearer, responsive website for a complex cross-border payments product.",
        "details": [("Role", "UX & Interface Design"), ("Client", "Karbon Business"), ("Services", "Web Design, Responsive UX"), ("Year", "2024–Present")],
        "services": ["Web Design", "Responsive UX"],
        "cover": ("project-4-0.png", 2304, 1422, "The Karbon Business homepage hero reading “Effortless Global Payments”, with partner bank logos below"),
        "slides": ["project-4-0.png", "project-4-1.png", "project-4-2.png"],
        "sections": [
            ("A clearer route through the product story", [
                "Karbon’s website needed stronger navigation, a more deliberate content hierarchy and layouts that hold up on any screen. Visitors were working through competing priorities to understand the product and find what was relevant to them.",
                ["I refined the ", ("hl", "navigation, typography and responsive layouts"), " across the site, so each section has a clear job and the same journey works on a phone."],
            ]),
            ("The needs behind the interface", [
                "First-time visitors need a clear explanation of the product and where to start. People comparing capabilities need readable product information and navigation that gets them to the right feature. Mobile visitors need a hierarchy that doesn’t depend on desktop space.",
                ("figure", "project-4-1.png", 4202, 1264, "A four-stage process map from discovery through UX design and UI design to Webflow development", "From discovery to Webflow build, in four stages."),
            ]),
            ("Four decisions", [
                "Structure information around navigation, so visitors can choose a path and find the relevant product detail. Design for smaller screens from the start, rather than treating responsive layouts as an afterthought.",
                ["Use one visual language across sections, and connect content decisions with interface decisions: ", ("hl", "clearer typography only helps when it supports a sequence people can follow"), "."],
                ("figure", "project-4-2.png", 2304, 1525, "A “Why choose Karbon FX?” section with four benefits arranged around a phone showing the Karbon app", "Benefits arranged around the product itself."),
            ]),
            ("What I’d test next", [
                "Can a first-time visitor quickly find the information for a specific need? I’d try task-specific navigation labels and easier-to-spot section headings, then run the same task on desktop and mobile, recording first clicks, wrong turns and how people describe what they found.",
            ]),
        ],
    },
]

# Playground tiles: (image, width, height, alt, project slug or None)
PLAYGROUND = [
    ("invoice/overview.png", 2048, 1004, "Karbon invoice confirmation with a shareable payment link", "karbon-invoice-flow"),
    ("invoice/flow.png", 2048, 1294, "Choosing a payment request type beside the invoice preview", "karbon-invoice-flow"),
    ("playground/countryside-footer.svg", 1600, 1000, "Slowly, thoughtfully — Ajaymon’s animated countryside footer study", "footer-study"),
    ("taxos/overview.png", 2048, 1362, "TaxOS CPA workspace with client preparation progress", "taxos"),
    ("taxos/dashboard.png", 2048, 1362, "TaxOS client documents grouped by type and status", "taxos"),
    ("taxos/workflow.png", 2048, 1024, "TaxOS dashboard with returns, clients and agenda", "taxos"),
    ("project-1-0.png", 3151, 1928, "Karbon Forex virtual accounts and ongoing invoices on a laptop", None),
    ("project-1-2.png", 2664, 1318, "Two Karbon Forex personas: a freelance designer and an export CFO", None),
    ("project-1-1.png", 4202, 1402, "Karbon Forex process from discovery to developer handoff", None),
    ("project-2-0.png", 2747, 1624, "Karbon payout calculator: how much will you receive?", "swift-code-finder"),
    ("project-2-1.png", 2560, 656, "SWIFT Code Finder user journey map", "swift-code-finder"),
    ("project-2-2.png", 7072, 3000, "SWIFT Code Finder search and validation flow", "swift-code-finder"),
    ("project-3-0.png", 3840, 1920, "Karbon Design System Kit with type and colour foundations", "karbon-design-system"),
    ("project-3-1.png", 3489, 2781, "Karbon product screen built from the design system", "karbon-design-system"),
    ("project-3-2.png", 3210, 2268, "Karbon interface components on a laptop", "karbon-design-system"),
    ("project-4-0.png", 2304, 1422, "Karbon Business homepage: Effortless Global Payments", "karbon-business"),
    ("project-4-1.png", 4202, 1264, "Karbon website process from discovery to Webflow build", "karbon-business"),
    ("project-4-2.png", 2304, 1525, "Why choose Karbon FX? section with the app on a phone", "karbon-business"),
]
