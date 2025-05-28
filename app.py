from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import importlib
import logging
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Memra Tool Execution API",
    description="API for executing Memra workflow tools",
    version="1.0.0"
)

# Request/Response models
class ToolExecutionRequest(BaseModel):
    tool_name: str
    hosted_by: str
    input_data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

class ToolExecutionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ToolDiscoveryResponse(BaseModel):
    tools: List[Dict[str, str]]

# Authentication
def verify_api_key(api_key: str) -> bool:
    """Verify if the provided API key is valid"""
    # Get valid keys from environment variable only - no defaults
    valid_keys_str = os.getenv("MEMRA_API_KEYS")
    if not valid_keys_str:
        # If no keys are set, deny all access
        return False
    
    valid_keys = valid_keys_str.split(",")
    return api_key.strip() in [key.strip() for key in valid_keys]

# FastAPI dependency for API key verification
async def get_api_key(x_api_key: Optional[str] = Header(None)):
    """FastAPI dependency to verify API key from header"""
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing API key. Please provide X-API-Key header."
        )
    
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key. Please contact info@memra.co for access."
        )
    
    logger.info(f"Valid API key used: {x_api_key}")
    return x_api_key

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """API documentation landing page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>memra API - Declarative AI Workflows</title>
        <style>
            @import url('https://fonts.cdnfonts.com/css/effra');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Effra', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #ffffff;
                background: #0f0f23;
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            /* Animated gradient background */
            .bg-gradient {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(ellipse at top left, rgba(88, 28, 135, 0.8) 0%, transparent 40%),
                            radial-gradient(ellipse at bottom right, rgba(59, 130, 246, 0.6) 0%, transparent 40%),
                            radial-gradient(ellipse at center, rgba(147, 51, 234, 0.4) 0%, transparent 60%),
                            #1a1a2e;
                z-index: -2;
            }
            
            /* Navigation */
            nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(15, 15, 35, 0.7);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                z-index: 1000;
                padding: 1.5rem 2rem;
            }
            
            .nav-content {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                font-size: 1.75rem;
                font-weight: 300;
                color: #ffffff;
                letter-spacing: -0.02em;
            }
            
            .status-badge {
                background: rgba(34, 197, 94, 0.15);
                border: 1px solid rgba(34, 197, 94, 0.3);
                color: #22c55e;
                padding: 0.4rem 1rem;
                border-radius: 999px;
                font-size: 0.875rem;
                font-weight: 400;
                animation: pulse 3s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            /* Main content */
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 10rem 2rem 4rem;
            }
            
            /* Hero section */
            .hero {
                text-align: center;
                margin-bottom: 8rem;
            }
            
            .hero h1 {
                font-size: clamp(2.5rem, 6vw, 4rem);
                font-weight: 300;
                margin-bottom: 1.5rem;
                color: #ffffff;
                letter-spacing: -0.02em;
            }
            
            .hero .tagline {
                font-size: 1.25rem;
                color: rgba(255, 255, 255, 0.6);
                margin-bottom: 4rem;
                font-weight: 300;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            /* Glass card effect */
            .glass-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 2.5rem;
                margin-bottom: 2rem;
                transition: all 0.3s ease;
            }
            
            .glass-card:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.12);
            }
            
            /* Code blocks */
            .code-block {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 1.5rem;
                font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.9);
                overflow-x: auto;
                margin: 1.5rem 0;
            }
            
            /* Use cases grid */
            .use-cases-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0 4rem 0;
            }
            
            .use-case-card {
                background: rgba(147, 51, 234, 0.05);
                border: 1px solid rgba(147, 51, 234, 0.2);
                border-radius: 16px;
                padding: 2rem;
                transition: all 0.3s ease;
            }
            
            .use-case-card:hover {
                background: rgba(147, 51, 234, 0.08);
                border-color: rgba(147, 51, 234, 0.4);
                transform: translateY(-2px);
            }
            
            .use-case-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .use-case-icon {
                font-size: 2rem;
            }
            
            .use-case-card h3 {
                font-size: 1.25rem;
                font-weight: 400;
                color: #ffffff;
            }
            
            .use-case-card p {
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 1rem;
                line-height: 1.6;
            }
            
            .code-snippet {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 0.75rem;
                font-size: 0.8rem;
                overflow-x: auto;
            }
            
            .code-snippet code {
                color: #a78bfa;
                font-family: 'Monaco', 'Menlo', monospace;
            }
            
            /* Features grid */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin: 3rem 0;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 16px;
                padding: 2.5rem;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                background: rgba(255, 255, 255, 0.04);
                border-color: rgba(147, 51, 234, 0.3);
                transform: translateY(-4px);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                opacity: 0.8;
            }
            
            .feature-title {
                font-size: 1.25rem;
                font-weight: 400;
                margin-bottom: 0.5rem;
                color: #ffffff;
            }
            
            .feature-desc {
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.95rem;
                line-height: 1.5;
            }
            
            /* Endpoints section */
            .endpoint {
                background: rgba(0, 0, 0, 0.2);
                border-left: 3px solid rgba(147, 51, 234, 0.5);
                padding: 1.5rem;
                margin: 1rem 0;
                border-radius: 0 12px 12px 0;
                transition: all 0.3s ease;
            }
            
            .endpoint:hover {
                background: rgba(0, 0, 0, 0.3);
                border-left-color: rgba(147, 51, 234, 0.8);
            }
            
            .method {
                display: inline-block;
                background: rgba(147, 51, 234, 0.15);
                color: #a78bfa;
                padding: 0.3rem 0.8rem;
                border-radius: 8px;
                font-weight: 500;
                font-size: 0.875rem;
                margin-right: 1rem;
            }
            
            /* CTA section */
            .cta-section {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                padding: 4rem;
                text-align: center;
                margin: 4rem 0;
            }
            
            .cta-button {
                display: inline-block;
                background: #e879f9;
                color: #0f0f23;
                padding: 1rem 2.5rem;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                font-size: 1rem;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(232, 121, 249, 0.3);
                background: #f0abfc;
            }
            
            /* Section headers */
            h2 {
                font-size: 2rem;
                font-weight: 300;
                margin-bottom: 2rem;
                color: #ffffff;
                letter-spacing: -0.02em;
            }
            
            /* Accent text */
            .accent {
                color: #e879f9;
            }
            
            /* Warning box */
            .warning-box {
                background: rgba(251, 191, 36, 0.1);
                border: 1px solid rgba(251, 191, 36, 0.3);
                border-radius: 12px;
                padding: 1rem 1.5rem;
                margin: 1.5rem 0;
                color: #fbbf24;
            }
            
            .warning-box strong {
                color: #f59e0b;
            }
            
            /* Links */
            a {
                color: #a78bfa;
                text-decoration: none;
                transition: color 0.3s ease;
            }
            
            a:hover {
                color: #e879f9;
            }
            
            /* Footer links */
            .footer-links {
                text-align: center;
                margin-top: 6rem;
                padding-top: 3rem;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
            
            .footer-links a {
                margin: 0 1.5rem;
                color: rgba(255, 255, 255, 0.5);
                font-size: 0.95rem;
            }
            
            .footer-links a:hover {
                color: rgba(255, 255, 255, 0.8);
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .hero h1 {
                    font-size: 2.5rem;
                }
                
                .hero .tagline {
                    font-size: 1.1rem;
                }
                
                .container {
                    padding: 7rem 1.5rem 2rem;
                }
                
                .glass-card {
                    padding: 2rem;
                }
                
                .cta-section {
                    padding: 3rem 2rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="bg-gradient"></div>
        
        <nav>
            <div class="nav-content">
                <div class="logo">
                    <span>memra API</span>
                </div>
                <div class="status-badge">● API Running</div>
            </div>
        </nav>
        
        <div class="container">
            <section class="hero">
                <h1>Build AI Agents That Actually Do Work</h1>
                <p class="tagline">Stop writing boilerplate. Define what you want done, not how to do it. memra handles the AI orchestration so you can ship faster.</p>
                
                <div class="glass-card">
                    <h2>🚀 Quick Start</h2>
                    <div class="code-block">pip install memra</div>
                    <div class="warning-box">
                        <strong>🔑 API Access Required:</strong> 
                        Contact <a href="mailto:info@memra.co">info@memra.co</a> for early access to the memra API
                    </div>
                    <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                        <h3 style="font-size: 1.25rem; margin-bottom: 1rem; color: #e879f9;">Next Steps:</h3>
                        <ol style="color: rgba(255, 255, 255, 0.8); line-height: 2;">
                            <li>Install the SDK: <code style="background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 4px;">pip install memra</code></li>
                            <li>Get your API key from <a href="mailto:info@memra.co">info@memra.co</a></li>
                            <li>Check out the examples below to see what you can build</li>
                            <li>Start with a simple agent and expand from there</li>
                        </ol>
                    </div>
                </div>
            </section>
            
            <section>
                <h2>🛠️ What Can You Build?</h2>
                <div class="use-cases-grid">
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">📄</span>
                            <h3>Document Processing Pipeline</h3>
                        </div>
                        <p>Auto-extract data from PDFs, invoices, contracts. Parse, validate, and push to your database.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Invoice Parser", tools=["PDFProcessor", "DatabaseWriter"])</code>
                        </div>
                    </div>
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">📧</span>
                            <h3>Customer Support Automation</h3>
                        </div>
                        <p>Handle support tickets, categorize issues, draft responses, and escalate complex cases.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Support Analyst", tools=["EmailReader", "TicketClassifier"])</code>
                        </div>
                    </div>
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">📊</span>
                            <h3>Data Analysis Workflows</h3>
                        </div>
                        <p>Connect to databases, run analysis, generate reports, and send insights to Slack.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Data Analyst", tools=["SQLQuery", "ChartGenerator", "SlackNotifier"])</code>
                        </div>
                    </div>
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">🔄</span>
                            <h3>API Integration Chains</h3>
                        </div>
                        <p>Chain multiple APIs together with AI decision-making between steps.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Integration Expert", tools=["HTTPClient", "JSONTransformer"])</code>
                        </div>
                    </div>
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">🔍</span>
                            <h3>Content Moderation Pipeline</h3>
                        </div>
                        <p>Review user content, flag issues, apply policies, and maintain compliance automatically.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Content Reviewer", tools=["TextAnalyzer", "PolicyEngine", "FlagSystem"])</code>
                        </div>
                    </div>
                    <div class="use-case-card">
                        <div class="use-case-header">
                            <span class="use-case-icon">🚀</span>
                            <h3>Lead Qualification System</h3>
                        </div>
                        <p>Score leads, enrich data from multiple sources, and route to the right sales team.</p>
                        <div class="code-snippet">
                            <code>Agent(role="Lead Scorer", tools=["CRMConnector", "DataEnricher", "RouterAgent"])</code>
                        </div>
                    </div>
                </div>
            </section>

            <section>
                <h2>✨ Why <span class="accent">memra</span>?</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📋</div>
                        <div class="feature-title">Declarative Design</div>
                        <div class="feature-desc">Define workflows like Kubernetes YAML. Version control your AI business logic.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <div class="feature-title">Multi-LLM Support</div>
                        <div class="feature-desc">Seamlessly integrate OpenAI, Anthropic, and other providers with zero config changes.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💬</div>
                        <div class="feature-title">Self-Documenting</div>
                        <div class="feature-desc">Agents explain their decisions in natural language for full transparency.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🏗️</div>
                        <div class="feature-title">Enterprise Ready</div>
                        <div class="feature-desc">Battle-tested on real databases, files, and complex business workflows.</div>
                    </div>
                </div>
            </section>
            
            <section>
                <h2>📡 API Endpoints</h2>
                <div class="glass-card">
                    <div class="endpoint">
                        <span class="method">GET</span>/health
                        <div>Health check and API status verification</div>
                    </div>
                    <div class="endpoint">
                        <span class="method">GET</span>/tools/discover
                        <div>Discover available workflow tools and their capabilities</div>
                    </div>
                    <div class="endpoint">
                        <span class="method">POST</span>/tools/execute
                        <div>Execute workflow tools with structured input data</div>
                    </div>
                </div>
            </section>
            
            <section>
                <h2>📚 Full Example: Invoice Processing</h2>
                <div class="glass-card">
                    <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1.5rem;">
                        Here's how you'd build an invoice processing system that extracts data and updates your database:
                    </p>
                    <div class="code-block">from memra import Agent, Department
from memra.execution import ExecutionEngine

# 1. Define what you want done (not how)
invoice_processor = Agent(
    role="Invoice Processor",
    job="Extract vendor, amount, and line items from PDF invoices", 
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra"},
        {"name": "DataValidator", "hosted_by": "memra"},
        {"name": "DatabaseWriter", "hosted_by": "memra"}
    ]
)

# 2. Create a department (group related agents)
finance_dept = Department(
    name="Accounts Payable",
    agents=[invoice_processor]
)

# 3. Execute - memra handles the AI orchestration
engine = ExecutionEngine()
result = engine.execute_department(
    finance_dept, 
    {"file": "invoice.pdf", "database": "postgresql://..."}
)

# Result: Structured data extracted and saved to your DB
print(result.summary)  # "Extracted invoice #INV-001 for $1,234.56 from Acme Corp"</div>
                </div>
            </section>
            
            <div class="cta-section">
                <h2>Ready to Build Your AI Workforce?</h2>
                <p style="color: rgba(255, 255, 255, 0.6); margin-bottom: 2rem;">Join innovative teams automating their workflows with memra</p>
                <a href="mailto:info@memra.co" class="cta-button">Get Started Now</a>
            </div>
            
            <div class="footer-links">
                <a href="https://pypi.org/project/memra/">PyPI Package</a>
                <a href="https://github.com/memra-platform/memra-sdk">GitHub</a>
                <a href="https://memra.co">Website</a>
                <a href="mailto:info@memra.co">Contact</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check for Fly.io"""
    return {"status": "healthy"}

@app.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    api_key: Optional[str] = Depends(get_api_key)
):
    """Execute a tool with the given input data"""
    try:
        logger.info(f"Executing tool: {request.tool_name}")
        
        # Import the tool registry from local logic
        from memra.tool_registry import ToolRegistry
        
        # Create registry and execute tool
        registry = ToolRegistry()
        result = registry.execute_tool(
            request.tool_name,
            request.hosted_by,
            request.input_data,
            request.config
        )
        
        return ToolExecutionResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return ToolExecutionResponse(
            success=False,
            error=str(e)
        )

@app.get("/tools/discover", response_model=ToolDiscoveryResponse)
async def discover_tools(api_key: Optional[str] = Depends(get_api_key)):
    """Discover available tools"""
    try:
        from memra.tool_registry import ToolRegistry
        
        registry = ToolRegistry()
        tools = registry.discover_tools()
        
        return ToolDiscoveryResponse(tools=tools)
        
    except Exception as e:
        logger.error(f"Tool discovery failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 