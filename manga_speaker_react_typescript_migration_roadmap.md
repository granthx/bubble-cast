# Anti-Gravity Roadmap: Rebuild Manga Speaker as a Modern Web Application

## Mission

Completely replace the current Streamlit presentation layer with a
polished, production-quality web frontend for **Manga Speaker ---
Multimodal Manga Reader & Dialogue Intelligence**.

The user explicitly does not want a Streamlit UI. **Do not spend time
polishing or extending the Streamlit interface.** Build a real frontend
using **React + TypeScript + Vite + HTML semantics + CSS**, connected to
the existing Python/model code through a clean API layer.

The objective is not a visual mockup. Implement a working application
that preserves the current manga-analysis capabilities, connects to real
data and inference, and can be run locally.

## Architecture decision

Use this stack unless repository inspection reveals a concrete
compatibility issue:

### Frontend

-   React
-   TypeScript with strict type checking
-   Vite for development/build tooling
-   CSS Modules or a clearly organized global CSS design system.
    Tailwind CSS is acceptable if already installed or if it materially
    speeds up consistent styling; do not mix several styling systems
    without reason.
-   React Router for main application routes if multiple full-page
    workspaces are needed.
-   Lucide icons (or an existing equivalent icon library) for
    consistent, accessible icons.
-   A lightweight charting library only if the existing application has
    real chart data that needs to be displayed.
-   Use semantic HTML and accessible native controls wherever practical.

### Backend and model layer

-   Preserve Python and the existing model/inference/data-processing
    code.
-   Prefer **FastAPI** as the HTTP API layer if the project does not
    already have an API server. If a working API layer already exists,
    reuse it rather than creating a duplicate.
-   Keep model loading and inference on the Python side.
-   The frontend must call real backend endpoints. Never hardcode sample
    predictions as if they were real.
-   Use REST endpoints for standard actions and Server-Sent Events or
    WebSockets only if the existing processing workflow needs real-time
    progress updates.
-   Keep file uploads, model inference, sequence data, character
    mappings, dialogue ordering, and exports in the backend.
-   Do not move ML inference into the browser.

### Suggested project layout

Adapt this to the actual repository instead of blindly creating
duplicate folders:

``` text
manga-speaker/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       │   ├── App.tsx
│       │   ├── router.tsx
│       │   └── providers.tsx
│       ├── components/
│       │   ├── layout/
│       │   ├── ui/
│       │   ├── manga/
│       │   ├── dialogue/
│       │   └── character/
│       ├── pages/
│       │   ├── ReaderPage.tsx
│       │   ├── UploadPage.tsx
│       │   ├── StudioPage.tsx
│       │   └── ExportsPage.tsx
│       ├── api/
│       │   ├── client.ts
│       │   ├── manga.ts
│       │   └── types.ts
│       ├── hooks/
│       ├── styles/
│       │   ├── tokens.css
│       │   ├── global.css
│       │   └── components.css
│       └── main.tsx
├── backend/                 # Reuse/rename only after inspecting the repo
│   ├── api/
│   ├── services/
│   ├── models/
│   └── ...
├── tests/
├── README.md
└── ...
```

Do not force this exact structure if the current repository already has
a clear structure. The goal is separation of concerns, not a wholesale
rewrite for its own sake.

------------------------------------------------------------------------

## Product context: features that must survive the migration

The existing application is a multimodal manga-reading engine that
transcribes panel dialogue in reading order and tracks character
identities across sequential pages. The primary workflow includes a
sequence of three manga pages.

Preserve these existing capabilities wherever present in the repository:

-   Manga Reader & Dialogue Inspector
-   Multilingual Comic Studio
-   Upload Any Manga
-   Export Deliverables
-   Test Predictions and Development Library source selection
-   Sequence/chapter selection
-   Chapter/sequence metadata
-   Three-page narrative context
-   Cross-page character identity consistency
-   Right-to-left manga panel reading order
-   Page images and ordered dialogue lines
-   Character Identification Guide / visual cast and panel map
-   Side-by-side page-and-dialogue mode
-   All-pages spread mode
-   Character IDs, speaker labels, and page associations
-   Multilingual options currently supported by the app (the current UI
    advertises English, Japanese, Korean, and Chinese; verify actual
    support in code)
-   Upload validation, processing status, errors, and results
-   Existing export formats and content

**Preserve the source of truth.** Inspect the actual code to establish
what exists. Do not invent features, model capabilities, confidence
scores, characters, or language support.

## Visual direction: premium editorial AI workspace

Create an interface that feels like a premium creative/AI product. Manga
artwork is the hero; the surrounding interface should make analysis easy
and precise.

### Design goals

-   Dark, cinematic workspace with clear typography and restrained
    accent colors.
-   Modern creative-tool feel---not a generic admin dashboard, not a
    clone of Streamlit, and not a landing page that hides the working
    application.
-   High information density without clutter.
-   Strong distinction between artwork, extracted dialogue, character
    metadata, controls, and system status.
-   Responsive desktop-first layout, usable on laptop and tablet widths.
-   Fast transitions and subtle motion only where it improves feedback.
-   No decorative controls that do nothing.

### Initial design tokens

Put tokens in `src/styles/tokens.css`, then use them consistently.

``` css
:root {
  color-scheme: dark;
  --bg: #0a0c12;
  --surface: #111522;
  --surface-raised: #171d2c;
  --surface-hover: #20283a;
  --border: rgba(255, 255, 255, 0.09);
  --text: #f4f6fb;
  --text-muted: #a2acc0;
  --text-subtle: #737f96;
  --accent: #9182ff;
  --accent-strong: #7563f4;
  --cyan: #64cce8;
  --coral: #ff8b7d;
  --success: #66d7a5;
  --warning: #f4c56b;
  --danger: #ff6f7d;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
  --shadow-panel: 0 16px 40px rgba(0, 0, 0, 0.22);
}
```

These are starting values, not a rigid requirement. Tune contrast and
palette after implementation. Use consistent spacing, focus rings,
borders, radii, and text styles. Avoid overusing gradients, glows, blur,
and glassmorphism.

------------------------------------------------------------------------

# UI roadmap

## Phase 0 --- Audit and baseline (do this before coding)

1.  Inspect the entire repository and identify:
    -   Streamlit entry point and every tab/view.
    -   Model loading and inference functions.
    -   Data schemas for pages, dialogue, characters, sequences, and
        chapter metadata.
    -   Source-selection logic for Test Predictions and Development
        Library.
    -   Upload handling and file validation.
    -   Multilingual processing.
    -   Export formats and output schemas.
    -   Existing tests, fixtures, environment variables, and run
        commands.
2.  Run the current application and tests to establish a baseline.
3.  Identify whether a FastAPI service or other backend API already
    exists.
4.  Map each current UI action to the Python function that implements
    it.
5.  Write a short implementation plan listing the files to create/modify
    and any risks.
6.  Do not delete the Streamlit implementation until the new frontend is
    verified. Keep it available during development as a fallback, but do
    not continue polishing it.

**Deliverable:** a verified feature map and implementation plan,
followed by code changes.

## Phase 1 --- Backend API contract

Create or reuse a backend API that exposes the real application
functionality.

Potential endpoint shapes below are illustrative. Adapt them to the
current code and data model; do not create endpoints that cannot be
implemented honestly.

-   `GET /api/health` --- service status.
-   `GET /api/sequences` --- available sequences and summary metadata.
-   `GET /api/sequences/{sequence_id}` --- sequence details, ordered
    pages, dialogue, and character references.
-   `GET /api/sources` --- supported sources such as test predictions
    and development library, if these exist.
-   `POST /api/analyze` --- upload/submit pages for analysis if this is
    how the existing inference workflow operates.
-   `GET /api/jobs/{job_id}` --- analysis status and results for
    asynchronous work, if required.
-   `GET /api/characters/{sequence_id}` --- character/cast information,
    if supported.
-   `GET /api/exports/{sequence_id}` or `POST /api/exports` --- use the
    actual export behavior and supported formats.

API requirements: - Use typed request/response schemas (Pydantic if
FastAPI is used). - Validate uploads and return useful, structured
errors. - Keep the actual sequence and dialogue order unchanged. - Use
real IDs; do not generate fake data to fill empty fields. - Return image
URLs or safe image-serving endpoints that the frontend can use. - Handle
long-running inference without blocking unrelated requests. Use an
appropriate background/job approach only if needed. - Configure CORS
narrowly for local development and production deployment. - Never expose
API keys, local filesystem paths, or secrets to the browser. - Document
endpoint contracts and error shapes. - If an endpoint already exists,
adapt the frontend to it instead of duplicating it.

**Deliverable:** working API contract and a tested frontend-to-backend
connection.

## Phase 2 --- Frontend foundation

1.  Create the React + TypeScript + Vite frontend.
2.  Enable TypeScript strict mode and avoid `any` except where
    explicitly justified.
3.  Create the global design tokens, reset, typography, layout
    primitives, and accessible focus styles.
4.  Build reusable components:
    -   `AppShell`
    -   `TopBar`
    -   `Sidebar` or compact primary navigation
    -   `PageHeader`
    -   `Button`
    -   `IconButton`
    -   `Select`
    -   `SegmentedControl`
    -   `StatusBadge`
    -   `MetricCard`
    -   `EmptyState`
    -   `ErrorState`
    -   `LoadingState`
    -   `Tooltip` only where necessary
5.  Create a typed API client with a configurable backend base URL from
    environment variables.
6.  Implement loading, error, retry, and empty states from the
    beginning.
7.  Use real data as soon as the API is available. Mock fixtures may be
    used only in isolated development/tests and must be visibly
    separated from production behavior.

**Deliverable:** a functioning app shell that can fetch and display real
sequence data.

## Phase 3 --- Reader workspace (the primary screen)

Design this as the product's central workspace.

### Top navigation and header

-   Product mark and "Manga Speaker" title.
-   Subtitle: "Multimodal manga reading & dialogue intelligence".
-   Main navigation for Reader, Studio, Upload, and Exports.
-   Small capability indicators only for capabilities verified in the
    code.
-   Keep the header compact so manga content appears immediately.

### Reader toolbar

-   Source selector: Test Predictions / Development Library, if
    supported.
-   Sequence/chapter selector.
-   View switcher: **Spread** / **Page + Dialogue**.
-   Compact metadata: page count, dialogue-line count, active character
    count.
-   Preserve actual selected values and do not reset selections
    unexpectedly.

### Manga canvas

-   Spread mode: three ordered pages in a balanced grid on wide screens.
-   Page + Dialogue mode: selected page artwork paired with the relevant
    ordered dialogue.
-   Preserve original image proportions. Never stretch or crop dialogue
    balloons or panel edges.
-   Make pages zoomable or viewable at a larger size if this can be
    implemented accessibly and reliably.
-   Give each page a clear page number and sequence position.
-   On narrower screens, stack pages and keep controls usable; avoid
    forced horizontal scrolling.

### Character guide

-   Use a collapsible side panel, drawer, or dialog depending on screen
    width.
-   Show only information that actually exists: character ID/name,
    reference image/crop, linked pages, dialogue count, and
    attribution/consistency status.
-   Keep the same character color/identity mapping across all pages.
-   Mark unknown or unassigned speakers clearly rather than guessing
    identity.

**Deliverable:** reader workspace connected to the real API and usable
in both view modes.

## Phase 4 --- Dialogue inspector

Replace the repetitive cards with a focused, legible dialogue
timeline/list.

Each dialogue item should support: - Reading-order index. -
Character/speaker badge with stable color mapping. - Dialogue text with
natural casing and comfortable line height. - Page association and panel
association if present in the source data. - Confidence/status only if
the backend provides it. - Clear distinction between model predictions
and ground truth if both are available.

Behavior: - Preserve the original dialogue text and punctuation. -
Preserve the model's established reading order; do not sort
alphabetically or by character. - Group entries by page where this
improves navigation, without changing the underlying sequence order. -
Selecting a dialogue item may highlight its linked panel/page only if a
reliable mapping exists. - Provide a compact density option only if it
adds value and does not complicate the default view. - Support long
dialogue without clipping or hiding text. - Make keyboard navigation and
focus visible.

**Deliverable:** dialogue inspector that is easier to scan and audit
without changing prediction semantics.

## Phase 5 --- Upload and multilingual studio

### Upload workspace

-   Drag-and-drop area and standard file picker.
-   Accepted file types and size limits must come from actual backend
    validation.
-   Ordered thumbnail queue with remove/reorder controls only if the
    workflow supports reordering.
-   Clear primary action to analyze/submit pages.
-   Visible states: idle, selected, uploading, processing, complete, and
    failed.
-   Progress information must reflect real upload/inference progress; do
    not invent percentages.
-   Keep errors specific and actionable.
-   Allow retry without losing the user's selected files when possible.

### Multilingual studio

-   Reuse actual language options and processing behavior from the
    current implementation.
-   Make source and target language roles explicit where applicable.
-   Keep translation/transcription outputs clearly distinguished.
-   Do not claim translation support or accuracy that the backend does
    not provide.

**Deliverable:** functional upload and language workflows connected to
real processing.

## Phase 6 --- Export center

-   Show only export formats that the backend actually supports.
-   Explain briefly what each format contains.
-   Make the selected sequence/result clear before exporting.
-   Show a real loading state while an export is generated.
-   Provide a download action using the actual returned file or URL.
-   Display the actual filename if available.
-   Report errors truthfully and allow retry.
-   Preserve existing schemas and output contents.

**Deliverable:** exports work end-to-end from the new frontend.

## Phase 7 --- Polish, responsive design, and accessibility

-   Verify at wide desktop, typical laptop, and tablet widths.
-   Ensure no horizontal overflow, clipped buttons, broken dialogs, or
    unreadable artwork.
-   Use semantic headings, landmarks, buttons, labels, and form
    controls.
-   Meet WCAG-minded contrast and visible keyboard focus expectations.
-   Ensure icon-only buttons have accessible labels.
-   Respect reduced-motion preferences.
-   Use subtle transitions only for state feedback.
-   Optimize image loading and avoid unnecessary re-renders.
-   Add clear not-found, backend-offline, empty-sequence, and
    failed-analysis states.
-   Ensure errors are visible without exposing stack traces or secrets
    to end users.

## Phase 8 --- Testing, cutover, and documentation

1.  Add or update frontend tests for critical components and
    interactions.
2.  Add API tests for sequence retrieval, upload validation, analysis
    result handling, and exports where practical.
3.  Run backend tests, frontend tests, TypeScript checks, and production
    build.
4.  Verify these scenarios manually:
    -   App loads when backend is healthy.
    -   Backend-offline state is useful and recoverable.
    -   Source and sequence selection work.
    -   Three pages appear in the correct order.
    -   Dialogue ordering is unchanged.
    -   Character identity mapping remains consistent across pages.
    -   Both reader modes work.
    -   Upload validation and processing states work.
    -   Language controls reflect actual support.
    -   Exported files contain the expected content.
5.  Run the production build and fix all errors introduced by the
    migration.
6.  Update README with exact commands to install dependencies, configure
    environment variables, run the backend, run the frontend, run tests,
    and build for production.
7.  Keep secrets in environment variables; provide `.env.example` with
    placeholder values only.
8.  After all acceptance checks pass, make the new frontend the primary
    local application. Do not remove the old Streamlit code unless it is
    clearly safe and explicitly approved.

**Deliverable:** working frontend, connected backend, passing checks,
and clear setup instructions.

------------------------------------------------------------------------

# Interaction and visual quality bar

The result should feel like a thoughtfully designed professional
application, not a collection of cards.

-   Artwork gets the most visual attention.
-   Dialogue is readable and structured.
-   Controls are compact and aligned.
-   Metadata is useful but secondary.
-   Use consistent spacing and typography.
-   Keep the interface responsive and calm.
-   Avoid giant empty hero areas, oversized cards, excessive uppercase
    labels, overuse of pill badges, gratuitous animations, and
    decorative gradients.
-   Never render a button that does not work.
-   Never claim that a model operation or export succeeded until the
    backend confirms success.

## Security and reliability

-   Validate all files on the backend, regardless of frontend
    validation.
-   Sanitize and safely render user-supplied filenames and dialogue.
-   Do not inject untrusted content as raw HTML.
-   Do not expose API credentials in frontend code.
-   Restrict CORS to intended origins.
-   Handle failed API calls and timeouts without crashing the entire
    application.
-   Keep inference and data processing independent from frontend
    component state.

# Acceptance checklist

-   [ ] The primary UI is React + TypeScript, not Streamlit.
-   [ ] Frontend starts with the documented Vite command.
-   [ ] Python model and data-processing code are preserved.
-   [ ] Frontend uses a real API; no fake production predictions.
-   [ ] Existing source and sequence selection remain available.
-   [ ] Three-page sequence display preserves the correct page order.
-   [ ] Dialogue remains in the correct reading order.
-   [ ] Character identities remain consistent across sequential pages.
-   [ ] Both spread and page-plus-dialogue modes work.
-   [ ] Character guide uses real data and is easy to inspect.
-   [ ] Upload, processing, and error states work.
-   [ ] Multilingual controls reflect actual backend capabilities.
-   [ ] Existing export formats and output schemas are preserved.
-   [ ] Responsive layout works on desktop and laptop/tablet sizes.
-   [ ] TypeScript check, tests, and production build have been run.
-   [ ] README includes exact setup and run commands.
-   [ ] Remaining limitations are explicitly documented.

# Final instruction to Anti-Gravity

**Build the migration, not just a plan or a screenshot.** Start by
auditing the current repository and mapping every existing feature to
its underlying Python function/data structure. Then implement the
React + TypeScript frontend and the smallest necessary API layer while
preserving the current model and inference code.

Do not ask the user to manually fill in placeholder project names or
filenames. Use the repository as the source of truth. Do not stop after
generating static components. Connect the UI to the actual backend,
verify the important flows, run tests/build checks, and report:

1.  Architecture selected and why.
2.  Files created/modified.
3.  How to run frontend and backend locally.
4.  Tests and build checks run, with results.
5.  Any feature that could not be preserved and why.

The goal is a substantial, functional, visually excellent replacement
for the Streamlit UI---not a cosmetic patch.
