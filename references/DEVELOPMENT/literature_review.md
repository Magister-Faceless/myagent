# Literature Review Agent - Refined Implementation Plan (DeepAgents v1.1)

## 1. Agent Overview
The Literature Review Agent is a sophisticated agent following the deepagents v1.1 framework for conducting comprehensive, human-in-the-loop systematic literature reviews. It leverages Perplexity's scholarly search capabilities, Grok-4-Fast's vision and context capabilities, and advanced context management to handle large-scale academic research with full paper analysis.

## 2. Core Philosophy & Workflow

### 2.1 Human-in-the-Loop Validation & Planning
**Primary Distinction**: Unlike other agents, the Literature Review Agent requires explicit user approval before executing any research activities.

1. **Request Validation**: Agent first determines if the request aligns with scientific literature review use cases
2. **Structured Planning**: Creates detailed, user-reviewable plan with clear title, description, and methodology
3. **User Approval Required**: No execution until user explicitly approves the plan
4. **Iterative Refinement**: Uses built-in tools for collaborative plan refinement with user

### 2.2 Model Selection Strategy
**Grok-4-Fast (Primary)**: Used for most coordination, validation, and analysis tasks due to:
- 2 million token context window for handling large documents
- Vision capabilities for analyzing images, tables, and figures
- Excellent thinking and planning capabilities
- Fastest processing speed

**Perplexity Sonar Deep Research**: Reserved for specialized deep research tasks:
- Multi-step research processes across multiple papers
- Comprehensive report generation with citations
- Long-running synthesis and analysis tasks
- Cross-referencing and evidence synthesis

### 2.3 Core API Integration
**CORE API Tools**: Fully integrated for academic paper discovery and metadata extraction
**Existing Research Infrastructure**: Leverages all established research tools and workflows
**File Management**: Built-in deepagents file tools for context management across subagents

## 3. Architecture (DeepAgents v1.1 Compliant)

### 3.1 Main Agent Structure
- **File**: `backend/agents/literature_review.py`
- **Pattern**: Uses `create_deep_agent()` with specialized planning workflow
- **Instructions**: Focused on validation, planning, and human-in-the-loop coordination
- **Integration**: Registered in `config/agent_registry.py`

### 3.2 Subagents (Following SubAgent Pattern)

#### Planning & Validation Subagents (Grok-4-Fast Model)
1. **Request Validator** (`subagents/request_validator.py`)
   - Purpose: Determines if request is appropriate for literature review
   - Function: Analyzes user prompt against expertise boundaries
   - Model: Grok-4-Fast (default) for fast validation and reasoning
   - Output: Recommendation to proceed or redirect to other agents

2. **Planning Coordinator** (`subagents/planning_coordinator.py`)
   - Purpose: Creates and refines structured research plans
   - Function: Generates detailed methodology, scope, and workflow
   - Model: Grok-4-Fast (default) for planning and coordination
   - Human-in-the-loop: Requires user approval before execution

#### Research Execution Subagents (Grok-4-Fast Model)
3. **Literature Screener** (`subagents/literature_screener.py`)
   - Purpose: PRISMA-compliant paper screening with CORE API integration
   - Features: Uses Grok-4-Fast's vision capabilities for full-text analysis
   - Model: Grok-4-Fast (default) for screening and vision analysis
   - File Access: Reads/writes screening results and PRISMA data

4. **Content Analyzer** (`subagents/content_analyzer.py`)
   - Purpose: Comprehensive analysis of 50+ full papers
   - Features: Grok-4-Fast vision integration for images/tables/figures
   - Model: Grok-4-Fast (default) leveraging 2M token context window
   - Context Management: Creates structured summaries and focused excerpts
   - File Access: Creates paper summary files, reads previous analyses

#### Deep Research Subagent (Perplexity Sonar Model)
5. **Synthesis Engine** (`subagents/synthesis_engine.py`)
   - Purpose: Advanced evidence synthesis and comprehensive report generation
   - Model: **Perplexity Sonar Deep Research** for multi-step synthesis
   - Enhanced: Long-running analysis across multiple papers with citations
   - Context Management: Orchestrates information retrieval from all context files
   - File Access: Reads all paper summaries, thematic excerpts, creates final report

### 3.3 Tools (Following @tool Decorator Pattern)

#### Planning Tools
1. **Request Analysis Tools**
   - `validate_request_scope.py` - Determines appropriateness of request
   - `create_research_plan.py` - Generates structured research methodology
   - `refine_plan_with_user.py` - Collaborative plan refinement

#### Research Tools (Integrated with CORE API)
2. **Enhanced Literature Review Tools** (`tools/literature/`)
   - `scholarly_search_core.py` - Academic search using existing CORE API tools
   - `full_paper_analyzer.py` - Comprehensive paper analysis (text + Grok-4-Fast vision)
   - `vision_content_extractor.py` - Extract data from images/tables using Grok-4-Fast
   - `context_manager.py` - Manages large content volumes across files
   - `structured_summary_generator.py` - Creates focused summaries and excerpts

#### Deep Research Tools (Perplexity Integration)
3. **Perplexity Research Tools** (`tools/perplexity/`)
   - `perplexity_sonar_synthesis.py` - Long-form synthesis using Sonar Deep Research
   - `perplexity_cross_reference.py` - Multi-paper analysis and citation generation
   - `perplexity_evidence_assessment.py` - Quality and bias evaluation

### 3.4 File Management & Cross-Agent Access
**Shared File System**: All agents and subagents have access to the same file workspace
**Built-in File Tools**: Leverage deepagents' `read_file`, `write_file`, `ls` tools
**File Naming Convention**: Structured naming for easy discovery and access
**Context Awareness**: Agents instructed to list and read relevant files before operations

## 4. Advanced Context Management Strategy

### 4.1 Large-Scale Content Handling
**Challenge**: 50+ full papers exceed model context windows
**Solution**: Hierarchical content management system

1. **Level 1 - Paper Summaries**
   - One structured summary file per paper
   - Key metadata, main findings, crucial quotes
   - Image/table descriptions using vision models

2. **Level 2 - Thematic Excerpts**
   - Topic-specific files with relevant excerpts
   - Cross-referenced quotes and data points
   - Organized by research question components

3. **Level 3 - Synthesis Files**
   - Integrated analysis files combining multiple papers
   - Perplexity Sonar-generated insights
   - Evidence tables and quality assessments

### 4.2 Vision Model Integration
**Multi-modal Analysis**: Extract information from:
- Tables and figures
- Charts and graphs
- Methodology diagrams
- Statistical results

**Implementation**: Dedicated vision analysis tools that create textual descriptions and extractable data from visual content.

## 5. Workflow Implementation

### 5.1 Phase 1: Validation & Planning (Human-in-the-Loop)
1. **Request Analysis**: Validate scope and appropriateness
2. **Plan Generation**: Create detailed research methodology
3. **User Review**: Present plan for approval/modification
4. **Iterative Refinement**: Use built-in tools for collaborative editing
5. **Final Approval**: User must explicitly approve before proceeding

### 5.2 Phase 2: Comprehensive Literature Search
1. **Scholarly Search**: Perplexity-powered academic search
2. **Full-Text Acquisition**: Retrieve complete papers (PDFs, web content)
3. **Initial Screening**: Title/abstract review with PRISMA compliance

### 5.3 Phase 3: Deep Content Analysis
1. **Full Paper Processing**: Analyze text, images, tables, figures
2. **Vision Model Analysis**: Extract data from visual elements
3. **Structured Summarization**: Create focused, quotable excerpts
4. **Context File Creation**: Organize content for synthesis phase

### 5.4 Phase 4: Advanced Synthesis
1. **Perplexity Sonar Analysis**: Deep research across all papers
2. **Thematic Integration**: Identify patterns and contradictions
3. **Evidence Strength Assessment**: Quality and bias evaluation
4. **Gap Analysis**: Identify research gaps and future directions

### 5.5 Phase 5: Orchestrated Reporting
1. **Multi-Agent Coordination**: Subagents retrieve from context files
2. **Comprehensive Report Generation**: Synthesize all findings
3. **Reference Management**: Proper citation and bibliography
4. **Export Capabilities**: Multiple formats (academic, policy, etc.)

## 6. Perplexity Model Integration Strategy

### 6.1 Model Selection Rationale
**Perplexity Sonar Pro/Deep**: Primary choice for literature review due to:
- Extended context windows for large document analysis
- Scholarly search capabilities
- Long-form research task handling
- Multi-step reasoning for complex synthesis

**Implementation Options**:
1. **As Main Agent Model**: For overall coordination and planning
2. **As Subagent Models**: For specific analysis tasks
3. **As Tools**: For targeted research functions

### 6.2 Integration Patterns
**Hybrid Approach**:
- Main agent: Standard model for coordination and validation
- Synthesis subagent: Perplexity Sonar for deep analysis
- Search tools: Perplexity scholarly search integration
- Cross-reference tools: Perplexity for multi-paper analysis

## 7. Quality Assurance & Academic Standards

### 7.1 Enhanced PRISMA Compliance
- Full-text analysis capabilities
- Vision model integration for complete data extraction
- Perplexity-powered quality assessment
- Comprehensive audit trails

### 7.2 Reproducibility Features
- Complete methodology documentation
- Version-controlled analysis files
- Transparent decision tracking
- Exportable search strategies and screening criteria

### 7.3 Quality Control Measures
- Multi-agent validation of key decisions
- Perplexity cross-verification of critical findings
- Human oversight at all major decision points
- Comprehensive error checking and validation

## 8. Implementation Priority & Phases

### Phase 1: Foundation (High Priority)
1. **Request Validator Subagent**: Core validation logic
2. **Planning Coordinator**: Human-in-the-loop planning system
3. **Basic Context Management**: File handling for large content

### Phase 2: Enhanced Research (High Priority)
1. **Perplexity Integration**: Scholarly search and analysis tools
2. **Vision Model Tools**: Image and table analysis
3. **Content Analyzer Subagent**: Full paper processing

### Phase 3: Advanced Synthesis (Medium Priority)
1. **Perplexity Sonar Integration**: Deep research capabilities
2. **Synthesis Engine Enhancement**: Multi-file orchestration
3. **Advanced Context Management**: Hierarchical content organization

### Phase 4: Optimization (Low Priority)
1. **Performance Optimization**: Large-scale processing efficiency
2. **Advanced Quality Assessment**: Automated bias detection
3. **Collaborative Features**: Multi-user review capabilities

## 9. Testing Strategy

### 9.1 Validation Testing
- Request validation accuracy
- Plan generation quality
- User experience in approval workflow

### 9.2 Content Processing Testing
- Full paper analysis capabilities
- Vision model accuracy on academic content
- Context management system reliability

### 9.3 Synthesis Testing
- Perplexity Sonar integration effectiveness
- Multi-agent coordination accuracy
- Final report quality assessment

### 9.4 Performance Testing
- Large-scale content handling (50+ papers)
- Context window management efficiency
- Processing time optimization

## 10. Success Metrics

### 10.1 Quality Metrics
- **Comprehensiveness**: Percentage of relevant literature captured
- **Accuracy**: Error rate in content extraction and synthesis
- **Depth**: Quality of analysis compared to human experts

### 10.2 Efficiency Metrics
- **Processing Speed**: Time to analyze large paper sets
- **Context Efficiency**: Effective use of available context windows
- **User Experience**: Time from request to approved plan

### 10.3 Academic Standards
- **PRISMA Compliance**: Adherence to systematic review guidelines
- **Reproducibility**: Ability to replicate results
- **Citation Accuracy**: Proper referencing and bibliography generation

## 11. Risk Mitigation

### 11.1 Context Window Limitations
- **Strategy**: Hierarchical content management with focused excerpts
- **Fallback**: Automatic content summarization when limits approached
- **Monitoring**: Real-time context usage tracking

### 11.2 Vision Model Limitations
- **Strategy**: Hybrid text + vision analysis with validation
- **Fallback**: Text-based analysis when vision fails
- **Quality Control**: Cross-verification of visual data extraction

### 11.3 Perplexity Model Availability
- **Strategy**: Multiple model options with graceful degradation
- **Fallback**: Standard models for basic functionality
- **Monitoring**: API availability and response time tracking

This refined plan creates a comprehensive, human-in-the-loop literature review system that can handle large-scale academic research while maintaining rigorous standards and user control throughout the process.

## 12. Literature Review Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           LITERATURE REVIEW AGENT WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│  USER REQUEST   │───▶│ REQUEST VALIDATOR│───▶│  PLANNING COORDINATOR           │
│                 │    │ (Grok-4-Fast)    │    │  (Grok-4-Fast)                  │
│ "Review X topic"│    │                  │    │                                 │
└─────────────────┘    │ ✓ Validates scope│    │ • Creates research plan         │
                       │ ✓ Checks expertise│    │ • Defines methodology           │
                       │ ✓ Recommends      │    │ • Sets inclusion/exclusion      │
                       │   proceed/redirect│    │ • Generates workflow            │
                       └──────────────────┘    └─────────────────────────────────┘
                                                                │
                                                                ▼
                       ┌─────────────────────────────────────────────────────────┐
                       │              HUMAN APPROVAL REQUIRED                    │
                       │  📋 plan_draft.md - Research plan for user review      │
                       │  ⏸️  WORKFLOW PAUSES UNTIL USER APPROVES              │
                       └─────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼ USER APPROVES
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          RESEARCH EXECUTION PHASE                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│ LITERATURE      │───▶│ CONTENT ANALYZER │───▶│ SYNTHESIS ENGINE                │
│ SCREENER        │    │ (Grok-4-Fast)    │    │ (Perplexity Sonar Deep)         │
│ (Grok-4-Fast)   │    │                  │    │                                 │
└─────────────────┘    └──────────────────┘    └─────────────────────────────────┘
         │                       │                              │
         ▼                       ▼                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│ CORE API SEARCH │    │ VISION ANALYSIS  │    │ DEEP RESEARCH & SYNTHESIS       │
│ • search_works  │    │ • Images/Tables  │    │ • Multi-paper analysis          │
│ • get_work_by_id│    │ • Figures/Charts │    │ • Evidence assessment           │
│ • aggregate_works│    │ • Statistical    │    │ • Citation generation           │
│ • Paper discovery│    │   results        │    │ • Comprehensive reporting       │
└─────────────────┘    │ • Methodology    │    └─────────────────────────────────┘
                       │   diagrams       │
                       └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            FILE MANAGEMENT SYSTEM                               │
└─────────────────────────────────────────────────────────────────────────────────┘

LEVEL 1: PAPER SUMMARIES (Created by Content Analyzer)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ paper_001.md    │  │ paper_002.md    │  │ paper_050.md    │
│ • Metadata      │  │ • Metadata      │  │ • Metadata      │
│ • Key findings  │  │ • Key findings  │  │ • Key findings  │
│ • Crucial quotes│  │ • Crucial quotes│  │ • Crucial quotes│
│ • Vision data   │  │ • Vision data   │  │ • Vision data   │
│ • Quality score │  │ • Quality score │  │ • Quality score │
└─────────────────┘  └─────────────────┘  └─────────────────┘

LEVEL 2: THEMATIC EXCERPTS (Created by Literature Screener)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ theme_methods.md│  │ theme_results.md│  │ theme_gaps.md   │
│ • Method quotes │  │ • Result quotes │  │ • Gap analysis  │
│ • Cross-refs    │  │ • Statistical   │  │ • Future work   │
│ • Paper IDs     │  │   data          │  │ • Limitations   │
└─────────────────┘  │ • Effect sizes  │  └─────────────────┘
                     └─────────────────┘

LEVEL 3: SYNTHESIS FILES (Created by Synthesis Engine)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ evidence_table. │  │ quality_assess. │  │ final_report.md │
│ md              │  │ md              │  │ • Introduction  │
│ • Study details │  │ • ROB2 scores   │  │ • Methods       │
│ • Effect sizes  │  │ • Newcastle-    │  │ • Results       │
│ • Confidence    │  │   Ottawa        │  │ • Discussion    │
│   intervals     │  │ • CASP ratings  │  │ • Conclusions   │
└─────────────────┘  └─────────────────┘  │ • References    │
                                          └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CONTEXT RETRIEVAL PROCESS                                │
└─────────────────────────────────────────────────────────────────────────────────┘

SYNTHESIS ENGINE WORKFLOW:
1. 📂 Lists all files using `ls` tool
2. 📖 Reads relevant paper summaries using `read_file`
3. 🔍 Extracts thematic excerpts for current section
4. 🧠 Uses Perplexity Sonar for deep analysis and synthesis
5. ✍️ Writes section to final report using `write_file`
6. 🔄 Repeats for each report section
7. 📚 Generates bibliography from all citations

CONTEXT MANAGEMENT STRATEGY:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 2M Token Window │───▶│ Focused Retrieval│───▶│ Structured      │
│ (Grok-4-Fast)   │    │ • Read only      │    │ Writing         │
│                 │    │   relevant files │    │ • Section by    │
│ • Handles large │    │ • Extract key    │    │   section       │
│   documents     │    │   quotes         │    │ • Proper        │
│ • Vision        │    │ • Maintain       │    │   citations     │
│   analysis      │    │   context        │    │ • Academic      │
│ • Multi-modal   │    │ • Cross-reference│    │   formatting    │
└─────────────────┘    └──────────────────┘    └─────────────────┘

FINAL OUTPUT:
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          COMPREHENSIVE LITERATURE REVIEW                        │
│                                                                                 │
│ 📄 final_report.md - Complete systematic review                                │
│ 📊 prisma_diagram.md - PRISMA flow chart                                       │
│ 📚 bibliography.bib - All citations in BibTeX format                          │
│ 📈 evidence_summary.md - Quality assessment summary                            │
│ 🔍 methodology.md - Reproducible search strategy                              │
│                                                                                 │
│ ✅ PRISMA Compliant ✅ Academically Rigorous ✅ Fully Cited                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 13. Model Usage Summary

### **Grok-4-Fast (Primary Model)**
- **Main Literature Review Agent**: Coordination and planning
- **Request Validator**: Fast validation and reasoning
- **Planning Coordinator**: Plan generation and refinement  
- **Literature Screener**: Paper screening and vision analysis
- **Content Analyzer**: Full paper analysis with 2M token context

**Advantages**: 
- 2 million token context window handles large documents
- Vision capabilities for images, tables, figures
- Fast processing for interactive workflows
- Excellent reasoning for validation and planning

### **Perplexity Sonar Deep Research (Specialized Model)**
- **Synthesis Engine**: Deep research and comprehensive reporting
- **Cross-referencing**: Multi-paper analysis and citation
- **Evidence Assessment**: Quality evaluation and bias detection

**Advantages**:
- Specialized for long-running research processes
- Multi-step reasoning across multiple papers
- Built-in citation and reference capabilities
- Comprehensive structured report generation

This two-model approach optimizes for both speed (Grok-4-Fast) and depth (Perplexity Sonar), ensuring efficient workflow while maintaining research quality.
