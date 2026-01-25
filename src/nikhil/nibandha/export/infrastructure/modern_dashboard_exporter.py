"""
Modern sidebar-based HTML dashboard exporter.
Replaces tab-based layout with sidebar + card-based metrics dashboard.
"""
from pathlib import Path
from typing import List, Dict
import markdown2
import logging

logger = logging.getLogger("nibandha.export.dashboard")


class ModernDashboardExporter:
    """Exports markdown to modern sidebar-based dashboard HTML."""
    
    def export(
        self,
        markdown_sections: List[Dict[str, str]],
        output_path: Path,
        project_info: Dict[str, str] = None
    ) -> Path:
        """
        Export markdown sections to modern dashboard HTML.
        
        Args:
            markdown_sections: List of {"title": "...", "content": "...", "metrics_cards": [...]}
            output_path: Where to save HTML
            project_info: Dict with 'name', 'grade', 'status' etc.
            
        Returns:
            Path to generated HTML file
        """
        logger.info(f"Exporting modern dashboard with {len(markdown_sections)} sections")
        
        if not project_info:
            project_info = {
                "name": "Quality Report",
                "grade": "N/A",
                "status": "Complete"
            }
        
        # Convert markdown sections to HTML
        html_sections = []
        for section in markdown_sections:
            html_content = markdown2.markdown(
                section["content"],
                extras=[
                    "tables",
                    "fenced-code-blocks",
                    "header-ids",
                    "break-on-newline",
                    "metadata"
                ]
            )
            html_sections.append({
                "title": section["title"],
                "id": section["title"].lower().replace(" ", "-"),
                "content": html_content,
                "metrics_cards": section.get("metrics_cards", [])
            })
        
        # Build complete HTML document
        html = self._build_html_document(html_sections, project_info)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        
        logger.info(f"Modern dashboard saved to: {output_path}")
        return output_path
    
    def _build_html_document(
        self, 
        sections: List[Dict], 
        project_info: Dict
    ) -> str:
        """Build complete HTML document with sidebar and cards."""
        
        # Build sidebar navigation
        nav_html = '<nav class="sidebar-nav">'
        for section in sections:
            icon = self._get_section_icon(section["title"])
            nav_html += f'''
            <a href="#{section["id"]}" class="nav-link" data-section="{section["id"]}">
                <span class="nav-icon">{icon}</span>
                <span class="nav-text">{section["title"]}</span>
            </a>
            '''
        nav_html += '</nav>'
        
        # Build content sections
        content_html = ''
        for i, section in enumerate(sections):
            # Add metric cards if available
            cards_html = ''
            if section.get("metrics_cards"):
                cards_html = '<div class="metrics-grid">'
                for card in section["metrics_cards"]:
                    cards_html += f'''
                    <div class="metric-card card-{card.get("color", "blue")}">
                        <div class="card-icon">{card.get("icon", "📊")}</div>
                        <div class="card-content">
                            <div class="card-title">{card.get("title", "")}</div>
                            <div class="card-value">{card.get("value", "")}</div>
                        </div>
                    </div>
                    '''
                cards_html += '</div>'
            
            content_html += f'''
            <section id="{section["id"]}" class="content-section">
                {cards_html}
                <div class="section-content">
                    {section["content"]}
                </div>
            </section>
            '''
        
        # Complete document
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_info.get('name', 'Quality Dashboard')}</title>
    <style>
{self._get_css()}
    </style>
</head>
<body data-theme="light">
    <div class="dashboard-layout">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h1 class="logo">Nibandha</h1>
                <div class="grade-badge grade-{project_info.get('grade', 'F').lower()}">
                    {project_info.get('grade', 'N/A')}
                </div>
            </div>
            {nav_html}
            <div class="sidebar-footer">
                <button class="theme-toggle" onclick="toggleTheme()">
                    <span class="icon">🌙</span>
                    <span class="text">Dark Mode</span>
                </button>
            </div>
        </aside>
        
        <!-- Main Content -->
        <main class="main-content">
            <header class="topbar">
                <div class="breadcrumb">
                    <span class="status-badge status-{project_info.get('status', '').lower().replace(' ', '-')}">
                        {project_info.get('status', 'In Progress')}
                    </span>
                </div>
                <div class="topbar-actions">
                    <button class="btn btn-secondary" onclick="window.print()">
                        <span>📄 Print</span>
                    </button>
                    <button class="btn btn-primary" onclick="exportPDF()">
                        <span>📥 Export PDF</span>
                    </button>
                </div>
            </header>
            
            <div class="content-wrapper">
                {content_html}
            </div>
        </main>
    </div>
    
    <script>
{self._get_javascript()}
    </script>
</body>
</html>"""
    
    def _get_section_icon(self, title: str) -> str:
        """Get icon for section based on title."""
        icons = {
            "summary": "📊",
            "unit": "🧪",
            "e2e": "🔗",
            "type": "🔒",
            "complexity": "📈",
            "architecture": "🏗️",
            "documentation": "📚",
            "module": "📦",
            "package": "📦"
        }
        
        title_lower = title.lower()
        for key, icon in icons.items():
            if key in title_lower:
                return icon
        return "📄"
    
    def _get_css(self) -> str:
        """Modern dashboard CSS with sidebar layout."""
        return """
/* Modern Dashboard Layout */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    /* Light Theme */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e9ecef;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --accent: #667eea;
    --accent-dark: #5568d3;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #3b82f6;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --border-radius: 8px;
    --sidebar-width: 260px;
}

[data-theme="dark"] {
    --bg-primary: #1a202c;
    --bg-secondary: #2d3748;
    --bg-tertiary: #4a5568;
    --text-primary: #f7fafc;
    --text-secondary: #cbd5e0;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.3);
}

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-secondary);
    color: var(--text-primary);
    line-height: 1.6;
}

/* Dashboard Layout */
.dashboard-layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: var(--sidebar-width);
    background: var(--bg-primary);
    border-right: 1px solid var(--bg-tertiary);
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    box-shadow: var(--shadow-md);
}

.sidebar-header {
    padding: 2rem 1.5rem;
    border-bottom: 1px solid var(--bg-tertiary);
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.grade-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    font-size: 1.5rem;
    font-weight: bold;
    background: var(--bg-secondary);
}

.grade-badge.grade-a { background: var(--success); color: white; }
.grade-badge.grade-b { background: var(--info); color: white; }
.grade-badge.grade-c { background: var(--warning); color: white; }
.grade-badge.grade-d,
.grade-badge.grade-f { background: var(--danger); color: white; }

.sidebar-nav {
    flex: 1;
    padding: 1rem 0;
}

.nav-link {
    display: flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.nav-link.active {
    background: var(--bg-secondary);
    color: var(--accent);
    border-right: 3px solid var(--accent);
}

.nav-icon {
    font-size: 1.25rem;
    margin-right: 0.75rem;
}

.sidebar-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--bg-tertiary);
}

.theme-toggle {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-primary);
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

.theme-toggle:hover {
    background: var(--bg-tertiary);
}

/* Main Content */
.main-content {
    margin-left: var(--sidebar-width);
    flex: 1;
    display: flex;
    flex-direction: column;
}

.topbar {
    background: var(--bg-primary);
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--bg-tertiary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm);
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.status-badge.status-complete { background: #d1fae5; color: #065f46; }
.status-badge.status-in-progress { background: #fef3c7; color: #92400e; }
.status-badge.status-critical { background: #fee2e2; color: #991b1b; }

.topbar-actions {
    display: flex;
    gap: 0.75rem;
}

.btn {
    padding: 0.625rem 1.25rem;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-primary {
    background: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.btn-secondary:hover {
    background: var(--bg-tertiary);
}

/* Content */
.content-wrapper {
    padding: 2rem;
    max-width: 1400px;
}

.content-section {
    margin-bottom: 3rem;
}

/* Metric Cards Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--bg-primary);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.card-icon {
    font-size: 2.5rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: var(--bg-secondary);
}

.card-green .card-icon { background: #d1fae5; }
.card-red .card-icon { background: #fee2e2; }
.card-yellow .card-icon { background: #fef3c7; }
.card-blue .card-icon { background: #dbeafe; }

.card-content {
    flex: 1;
}

.card-title {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.card-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
}

/* Section Content Styling */
.section-content h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.section-content h2 {
    font-size: 1.5rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--bg-tertiary);
    color: var(--text-primary);
}

.section-content h3 {
    font-size: 1.25rem;
    margin: 1.5rem 0 0.75rem;
    color: var(--text-primary);
}

.section-content table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    background: var(--bg-primary);
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.section-content th {
    background: var(--accent);
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.section-content td {
    padding: 1rem;
    border-bottom: 1px solid var(--bg-tertiary);
}

.section-content tr:last-child td {
    border-bottom: none;
}

.section-content tr:hover {
    background: var(--bg-secondary);
}

.section-content img {
    max-width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    margin: 1.5rem 0;
    box-shadow: var(--shadow-md);
}

.section-content pre {
    background: var(--bg-tertiary);
    padding: 1.5rem;
    border-radius: var(--border-radius);
    overflow-x: auto;
    margin: 1.5rem 0;
}

.section-content code {
    background: var(--bg-tertiary);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

.section-content ul,
.section-content ol {
    margin: 1rem 0;
    padding-left: 2rem;
}

.section-content li {
    margin: 0.5rem 0;
}

/* Responsive */
@media (max-width: 968px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}

/* Print Styles */
@media print {
    .sidebar,
    .topbar {
        display: none;
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .metric-card {
        break-inside: avoid;
    }
}
"""
    
    def _get_javascript(self) -> str:
        """JavaScript for theme toggle and smooth scrolling."""
        return """
// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    
    const btn = document.querySelector('.theme-toggle .text');
    btn.textContent = newTheme === 'light' ? 'Dark Mode' : 'Light Mode';
    
    const icon = document.querySelector('.theme-toggle .icon');
    icon.textContent = newTheme === 'light' ? '🌙' : '☀️';
    
    localStorage.setItem('theme', newTheme);
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.body.setAttribute('data-theme', savedTheme);
if (savedTheme === 'dark') {
    document.querySelector('.theme-toggle .text').textContent = 'Light Mode';
    document.querySelector('.theme-toggle .icon').textContent = '☀️';
}

// Smooth scrolling for navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        this.classList.add('active');
        
        // Smooth scroll to section
        targetSection.scrollIntoView({ behavior: 'smooth' });
    });
});

// Set first link as active on load
document.querySelector('.nav-link')?.classList.add('active');

// Export PDF function (placeholder)
function exportPDF() {
    window.print();
}

// Intersection Observer for active nav highlighting
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.content-section').forEach(section => {
    observer.observe(section);
});
"""
