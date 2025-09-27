"""
Quality Assessment Tool

Assesses the quality and risk of bias in research studies.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List
import json
from datetime import datetime


@tool
def quality_assessment(
    paper_metadata: Dict[str, Any],
    assessment_tool: str = "rob2",
    study_type: str = "rct"
) -> Dict[str, Any]:
    """Assess the quality and risk of bias of a research study.
    
    Args:
        paper_metadata: Dictionary containing paper information
        assessment_tool: Quality assessment tool ("rob2", "newcastle_ottawa", "casp")
        study_type: Type of study ("rct", "cohort", "case_control", "systematic_review")
        
    Returns:
        Dictionary containing quality assessment results
    """
    try:
        # Validate inputs
        if not paper_metadata:
            return {
                "status": "error",
                "message": "Paper metadata is required for quality assessment"
            }
        
        # Perform assessment based on tool and study type
        if assessment_tool.lower() == "rob2" and study_type.lower() == "rct":
            assessment = _assess_rob2_rct(paper_metadata)
        elif assessment_tool.lower() == "newcastle_ottawa":
            if study_type.lower() in ["cohort", "case_control"]:
                assessment = _assess_newcastle_ottawa(paper_metadata, study_type)
            else:
                return {
                    "status": "error",
                    "message": f"Newcastle-Ottawa scale not applicable to {study_type} studies"
                }
        elif assessment_tool.lower() == "casp":
            assessment = _assess_casp(paper_metadata, study_type)
        else:
            return {
                "status": "error",
                "message": f"Unsupported assessment tool '{assessment_tool}' for study type '{study_type}'"
            }
        
        return {
            "status": "success",
            "assessment": assessment,
            "tool": assessment_tool,
            "study_type": study_type,
            "paper_title": paper_metadata.get('title', 'Unknown'),
            "assessed_at": datetime.utcnow().isoformat(),
            "message": f"Successfully completed {assessment_tool} assessment for {study_type} study"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to complete quality assessment using {assessment_tool}"
        }


def _assess_rob2_rct(paper_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess RCT using RoB 2.0 tool."""
    # This is a simplified mock assessment
    # In a real implementation, this would analyze the paper content
    
    domains = {
        "randomization_process": {
            "judgment": "low",  # low, some_concerns, high
            "rationale": "Adequate randomization method described",
            "questions": {
                "q1_1": "Was the allocation sequence random?",
                "q1_2": "Was the allocation sequence concealed until participants were enrolled?",
                "q1_3": "Did baseline differences suggest problems with randomization?"
            }
        },
        "deviations_intended_interventions": {
            "judgment": "some_concerns",
            "rationale": "Some protocol deviations noted but balanced between groups",
            "questions": {
                "q2_1": "Were participants aware of their assigned intervention?",
                "q2_2": "Were carers and people delivering interventions aware?",
                "q2_3": "Were there deviations from intended intervention?"
            }
        },
        "missing_outcome_data": {
            "judgment": "low",
            "rationale": "Low dropout rate with reasons provided",
            "questions": {
                "q3_1": "Were data for this outcome available for all participants?",
                "q3_2": "Is there evidence that result was not biased by missing data?",
                "q3_3": "Could missingness depend on its true value?"
            }
        },
        "measurement_outcome": {
            "judgment": "low",
            "rationale": "Objective outcome measurement methods used",
            "questions": {
                "q4_1": "Was the method of measuring the outcome inappropriate?",
                "q4_2": "Could measurement have differed between groups?",
                "q4_3": "Were outcome assessors aware of intervention received?"
            }
        },
        "selection_reported_result": {
            "judgment": "low",
            "rationale": "Pre-specified analysis plan followed",
            "questions": {
                "q5_1": "Were the data analyzed in accordance with pre-specified plan?",
                "q5_2": "Were multiple eligible outcome measurements available?",
                "q5_3": "Were multiple eligible analyses available?"
            }
        }
    }
    
    # Calculate overall risk of bias
    judgments = [domain["judgment"] for domain in domains.values()]
    if "high" in judgments:
        overall_risk = "high"
    elif "some_concerns" in judgments:
        overall_risk = "some_concerns"
    else:
        overall_risk = "low"
    
    return {
        "tool": "RoB 2.0",
        "domains": domains,
        "overall_risk": overall_risk,
        "summary": f"Overall risk of bias: {overall_risk}",
        "recommendations": _get_rob2_recommendations(overall_risk)
    }


def _assess_newcastle_ottawa(paper_metadata: Dict[str, Any], study_type: str) -> Dict[str, Any]:
    """Assess cohort or case-control study using Newcastle-Ottawa Scale."""
    if study_type.lower() == "cohort":
        return _assess_newcastle_ottawa_cohort(paper_metadata)
    else:
        return _assess_newcastle_ottawa_case_control(paper_metadata)


def _assess_newcastle_ottawa_cohort(paper_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess cohort study using Newcastle-Ottawa Scale."""
    # Mock assessment for cohort studies
    categories = {
        "selection": {
            "representativeness": {"score": 1, "max": 1, "description": "Truly representative of average in community"},
            "selection_non_exposed": {"score": 1, "max": 1, "description": "Drawn from same community as exposed"},
            "ascertainment_exposure": {"score": 1, "max": 1, "description": "Secure record or structured interview"},
            "outcome_not_present": {"score": 1, "max": 1, "description": "Demonstration that outcome was not present at start"}
        },
        "comparability": {
            "comparability": {"score": 2, "max": 2, "description": "Study controls for most important factors"}
        },
        "outcome": {
            "assessment_outcome": {"score": 1, "max": 1, "description": "Independent blind assessment"},
            "follow_up_length": {"score": 1, "max": 1, "description": "Follow-up long enough for outcomes"},
            "adequacy_follow_up": {"score": 1, "max": 1, "description": "Complete follow-up or subjects lost unlikely to bias"}
        }
    }
    
    total_score = sum(item["score"] for category in categories.values() for item in category.values())
    max_score = sum(item["max"] for category in categories.values() for item in category.values())
    
    # Quality interpretation
    if total_score >= 7:
        quality = "high"
    elif total_score >= 5:
        quality = "moderate"
    else:
        quality = "low"
    
    return {
        "tool": "Newcastle-Ottawa Scale (Cohort)",
        "categories": categories,
        "total_score": total_score,
        "max_score": max_score,
        "quality": quality,
        "summary": f"Quality rating: {quality} ({total_score}/{max_score})"
    }


def _assess_newcastle_ottawa_case_control(paper_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess case-control study using Newcastle-Ottawa Scale."""
    # Mock assessment for case-control studies
    categories = {
        "selection": {
            "case_definition": {"score": 1, "max": 1, "description": "Independent validation with reference standard"},
            "representativeness_cases": {"score": 1, "max": 1, "description": "Consecutive or obviously representative series"},
            "selection_controls": {"score": 1, "max": 1, "description": "Community controls"},
            "definition_controls": {"score": 1, "max": 1, "description": "No history of disease"}
        },
        "comparability": {
            "comparability": {"score": 2, "max": 2, "description": "Study controls for most important factors"}
        },
        "exposure": {
            "ascertainment_exposure": {"score": 1, "max": 1, "description": "Secure record or structured interview"},
            "same_method": {"score": 1, "max": 1, "description": "Same method of ascertainment for cases and controls"},
            "non_response_rate": {"score": 1, "max": 1, "description": "Same rate for both groups"}
        }
    }
    
    total_score = sum(item["score"] for category in categories.values() for item in category.values())
    max_score = sum(item["max"] for category in categories.values() for item in category.values())
    
    # Quality interpretation
    if total_score >= 7:
        quality = "high"
    elif total_score >= 5:
        quality = "moderate"
    else:
        quality = "low"
    
    return {
        "tool": "Newcastle-Ottawa Scale (Case-Control)",
        "categories": categories,
        "total_score": total_score,
        "max_score": max_score,
        "quality": quality,
        "summary": f"Quality rating: {quality} ({total_score}/{max_score})"
    }


def _assess_casp(paper_metadata: Dict[str, Any], study_type: str) -> Dict[str, Any]:
    """Assess study using CASP (Critical Appraisal Skills Programme) checklist."""
    # Mock CASP assessment
    questions = {
        "clear_aims": {"answer": "yes", "question": "Did the study address a clearly focused question?"},
        "appropriate_method": {"answer": "yes", "question": "Was the research method appropriate?"},
        "appropriate_design": {"answer": "yes", "question": "Was the study design appropriate?"},
        "recruitment": {"answer": "partly", "question": "Was the recruitment strategy appropriate?"},
        "data_collection": {"answer": "yes", "question": "Was the data collected appropriately?"},
        "researcher_bias": {"answer": "yes", "question": "Has the relationship between researcher and participants been considered?"},
        "ethical_issues": {"answer": "yes", "question": "Have ethical issues been taken into consideration?"},
        "rigorous_analysis": {"answer": "yes", "question": "Was the data analysis sufficiently rigorous?"},
        "clear_findings": {"answer": "yes", "question": "Is there a clear statement of findings?"},
        "valuable_research": {"answer": "yes", "question": "How valuable is the research?"}
    }
    
    # Calculate quality score
    yes_count = sum(1 for q in questions.values() if q["answer"] == "yes")
    partly_count = sum(1 for q in questions.values() if q["answer"] == "partly")
    total_questions = len(questions)
    
    quality_score = (yes_count + 0.5 * partly_count) / total_questions
    
    if quality_score >= 0.8:
        quality = "high"
    elif quality_score >= 0.6:
        quality = "moderate"
    else:
        quality = "low"
    
    return {
        "tool": f"CASP ({study_type})",
        "questions": questions,
        "yes_count": yes_count,
        "partly_count": partly_count,
        "no_count": total_questions - yes_count - partly_count,
        "quality_score": round(quality_score, 2),
        "quality": quality,
        "summary": f"CASP quality rating: {quality} ({quality_score:.1%})"
    }


def _get_rob2_recommendations(overall_risk: str) -> List[str]:
    """Get recommendations based on RoB 2.0 assessment."""
    if overall_risk == "low":
        return [
            "Study has low risk of bias and can be included with high confidence",
            "Results are likely to be reliable for decision making"
        ]
    elif overall_risk == "some_concerns":
        return [
            "Study has some concerns about bias - include but interpret with caution",
            "Consider sensitivity analysis excluding this study",
            "Look for additional studies to strengthen evidence base"
        ]
    else:  # high risk
        return [
            "Study has high risk of bias - consider excluding from analysis",
            "If included, clearly note limitations in interpretation",
            "Results should not be given significant weight in conclusions"
        ]
