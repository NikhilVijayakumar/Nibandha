"""
Modern tab-based HTML exporter for unified reports.
Creates interactive dashboard-style HTML with navigation tabs.
"""
from pathlib import Path
from typing import List, Dict, Optional, Any
import markdown2
import logging

logger = logging.getLogger("nibandha.export.tabs")


from .base_exporter import BaseHTMLExporter

class TabBasedHTMLExporter(BaseHTMLExporter):
    """Exports markdown to interactive HTML with tab navigation."""
    
    def __init__(self):
        super().__init__("nibandha.export.tabs")
    
    def _build_html_document(
        self, 
        sections: List[Dict[str, Any]], 
        project_info: Dict[str, str]
    ) -> str:
        """Build complete HTML document with tabs."""
        
        # Build tab navigation
        tabs_html = '<div class="tabs">'
        for i, section in enumerate(sections):
            active = ' active' if i == 0 else ''
            tabs_html += f'<button class="tab{active}" data-tab="{section["id"]}">{section["title"]}</button>'
        tabs_html += '</div>'
        
        # Build tab content
        content_html = '<div class="tab-contents">'
        for i, section in enumerate(sections):
            active = ' active' if i == 0 else ''
            content_html += f'''
            <div class="tab-content{active}" id="{section["id"]}">
                {section["content"]}
            </div>
            '''
        content_html += '</div>'
        
        # Complete document
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_info.get('name', 'Quality Report')}</title>
    <style>
{self._get_css()}
    </style>
</head>
<body>
    <div class="dashboard">
        <header class="dashboard-header">
            <div class="header-content">
                <h1>{project_info.get('name', 'Quality Report')}</h1>
                <div class="header-meta">
                    <span class="status">{project_info.get('status', '')}</span>
                    <span class="grade grade-{project_info.get('grade', 'F').lower()}">{project_info.get('grade', 'N/A')}</span>
                </div>
            </div>
        </header>
        
        <nav class="navigation">
            {tabs_html}
        </nav>
        
        <main class="content">
            {content_html}
        </main>
    </div>
    
    <script>
{self._get_javascript()}
    </script>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """Modern dashboard CSS."""
        return """
/* Modern Dashboard Styling */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f7fa;
    color: #2d3748;
}

.dashboard {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-header h1 {
    font-size: 1.8rem;
    font-weight: 600;
}

.header-meta {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.status {
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    font-size: 0.9rem;
}

.grade {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: bold;
    background: white;
    color: #2d3748;
}

.grade-a { background: #48bb78; color: white; }
.grade-b { background: #ed8936; color: white; }
.grade-c { background: #ecc94b; color: white; }
.grade-d { background: #f56565; color: white; }
.grade-f { background: #e53e3e; color: white; }

/* Navigation Tabs */
.navigation {
    background: white;
    border-bottom: 2px solid #e2e8f0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tabs {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    overflow-x: auto;
}

.tab {
    padding: 1rem 1.5rem;
    border: none;
    background: transparent;
    color: #718096;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
}

.tab:hover {
    color: #667eea;
    background: #f7fafc;
}

.tab.active {
    color: #667eea;
    border-bottom-color: #667eea;
    background: #f7fafc;
}

/* Content Area */
.content {
    flex: 1;
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 2rem;
    width: 100%;
}

.tab-content {
    display: none;
    animation: fadeIn 0.3s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Content Styling */
.tab-content h1 {
    font-size: 2rem;
    margin: 1.5rem 0 1rem;
    color: #1a202c;
}

.tab-content h2 {
    font-size: 1.5rem;
    margin: 2rem 0 1rem;
    color: #2d3748;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
}

.tab-content h3 {
    font-size: 1.2rem;
    margin: 1.5rem 0 0.75rem;
    color: #4a5568;
}

.tab-content table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    overflow: hidden;
}

.tab-content th {
    background: #667eea;
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.tab-content td {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
}

.tab-content tr:last-child td {
    border-bottom: none;
}

.tab-content tr:hover {
    background: #f7fafc;
}

.tab-content img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1.5rem 0;
}

.tab-content pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 1.5rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1.5rem 0;
}

.tab-content code {
    background: #edf2f7;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

.tab-content ul {
    margin: 1rem 0;
    padding-left: 2rem;
}

.tab-content li {
    margin: 0.5rem 0;
    line-height: 1.6;
}

/* Print Styles */
@media print {
    .navigation {
        display: none;
    }
    
    .tab-content {
        display: block !important;
        page-break-after: always;
    }
    
    .dashboard-header {
        background: #667eea;
        print-color-adjust: exact;
    }
}

/* Responsive */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .tabs {
        overflow-x: scroll;
    }
    
    .content {
        padding: 0 1rem;
    }
}
"""
    
    def _get_javascript(self) -> str:
        """Tab switching JavaScript."""
        return """
// Tab switching functionality
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        const targetId = this.getAttribute('data-tab');
        
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        this.classList.add('active');
        document.getElementById(targetId).classList.add('active');
        
        // Scroll to top smoothly
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
"""
