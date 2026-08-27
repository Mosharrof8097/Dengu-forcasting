# 🦟 DENGUE-NET DASHBOARD | UI/UX DESIGN GUIDELINE
**Version 1.0** | Public Health Emergency Response System | Bangladesh DGHS

---

## 📋 ডকুমেন্ট সূচী | Table of Contents

1. **Design Philosophy & Vision**
2. **Color Palette & Risk-Level Mapping**
3. **Typography System**
4. **Layout Grid & Spacing**
5. **Component Design Specifications**
6. **Dark/Light Mode Strategy**
7. **Glassmorphism & Visual Effects**
8. **Interaction Patterns & Micro-interactions**
9. **Accessibility & Usability Standards**
10. **Mobile Responsive Breakpoints**

---

## 1️⃣ DESIGN PHILOSOPHY & VISION

### Core Principles
- **Trust & Authority**: Government health agency (DGHS) credibility
- **Urgency & Clarity**: Life-critical data must be instantly scannable
- **Data-Driven Aesthetics**: Every visual element communicates information
- **Accessibility First**: Color-blind safe, WCAG 2.1 AA compliant
- **Minimal Cognitive Load**: Users under pressure need fast decision-making

### Target Users
1. **Primary**: DGHS Health Officials, District Health Officers
2. **Secondary**: Hospital Administrators, NGO Response Teams
3. **Tertiary**: Policy Makers, General Public (Info Portal)

### Design Tone
- **Professional yet approachable**
- **Modern but authoritative**
- **Data-heavy but not cluttered**
- **Bengali + English bilingual support**

---

## 2️⃣ COLOR PALETTE & RISK-LEVEL MAPPING

### Primary Risk Indicator Colors (Backend-aligned)

| Risk Level | Hex Code | RGB | Usage | Meaning |
|---|---|---|---|---|
| **HIGH_SURGE** 🔴 | `#EF4444` | RGB(239, 68, 68) | Alert Badge, Heatmap (Hot), Critical Stats | Immediate Action Required |
| **MODERATE_WARNING** 🟡 | `#F59E0B` | RGB(245, 158, 11) | Caution Badge, Heatmap (Warm), Watch Stats | Monitor Closely |
| **LOW_NORMAL** 🟢 | `#10B981` | RGB(16, 185, 129) | Safe Badge, Heatmap (Cool), Stable Stats | Under Control |

### Secondary Color Palette

| Element | Hex Code | Purpose |
|---|---|---|
| **Neutral Dark** | `#1F2937` | Text, Dark mode background |
| **Neutral Light** | `#F9FAFB` | Light mode background, Cards |
| **Border Subtle** | `#E5E7EB` | Dividers, Card borders (light mode) |
| **Border Dark** | `#374151` | Dividers, Card borders (dark mode) |
| **Accent Blue** | `#3B82F6` | Secondary actions, Hover states, Focus rings |
| **Info Cyan** | `#06B6D4` | Informational alerts, Secondary stats |
| **Success Green** | `#059669` | Confirmation, Success feedback |
| **Error Red** | `#DC2626` | Destructive actions, Error messages |
| **Warning Amber** | `#D97706` | Warnings, Non-critical alerts |

### Gradient System (for Glassmorphic Elements)

```
Primary Risk Gradient:
  Start: #EF4444 (High Risk)
  End: #FCA5A5 (Faded Red)
  Angle: 135° (top-left to bottom-right)

Success Gradient:
  Start: #10B981 (Low Risk)
  End: #6EE7B7 (Faded Green)
  Angle: 135°

Neutral Gradient:
  Start: #374151 (Dark)
  End: #111827 (Very Dark)
  Angle: 180° (top to bottom)
```

### Heatmap Color Scale (for Geospatial Map)

**Low → High Risk Progression:**
```
Low:      #10B981 (Green)
→         #84CC16 (Lime)
→         #EAB308 (Yellow)
→         #F59E0B (Orange)
→ High:   #EF4444 (Red)
```

---

## 3️⃣ TYPOGRAPHY SYSTEM

### Font Families

**Primary Font (Headlines & UI):**
- **Font Name**: Inter or System-UI (Fallback: Segoe UI, Helvetica Neue)
- **Weight Variants**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Use Case**: Headlines, Button text, Navigation

**Secondary Font (Body Text):**
- **Font Name**: Inter or Source Sans Pro
- **Weight Variants**: 400 (Regular), 500 (Medium)
- **Use Case**: Body copy, Descriptions, Forms

**Monospace Font (Data Display):**
- **Font Name**: JetBrains Mono or Monaco (for numbers/codes)
- **Use Case**: Statistics, Model latency, Data tables

### Typography Scale

| Element | Size | Weight | Line Height | Letter Spacing | Margin Bottom |
|---|---|---|---|---|---|
| **H1 (Page Title)** | 36px | 700 | 1.4 | -0.02em | 24px |
| **H2 (Section Title)** | 28px | 600 | 1.4 | -0.01em | 20px |
| **H3 (Subsection)** | 22px | 600 | 1.4 | 0 | 16px |
| **H4 (Card Title)** | 18px | 600 | 1.4 | 0 | 12px |
| **Body Large** | 16px | 400 | 1.6 | 0 | - |
| **Body Regular** | 14px | 400 | 1.6 | 0 | - |
| **Body Small** | 12px | 400 | 1.5 | 0 | - |
| **Caption** | 11px | 500 | 1.4 | 0.05em | - |
| **Button Text** | 14px | 600 | 1.4 | 0.02em | - |
| **Label** | 13px | 500 | 1.4 | 0.02em | - |

### Font Color Usage

**Light Mode:**
- Primary Text: `#111827` (Neutral-900)
- Secondary Text: `#6B7280` (Neutral-500)
- Tertiary Text: `#9CA3AF` (Neutral-400)
- Disabled Text: `#D1D5DB` (Neutral-300)

**Dark Mode:**
- Primary Text: `#F9FAFB` (Neutral-50)
- Secondary Text: `#D1D5DB` (Neutral-300)
- Tertiary Text: `#9CA3AF` (Neutral-400)
- Disabled Text: `#6B7280` (Neutral-500)

---

## 4️⃣ LAYOUT GRID & SPACING

### Grid System

**Desktop (1920px and above):**
- 12-column grid
- Column width: 140px
- Gutter (gap): 24px
- Outer margin (left/right): 32px

**Laptop (1440px - 1919px):**
- 12-column grid
- Column width: 100px
- Gutter: 20px
- Outer margin: 28px

**Tablet (768px - 1439px):**
- 8-column grid
- Column width: 80px
- Gutter: 16px
- Outer margin: 20px

**Mobile (320px - 767px):**
- 4-column grid (or full-width stacking)
- Column width: ~50px
- Gutter: 12px
- Outer margin: 16px

### Spacing Scale (8px base unit)

```
8px   (1 unit)   - Micro spacing
12px  (1.5 unit) - Component internal
16px  (2 unit)   - Component external / Section padding
24px  (3 unit)   - Section spacing
32px  (4 unit)   - Large section spacing
40px  (5 unit)   - Page-level spacing
48px  (6 unit)   - Major section breaks
```

### Common Spacing Patterns

| Pattern | Spacing | Example |
|---|---|---|
| **Card Padding (Interior)** | 20px | Content inside cards |
| **Section Padding (Vertical)** | 32px | Space between major sections |
| **Component Gap (Horizontal)** | 16px | Space between buttons/cards in a row |
| **Form Field Spacing** | 12px | Gap between label and input |
| **List Item Spacing** | 8px | Vertical gap in lists |

---

## 5️⃣ COMPONENT DESIGN SPECIFICATIONS

### 5.1 TOP LIVE STATS BAR
**Purpose**: Real-time forecast metrics at a glance

**Layout:**
- Sticky header, positioned at top of page
- Height: 80-100px (desktop), 60px (mobile)
- Background: Semi-transparent glassmorphic card with backdrop blur
- Divider: 1px border bottom with subtle gradient

**Content Grid:**
- 3-4 stat cards arranged horizontally
- Each stat card = 220px wide (desktop), 100% stacked (mobile)

**Individual Stat Card Structure:**
```
┌─────────────────────────┐
│ Label (12px, Secondary) │
│ 61.93 cases/day ↗ 5%    │ (24px, Bold primary)
│ (Inference: 0.02ms)     │ (10px, Tertiary)
└─────────────────────────┘
```

**Design Details:**
- Background: `rgba(255, 255, 255, 0.9)` (light mode) / `rgba(31, 41, 55, 0.8)` (dark)
- Backdrop blur: 8px
- Border: 1px solid `#E5E7EB` (light) / `#374151` (dark)
- Border radius: 12px
- Box shadow: `0 4px 12px rgba(0, 0, 0, 0.1)`
- Padding: 16px 20px
- Hover effect: Slight lift (shadow increase), scale 1.02

**Stat Indicators:**
- Green ✓ for improving trends
- Red ↗ for worsening trends
- Orange → for stable trends
- Animation: Fade in from bottom on page load (300ms)

---

### 5.2 GEOSPATIAL OUTBREAK HEATMAP
**Purpose**: Visual risk levels across 11 districts

**Container:**
- Full width (minus margins)
- Aspect ratio: 16:9 (desktop), 3:2 (mobile)
- Background: Light gray for light mode, dark gray for dark mode
- Border radius: 12px
- Box shadow: `0 10px 30px rgba(0, 0, 0, 0.15)`

**Map Features:**
- **Districts** rendered as separate regions (polygon or rectangle tiles)
- **Color coding**: Heatmap gradient (green → yellow → orange → red)
- **Interactive elements**:
  - Hover: Region darkens slightly, tooltip appears (100ms delay)
  - Click: District details modal opens with resource allocation data
  - Highlight effect: 2px glowing border in risk color

**Tooltip Design (on hover):**
```
┌────────────────────────┐
│ District: Dhaka        │
│ Risk Level: HIGH_SURGE │
│ Cases/Day: 143.5 ↗     │
│ Status: 🔴 URGENT      │
└────────────────────────┘
```
- Tooltip styling: Glassmorphic, white text on dark semi-transparent background
- Arrow pointer: 8px triangle pointing to district
- Animation: Fade in (150ms)

**District Modal (on click):**
- Overlay: `rgba(0, 0, 0, 0.7)` (transparent dark background)
- Modal size: 500px wide, centered
- Elevation: 24px shadow
- Border radius: 16px
- Close button: Top-right corner (X icon, 32px)

---

### 5.3 PRESCRIPTIVE RESOURCE ACTION CARDS
**Purpose**: Hospital resource requirements per district

**Card Grid Layout:**
- Desktop: 3-column grid (4 cards visible, horizontal scroll)
- Tablet: 2-column grid
- Mobile: Single column, stacked

**Individual Card Dimensions:**
- Width: 300px (fixed) or 100% (responsive)
- Height: auto (content-driven)
- Padding: 24px
- Margin: 16px between cards

**Card Structure:**

```
╔═══════════════════════════════════╗
║ District Badge [Dhaka]            ║ (Colored badge)
║ ────────────────────────────────  ║
║ 🏥 Hospital Beds: +152            ║ (Icon + Label + Value)
║ 🧪 Test Kits: +781                ║
║ 💧 IV Saline Bags: +1084           ║
║ ────────────────────────────────  ║
║ Status: 🚨 URGENT DISPATCH        ║ (Badge with animation)
║ ────────────────────────────────  ║
║ [VIEW DETAILS] [ALLOCATE NOW]     ║ (Action buttons)
╚═══════════════════════════════════╝
```

**Card Design Details:**
- Background: Glassmorphic gradient (light to slightly darker)
- Border: 1px solid, matches risk color (`#EF4444` for HIGH_SURGE)
- Border radius: 12px
- Shadow: `0 8px 24px rgba(0, 0, 0, 0.12)`
- Hover state: 
  - Transform: `translateY(-4px)` (lift effect)
  - Shadow increase: `0 12px 32px rgba(0, 0, 0, 0.2)`
  - Border glow: Subtle glow filter

**Badge Styling:**
- Dispatch badge: Pill-shaped, 8px padding
  - `URGENT` 🚨: Red background, white text, pulsing animation (0.5s)
  - `STANDARD` 📦: Blue background, white text, no animation
- District badge: Small pill, top-left, colored by region

**Icons:**
- Size: 20px × 20px
- Color: Match risk level or primary color
- Font: Font Awesome or Material Icons (consistent library)

---

### 5.4 "WHAT-IF" WEATHER SIMULATOR (SLIDERS)
**Purpose**: Interactive prediction adjustment based on weather parameters

**Container:**
- Panel width: 100% or sidebar (300px on desktop)
- Background: Subtle glassmorphic card
- Padding: 24px
- Border radius: 12px

**Slider Section Structure:**

```
┌─────────────────────────────────┐
│ Weather Simulator               │
├─────────────────────────────────┤
│ 🌧️ Rainfall (mm)               │
│ Current: 85mm  Input: [75]      │
│ ├─────●────────────────┤        │ (Slider track)
│ 0mm               200mm          │
│ [Real-time output]              │
│                                  │
│ Predicted cases: 76.4/day ↗ 2%  │ (Updates in real-time)
├─────────────────────────────────┤
│ 🌡️ Temperature (°C)             │
│ Current: 28°C  Input: [32]       │
│ ├───────────●─────────┤          │
│ 15°C              40°C             │
│ [Real-time output]              │
│                                  │
│ Predicted cases: 89.2/day ↗ 5%  │
├─────────────────────────────────┤
│ 💨 Humidity (%)                  │
│ Current: 72%  Input: [80]        │
│ ├──────────●──────────┤          │
│ 30%               95%             │
│ [Real-time output]              │
│                                  │
│ Predicted cases: 92.7/day ↗ 7%  │
├─────────────────────────────────┤
│ [RESET] [SAVE SCENARIO]         │
└─────────────────────────────────┘
```

**Slider Design Details:**
- Track width: 100% of container
- Track height: 6px
- Track color: `#E5E7EB` (light) / `#4B5563` (dark)
- Thumb (handle):
  - Size: 16px × 16px (circle)
  - Color: `#3B82F6` (blue)
  - Hover: `#2563EB` (darker blue)
  - Shadow: `0 2px 8px rgba(59, 130, 246, 0.4)`
  - Cursor: `pointer` with hand icon
- Range highlight: Blue gradient from 0 to current value

**Input Field (Number):**
- Width: 60px
- Height: 36px
- Border radius: 6px
- Border: 1px solid `#D1D5DB` (light) / `#4B5563` (dark)
- Padding: 8px 12px
- Font size: 14px
- Alignment: Right-aligned

**Output Display (Prediction):**
- Font size: 16px, bold
- Color: Risk color based on output (red/orange/green)
- Metric label: "Predicted cases: X/day"
- Trend indicator: Arrow (↗/↘/→) with % change
- Update animation: Fade in (200ms) on value change

**Buttons:**
- `[RESET]`: Neutral secondary button, 12px padding
- `[SAVE SCENARIO]`: Primary blue button, icon + text
- Button spacing: 12px gap
- Hover: Slight brightness increase, shadow enhancement
- Click: Haptic-like feedback (subtle scale 0.98 → 1.0)

---

### 5.5 1-CLICK PDF REPORT EXPORTER
**Purpose**: Generate official executive summary for DGHS/Health Officers

**Button Placement:**
- Top-right corner of dashboard
- Size: 40-48px (icon button) or 120px (text + icon button)
- Fixed position (sticky on scroll)

**Button Design:**
```
[📄 Export Report] or [🔴 PDF]
```
- Background: Primary blue gradient or glassmorphic
- Icon: PDF icon (🔴 or document icon)
- Text: "Export Report" or "Download PDF"
- Hover: Slight enlarge, shadow boost, tooltip: "Generate official DGHS report"
- Loading state: Spinner animation inside button (animated dots)

**Export Dialog (Pre-export options):**

```
┌──────────────────────────────────┐
│ Export Report Configuration      │
├──────────────────────────────────┤
│                                  │
│ Report Type:                     │
│ ○ Executive Summary (2 pages)    │
│ ◉ Full Technical Report (5-7 p)  │
│ ○ Resource Allocation Only (1 p) │
│                                  │
│ Date Range:                      │
│ From: [Today] To: [Today]        │
│                                  │
│ Include Sections:                │
│ ☑ Forecast Data                  │
│ ☑ Risk Assessment                │
│ ☑ Resource Requirements          │
│ ☑ Recommendations                │
│ ☑ District-wise Breakdown        │
│                                  │
│ Recipient Organization:          │
│ [Select DGHS / District / NGO]   │
│                                  │
│ [CANCEL]  [GENERATE PDF]         │
└──────────────────────────────────┘
```

**PDF Output Specifications:**
- **Format**: A4 (210 × 297mm)
- **Margins**: 20mm all sides
- **Header**: Government of Bangladesh seal + "Ministry of Health & Family Welfare" + DGHS logo
- **Colors**: Same risk-level colors, print-optimized
- **Fonts**: Arial/Calibri (web-safe for PDFs)
- **Content sections**:
  1. Title page (Report date, generated timestamp)
  2. Executive Summary (1 page)
  3. Forecast Data Table (Risk levels, daily/weekly projections)
  4. Resource Allocation Table (Hospital beds, test kits, IV fluids)
  5. District-wise Breakdown (Heatmap color reference + data)
  6. Recommendations (Bulleted action items)
  7. Metadata (Model version, inference latency, data source)

**Filename Convention:**
```
DGHS_DengueNet_Report_YYYY-MM-DD_REGION.pdf
(e.g., DGHS_DengueNet_Report_2025-01-15_Dhaka.pdf)
```

---

## 6️⃣ DARK/LIGHT MODE STRATEGY

### Light Mode (Default)

**Background Colors:**
- Primary BG: `#FFFFFF` (Pure white)
- Secondary BG: `#F9FAFB` (Neutral-50)
- Card BG: `#FFFFFF` with 1px border `#E5E7EB`
- Hover BG: `#F3F4F6` (Neutral-100)

**Text Colors:**
- Primary: `#111827` (Neutral-900)
- Secondary: `#6B7280` (Neutral-500)
- Tertiary: `#9CA3AF` (Neutral-400)

**Border Colors:**
- Standard: `#E5E7EB` (Neutral-200)
- Focus: `#3B82F6` (Blue)
- Success: `#10B981` (Green)
- Error: `#EF4444` (Red)

**Shadow:**
- Subtle: `0 1px 3px rgba(0, 0, 0, 0.12)`
- Medium: `0 4px 12px rgba(0, 0, 0, 0.15)`
- Large: `0 10px 30px rgba(0, 0, 0, 0.2)`

---

### Dark Mode (High Contrast, Eye-Friendly)

**Background Colors:**
- Primary BG: `#111827` (Neutral-900)
- Secondary BG: `#1F2937` (Neutral-800)
- Card BG: `#1F2937` with 1px border `#374151`
- Hover BG: `#374151` (Neutral-700)

**Text Colors:**
- Primary: `#F9FAFB` (Neutral-50)
- Secondary: `#D1D5DB` (Neutral-300)
- Tertiary: `#9CA3AF` (Neutral-400)

**Border Colors:**
- Standard: `#374151` (Neutral-700)
- Focus: `#60A5FA` (Blue-400, brighter)
- Success: `#6EE7B7` (Green-300, brighter)
- Error: `#FCA5A5` (Red-300, brighter)

**Shadow:**
- Subtle: `0 1px 3px rgba(0, 0, 0, 0.5)`
- Medium: `0 4px 12px rgba(0, 0, 0, 0.7)`
- Large: `0 10px 30px rgba(0, 0, 0, 0.8)`

### Mode Toggle

**Location**: Top-right corner, next to profile icon
**Design**: 
- Toggle switch (Animated)
- Icons: ☀️ (Light) and 🌙 (Dark)
- Smooth transition: All color changes fade in (300ms)
- Persistence: Store user preference in localStorage

---

## 7️⃣ GLASSMORPHISM & VISUAL EFFECTS

### Glassmorphic Card Template

```css
Background: rgba(255, 255, 255, 0.7) [Light]
            rgba(255, 255, 255, 0.1) [Dark mode overlay]
Backdrop Blur: 8px - 12px
Border: 1px solid rgba(255, 255, 255, 0.2) [Light]
        1px solid rgba(255, 255, 255, 0.15) [Dark]
Border Radius: 12px - 16px
Box Shadow: 0 8px 32px rgba(0, 0, 0, 0.1)
```

### Blur & Frosted Glass Effect

- **Light Mode Cards**: Light transparency with subtle white border
- **Dark Mode Cards**: Darker transparency, slightly brighter border
- **Backdrop Blur**: Consistent 10px (CSS: `backdrop-filter: blur(10px)`)

### Glow & Shadow Hierarchy

| Element Importance | Shadow Strength | Use Case |
|---|---|---|
| **Subtle** | 0 2px 4px rgba(0,0,0,0.06) | Form inputs, small components |
| **Medium** | 0 4px 12px rgba(0,0,0,0.12) | Cards, buttons |
| **Strong** | 0 10px 30px rgba(0,0,0,0.20) | Modals, dropdowns |
| **Critical** | 0 20px 50px rgba(0,0,0,0.30) | High-priority alerts |

### Gradient Overlays (for Data Visualization)

**Heatmap Gradient:**
```
Direction: Left to Right (for maps)
Colors: #10B981 → #84CC16 → #EAB308 → #F59E0B → #EF4444
Opacity: 0.9 for visibility
```

**Risk Indicator Gradient:**
```
Direction: Top to Bottom
Color Pair 1: #EF4444 → #FCA5A5 (High → Light Red)
Color Pair 2: #F59E0B → #FBBF24 (Moderate → Light Orange)
Color Pair 3: #10B981 → #6EE7B7 (Low → Light Green)
```

---

## 8️⃣ INTERACTION PATTERNS & MICRO-INTERACTIONS

### Button States

**Primary Button (e.g., [ALLOCATE NOW])**
```
Default:
  Background: #3B82F6 (Blue)
  Text: White
  Border radius: 8px
  Padding: 12px 24px
  Font weight: 600
  
Hover:
  Background: #2563EB (Darker blue)
  Shadow: 0 4px 12px rgba(59, 130, 246, 0.4)
  Transform: translateY(-2px)
  
Active/Pressed:
  Background: #1D4ED8 (Even darker)
  Transform: translateY(0)
  
Disabled:
  Background: #D1D5DB (Gray)
  Color: #9CA3AF (Lighter gray text)
  Cursor: not-allowed
  Opacity: 0.6
```

**Secondary Button (e.g., [CANCEL])**
```
Default:
  Background: Transparent
  Border: 2px solid #D1D5DB
  Text: #111827 (Light mode) or #F9FAFB (Dark mode)
  
Hover:
  Background: #F3F4F6 (Light) or #374151 (Dark)
  Border color: #9CA3AF
  
Active:
  Background: #E5E7EB (Light) or #4B5563 (Dark)
```

### Input Field Focus

```
Default:
  Border: 1px solid #D1D5DB
  Background: White (Light) / #1F2937 (Dark)
  
Focus:
  Border: 2px solid #3B82F6
  Background: White (Light) / #1F2937 (Dark)
  Box shadow: 0 0 0 3px rgba(59, 130, 246, 0.1)
  Outline: None
  
Error:
  Border: 2px solid #EF4444
  Box shadow: 0 0 0 3px rgba(239, 68, 68, 0.1)
```

### Loading States

**Spinner Animation:**
- Style: Rotating circle outline
- Color: Risk-level color (red/orange/green)
- Duration: 0.8s per rotation
- Easing: linear (infinite)
- Size: 20px (inline), 40px (modal center)

**Skeleton Loaders:**
- Placeholder shimmer effect (left to right)
- Color: Gray pulse (`#E5E7EB` → `#F3F4F6` → `#E5E7EB`)
- Animation duration: 1.5s
- Used for: Data tables, card content while loading

### Hover & Focus Effects

**Card Hover:**
- Lift: `transform: translateY(-4px)`
- Shadow increase: `box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2)`
- Duration: 200ms
- Timing: ease-out

**Link Hover:**
- Underline appears/highlights
- Color shifts (primary → accent)
- Duration: 150ms

**Icon Hover:**
- Scale: 1.1x
- Color: Brighten by 20%
- Duration: 150ms

### Transition Durations (Standard)

```
UI Element Changes:     150ms (fast)
Color/Background:       200ms (moderate)
Position/Transform:     300ms (smooth)
Modal Open/Close:       400ms (deliberate)
Page Navigation:        300-500ms
```

---

## 9️⃣ ACCESSIBILITY & USABILITY STANDARDS

### Color Contrast Requirements (WCAG 2.1 AA)

| Element Pair | Minimum Ratio | Status |
|---|---|---|
| Text on Background | 4.5:1 | ✓ Compliant |
| Large Text (18px+) on Background | 3:1 | ✓ Compliant |
| UI Component Borders | 3:1 | ✓ Compliant |
| Focus Indicators | 3:1 | ✓ Must check |

### Focus Management

- **Focus indicator**: 2px solid blue border + 3px glow
- **Tab order**: Logical flow (top-to-bottom, left-to-right)
- **Skip links**: "Skip to main content" link (hidden, appears on tab)
- **Focus trap**: Modals trap focus until closed

### Keyboard Navigation

```
Tab / Shift+Tab:        Move between focusable elements
Enter / Space:          Activate buttons
Arrow Keys:             Navigate sliders, dropdowns
Escape:                 Close modals, tooltips
```

### Screen Reader Support

- **Semantic HTML**: Use `<button>`, `<nav>`, `<main>`, `<section>`
- **ARIA labels**: All icon buttons need `aria-label`
- **Live regions**: Risk updates announced with `aria-live="polite"`
- **Form labels**: Associated with inputs via `for` attribute
- **Alt text**: All images include descriptive alt text

### Color-Blind Safe Palette

✓ Red + Green is supported via additional indicators:
  - Icons (✓, ✗, ⚠️, ℹ️)
  - Text labels ("URGENT", "SAFE", "MONITOR")
  - Hatch patterns or different shades of gray (backup)

### Dyslexia-Friendly Font Spacing

- Line height: 1.5-1.6
- Letter spacing: 0.02em (body text)
- Word spacing: Normal (0.15em)
- Font: Sans-serif (Inter preferred)
- Avoid: All caps, justified alignment

---

## 🔟 MOBILE RESPONSIVE BREAKPOINTS

### Breakpoint Strategy

| Device | Width | Grid | Sidebar | Layout |
|---|---|---|---|---|
| **Mobile** | 320px - 767px | 4-col | Hidden (Drawer) | Single column |
| **Tablet** | 768px - 1023px | 8-col | Side panel (80%) | 2-3 columns |
| **Laptop** | 1024px - 1439px | 12-col | Always visible | 3-4 columns |
| **Desktop** | 1440px+ | 12-col | Always visible | 4+ columns |

### Mobile-Specific Changes

**Top Stats Bar:**
- Stack vertically on mobile (scrollable horizontally, wrapped in tab bar)
- Font sizes reduce by 2-4px
- Remove latency display (show only on desktop)
- Height: 60px instead of 100px

**Heatmap:**
- Simplified district representation (circles instead of complex shapes)
- Touchable region size: Minimum 44px × 44px
- Tap for tooltip (no hover)
- Swipe to explore adjacent regions

**Resource Cards:**
- Full width with padding (16px margins)
- Stack vertically
- Hide secondary details on mobile (show in details view)

**Weather Sliders:**
- Convert to drawer/modal on mobile (not sidebar)
- Larger touch targets: 44px minimum height
- Number input: Spinner buttons larger (36px)

**Buttons:**
- Minimum size: 44px × 44px (tap target)
- Spacing between buttons: 12px
- Primary action buttons: Full width on mobile

**Font Sizes (Mobile adjustments):**
- H1: 28px (down from 36px)
- H2: 22px (down from 28px)
- Body: 14px (same)
- Caption: 11px (same)

### Touch Optimizations

- Hover states → Active/pressed states (more prominent)
- Tooltips → Tap-triggered modals
- Dropdowns → Full-screen pickers
- Double-tap → Pinch-zoom alternative
- Long-press → Context menu

---

## 📋 IMPLEMENTATION CHECKLIST

### Design System Assets to Prepare

- [ ] Color palette (Figma / CSS variables)
- [ ] Typography scale (Font files + CSS)
- [ ] Icon library (SVG set, 20px + 24px sizes)
- [ ] Component library (buttons, cards, modals, sliders)
- [ ] Gradients & glassmorphism templates
- [ ] Animation/transition definitions
- [ ] Spacing & grid templates

### Component Order (Priority)

1. **Tier 1 (Critical)**: Buttons, Forms, Cards, Text styles
2. **Tier 2 (High)**: Stats bar, Heatmap, Resource cards
3. **Tier 3 (Medium)**: Sliders, Modals, Tooltips
4. **Tier 4 (Lower)**: Loading states, Animations, Polish

### Responsive Testing Checklist

- [ ] Mobile (iPhone SE 375px, iPhone 12 390px, iPhone 14 Pro 393px)
- [ ] Tablet (iPad 768px, iPad Air 820px)
- [ ] Laptop (1366px, 1440px)
- [ ] Desktop (1920px+)
- [ ] Orientation changes (Portrait ↔ Landscape)
- [ ] Touch device testing (stylus, multitouch)
- [ ] Keyboard navigation (all pages)
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver)

### Accessibility Audit Checklist

- [ ] Color contrast verified (WCAG AA 4.5:1)
- [ ] Focus indicators visible
- [ ] Tab order logical
- [ ] ARIA labels complete
- [ ] Form labels associated
- [ ] Alt text for images
- [ ] Keyboard-only navigation possible
- [ ] Screen reader announcements clear
- [ ] No auto-playing media/animations
- [ ] Resizable text (100-200% zoom)

---

## 🎨 DESIGN TOKENS (CSS VARIABLES REFERENCE)

```css
/* Colors */
--color-risk-high: #EF4444;
--color-risk-moderate: #F59E0B;
--color-risk-low: #10B981;
--color-accent-blue: #3B82F6;
--color-text-primary: #111827;
--color-bg-primary: #FFFFFF;

/* Spacing */
--spacing-xs: 8px;
--spacing-sm: 12px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;

/* Typography */
--font-family-sans: 'Inter', system-ui, sans-serif;
--font-family-mono: 'JetBrains Mono', monospace;
--font-size-h1: 36px;
--font-size-body: 14px;
--line-height-tight: 1.4;
--line-height-normal: 1.6;

/* Border Radius */
--radius-sm: 6px;
--radius-md: 12px;
--radius-lg: 16px;

/* Shadows */
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
--shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.20);

/* Transitions */
--transition-fast: 150ms ease-out;
--transition-moderate: 200ms ease-out;
--transition-smooth: 300ms ease-out;
```

---

## 📞 DESIGN HANDOFF NOTES

### For Developers

1. **No hardcoded colors** – Use CSS variables/tokens
2. **Consistent font sizes** – Follow typography scale exactly
3. **Spacing multiples of 4px or 8px** – Maintain visual rhythm
4. **Focus states mandatory** – Every interactive element
5. **Dark mode variables ready** – Auto-switch on preference change
6. **SVG icons preferred** – Over images for scalability
7. **Test hover/active states** – Especially on touch devices
8. **Glassmorphism careful** – Ensure text readable over any background
9. **PDF export quality** – Use print CSS media queries
10. **Mobile-first CSS** – Scale up from mobile to desktop

### For QA/Testing

1. Verify color contrast in light AND dark modes
2. Test all button/input states (default, hover, active, disabled)
3. Keyboard navigation without mouse
4. Screen reader experience (NVDA + JAWS)
5. PDF export generates correctly
6. Responsive breakpoints snap correctly
7. Animations/transitions smooth on slow devices
8. No flickering on mode toggle
9. Touch targets large enough (44px+)
10. Performance: Heatmap renders <2s, predictions <500ms

---

## 📄 VERSION HISTORY

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025-01-26 | Initial guideline document (all 5 components) |

---

**Document Owner**: Dengue-Net UI/UX Design System  
**Last Updated**: 2025-01-26  
**Confidentiality**: Public (Government Health Initiative)

---

*This guideline is a living document. Updates will reflect evolving design needs and user feedback from health officials and NGO partners.*
