"""
Tools for Quality Assurance Agent
Implements specialized tools for content quality analysis, validation, and improvement
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import re

# Database and external service imports
import asyncpg
from supabase import create_client, Client

# AI and analysis tools
import openai
from sentence_transformers import SentenceTransformer
import spacy

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Shared database connection for all tools."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.warning("Supabase credentials not found")
    
    def is_connected(self) -> bool:
        return self.supabase is not None

# Global database connection
db_connection = DatabaseConnection()

class ContentQualityAnalyzer:
    """Analyzes content quality across multiple dimensions."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.quality_standards = self._load_quality_standards()
        self.analysis_templates = self._load_analysis_templates()
    
    def _load_quality_standards(self) -> Dict[str, Dict[str, Any]]:
        """Load quality standards for different content types."""
        return {
            "lesson": {
                "required_sections": ["learning_objectives", "activities", "assessment"],
                "min_activities": 3,
                "max_duration": 120,
                "engagement_score_threshold": 75
            },
            "exercise": {
                "required_fields": ["instructions", "content", "answers"],
                "min_completion_time": 1,
                "max_completion_time": 30,
                "clarity_score_threshold": 80
            },
            "assessment": {
                "required_components": ["questions", "scoring", "feedback"],
                "min_questions": 5,
                "reliability_threshold": 0.7,
                "validity_threshold": 0.8
            }
        }
    
    def _load_analysis_templates(self) -> Dict[str, str]:
        """Load analysis prompt templates."""
        return {
            "comprehensive": """
            Analyze this {content_type} content for overall quality:
            
            Content: {content}
            Target CEFR Level: {cefr_level}
            
            Evaluate across these dimensions:
            1. **Linguistic Accuracy** (0-100): Grammar, vocabulary, language appropriateness
            2. **Pedagogical Effectiveness** (0-100): Learning design, activity quality, progression
            3. **Cultural Sensitivity** (0-100): Inclusive language, diverse perspectives
            4. **Engagement & Relevance** (0-100): Workplace applicability, motivation
            5. **Technical Quality** (0-100): Formatting, instructions, clarity
            
            For each dimension:
            - Provide specific score with justification
            - Identify specific issues with locations
            - Suggest concrete improvements
            - Assess severity (critical/major/minor)
            
            Return detailed analysis with overall quality score.
            """,
            "issue_focused": """
            Review this content and identify specific quality issues:
            
            {content}
            
            Look for:
            - Grammar and language errors
            - CEFR level misalignment
            - Cultural insensitivity or bias
            - Unclear instructions or activities
            - Missing or inadequate components
            
            For each issue found:
            - Exact location in content
            - Description of the problem
            - Severity level
            - Recommended fix
            """,
            "improvement": """
            Generate improved version of this content addressing these issues:
            
            Original Content: {content}
            Issues to Fix: {issues}
            
            Create improved content that:
            - Resolves all identified issues
            - Maintains pedagogical intent
            - Enhances overall quality
            - Preserves content structure
            
            Document all changes made and justification.
            """
        }
    
    async def analyze_comprehensive_quality(self, content: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """Perform comprehensive quality analysis."""
        
        try:
            content_type = content.get("type", "unknown")
            cefr_level = content.get("cefr_level", "B1")
            
            # Get quality standards for content type
            standards = self.quality_standards.get(content_type, {})
            
            analysis_prompt = self.analysis_templates["comprehensive"].format(
                content_type=content_type,
                content=json.dumps(content, indent=2),
                cefr_level=cefr_level
            )
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert content quality analyst for English language learning materials."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=3000,
                temperature=0.2
            )
            
            # Parse AI response
            ai_analysis = response.choices[0].message.content
            
            # Extract structured data from response
            quality_data = await self._extract_quality_data(ai_analysis, criteria)
            
            # Add technical validation
            technical_validation = await self._validate_technical_requirements(content, standards)
            quality_data["technical_validation"] = technical_validation
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(quality_data, criteria)
            
            return {
                "content_id": content.get("id", "unknown"),
                "analysis_date": datetime.utcnow().isoformat(),
                "overall_score": overall_score,
                "criteria_scores": quality_data.get("criteria_scores", {}),
                "issues_found": quality_data.get("issues", []),
                "recommendations": quality_data.get("recommendations", []),
                "technical_validation": technical_validation,
                "ai_analysis": ai_analysis,
                "approved_for_release": overall_score >= 80
            }
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "approved_for_release": False
            }
    
    async def _extract_quality_data(self, ai_analysis: str, criteria: List[str]) -> Dict[str, Any]:
        """Extract structured data from AI analysis."""
        
        # Use regex patterns to extract scores and issues
        score_pattern = r"(\w+(?:\s+\w+)*)\s*\(0-100\):\s*(\d+)"
        issue_pattern = r"Issue:\s*(.+?)\nLocation:\s*(.+?)\nSeverity:\s*(\w+)"
        
        criteria_scores = {}
        scores = re.findall(score_pattern, ai_analysis)
        for criterion, score in scores:
            criteria_scores[criterion.lower().replace(" ", "_")] = int(score)
        
        issues = []
        issue_matches = re.findall(issue_pattern, ai_analysis, re.DOTALL)
        for description, location, severity in issue_matches:
            issues.append({
                "description": description.strip(),
                "location": location.strip(),
                "severity": severity.lower(),
                "type": "quality_issue"
            })
        
        return {
            "criteria_scores": criteria_scores,
            "issues": issues,
            "recommendations": []  # Extract from AI response if needed
        }
    
    async def _validate_technical_requirements(self, content: Dict[str, Any], standards: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technical requirements against standards."""
        
        validation_results = {
            "passed": True,
            "issues": [],
            "score": 100
        }
        
        # Check required fields
        required_fields = standards.get("required_sections", [])
        for field in required_fields:
            if field not in content or not content[field]:
                validation_results["issues"].append({
                    "type": "missing_field",
                    "description": f"Required field '{field}' is missing or empty",
                    "severity": "critical"
                })
                validation_results["passed"] = False
        
        # Check duration limits
        duration = content.get("duration_minutes", 0)
        max_duration = standards.get("max_duration", 120)
        if duration > max_duration:
            validation_results["issues"].append({
                "type": "duration_exceeded",
                "description": f"Duration {duration} exceeds maximum {max_duration} minutes",
                "severity": "major"
            })
        
        # Check minimum activity count
        activities = content.get("activities", [])
        min_activities = standards.get("min_activities", 1)
        if len(activities) < min_activities:
            validation_results["issues"].append({
                "type": "insufficient_activities",
                "description": f"Only {len(activities)} activities, minimum {min_activities} required",
                "severity": "major"
            })
        
        # Calculate technical score based on issues
        if validation_results["issues"]:
            critical_issues = len([i for i in validation_results["issues"] if i["severity"] == "critical"])
            major_issues = len([i for i in validation_results["issues"] if i["severity"] == "major"])
            validation_results["score"] = max(0, 100 - (critical_issues * 30) - (major_issues * 15))
        
        return validation_results
    
    def _calculate_overall_score(self, quality_data: Dict[str, Any], criteria: List[str]) -> float:
        """Calculate overall quality score from criteria scores."""
        
        criteria_scores = quality_data.get("criteria_scores", {})
        technical_score = quality_data.get("technical_validation", {}).get("score", 100)
        
        # Default weights for criteria
        weights = {
            "linguistic_accuracy": 0.25,
            "pedagogical_effectiveness": 0.25,
            "cultural_sensitivity": 0.20,
            "engagement_relevance": 0.20,
            "technical_quality": 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for criterion in criteria:
            if criterion in criteria_scores:
                weight = weights.get(criterion, 0.1)
                total_score += criteria_scores[criterion] * weight
                total_weight += weight
        
        # Add technical score
        total_score += technical_score * 0.1
        total_weight += 0.1
        
        return round(total_score / total_weight if total_weight > 0 else 0, 1)
    
    async def generate_improvements(self, content: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate improved content addressing identified issues."""
        
        try:
            improvement_prompt = self.analysis_templates["improvement"].format(
                content=json.dumps(content, indent=2),
                issues=json.dumps(issues, indent=2)
            )
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert content improver for English language learning materials."},
                    {"role": "user", "content": improvement_prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse improved content from response
            improved_content_text = response.choices[0].message.content
            
            # Extract improved content (this would need more sophisticated parsing)
            try:
                # Look for JSON in the response
                json_start = improved_content_text.find('{')
                json_end = improved_content_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    improved_content = json.loads(improved_content_text[json_start:json_end])
                else:
                    improved_content = content  # Fallback to original
            except:
                improved_content = content
            
            # Generate change documentation
            changes_made = await self._document_changes(content, improved_content, issues)
            
            # Calculate improvement score
            improvement_score = self._calculate_improvement_score(issues, changes_made)
            
            return {
                "improved_content": improved_content,
                "changes_made": changes_made,
                "improvement_score": improvement_score,
                "justification": "Content improved to address identified quality issues",
                "improved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content improvement failed: {e}")
            return {
                "improved_content": content,
                "changes_made": [],
                "improvement_score": 0,
                "error": str(e)
            }
    
    async def _document_changes(self, original: Dict[str, Any], improved: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Document changes made between original and improved content."""
        
        changes = []
        
        # Compare content sections
        for key in improved.keys():
            if key not in original:
                changes.append({
                    "type": "addition",
                    "section": key,
                    "description": f"Added new section: {key}",
                    "addresses_issue": "missing_content"
                })
            elif original[key] != improved[key]:
                changes.append({
                    "type": "modification",
                    "section": key,
                    "description": f"Modified content in section: {key}",
                    "original": str(original[key])[:100] + "..." if len(str(original[key])) > 100 else str(original[key]),
                    "improved": str(improved[key])[:100] + "..." if len(str(improved[key])) > 100 else str(improved[key])
                })
        
        return changes
    
    def _calculate_improvement_score(self, issues: List[Dict[str, Any]], changes: List[Dict[str, Any]]) -> float:
        """Calculate improvement score based on issues addressed."""
        
        if not issues:
            return 0
        
        # Weight by severity
        issue_weights = {"critical": 3, "major": 2, "minor": 1}
        total_issue_weight = sum(issue_weights.get(issue.get("severity", "minor"), 1) for issue in issues)
        
        # Assume each change addresses issues proportionally
        addressed_weight = len(changes) * (total_issue_weight / len(issues)) if issues else 0
        
        improvement_percentage = min(100, (addressed_weight / total_issue_weight) * 100) if total_issue_weight > 0 else 0
        
        return round(improvement_percentage, 1)

class CEFRLevelValidator:
    """Validates content alignment with CEFR levels."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cefr_descriptors = self._load_cefr_descriptors()
    
    def _load_cefr_descriptors(self) -> Dict[str, Dict[str, Any]]:
        """Load detailed CEFR level descriptors."""
        return {
            "A1": {
                "vocabulary": "Basic everyday expressions, very basic phrases",
                "grammar": "Simple present, basic word order, limited vocabulary",
                "complexity": "Very simple sentences, concrete and immediate topics",
                "skills": "Understand familiar words, simple phrases with help"
            },
            "A2": {
                "vocabulary": "Frequently used expressions, basic personal information",
                "grammar": "Simple past, future with going to, basic comparisons",
                "complexity": "Simple compound sentences, routine matters",
                "skills": "Direct exchange of information on familiar topics"
            },
            "B1": {
                "vocabulary": "Main points on familiar work, school, leisure topics",
                "grammar": "Present perfect, conditionals, passive voice basics",
                "complexity": "Connected text on familiar topics, personal experiences",
                "skills": "Deal with most situations, describe experiences and events"
            },
            "B2": {
                "vocabulary": "Complex text on concrete and abstract topics",
                "grammar": "Advanced conditionals, reported speech, complex structures",
                "complexity": "Clear detailed text on wide range of subjects",
                "skills": "Interact with fluency, argue viewpoint on topical issues"
            },
            "C1": {
                "vocabulary": "Wide range of demanding, longer texts, implicit meaning",
                "grammar": "Full range of structures used accurately and flexibly",
                "complexity": "Well-structured, detailed text on complex subjects",
                "skills": "Express fluently without obvious searching for expressions"
            },
            "C2": {
                "vocabulary": "Virtually everything heard or read with ease",
                "grammar": "All structures used naturally and accurately",
                "complexity": "Coherent, cohesive discourse appropriate to context",
                "skills": "Express precisely, distinguishing finer shades of meaning"
            }
        }
    
    async def validate_level_alignment(self, content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
        """Validate content alignment with target CEFR level."""
        
        try:
            level_descriptors = self.cefr_descriptors.get(target_level, {})
            
            validation_prompt = f"""
            Validate if this content is appropriate for CEFR {target_level} level:
            
            Content: {json.dumps(content, indent=2)}
            
            CEFR {target_level} Characteristics:
            - Vocabulary: {level_descriptors.get('vocabulary', 'N/A')}
            - Grammar: {level_descriptors.get('grammar', 'N/A')}
            - Complexity: {level_descriptors.get('complexity', 'N/A')}
            - Skills: {level_descriptors.get('skills', 'N/A')}
            
            Analyze:
            1. **Vocabulary Appropriateness**: Are vocabulary items suitable for {target_level}?
            2. **Grammar Complexity**: Do grammar structures match {target_level} expectations?
            3. **Task Complexity**: Are activities appropriate for this proficiency level?
            4. **Language Demands**: Is the language input/output suitable?
            
            For each misalignment:
            - Specify the exact issue
            - Suggest appropriate level
            - Recommend adjustments
            
            Return validation score (0-100) and specific recommendations.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a CEFR expert specializing in content level validation."},
                    {"role": "user", "content": validation_prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            validation_analysis = response.choices[0].message.content
            
            # Extract validation data
            validation_data = await self._extract_validation_data(validation_analysis, target_level)
            
            return {
                "target_level": target_level,
                "alignment_score": validation_data.get("score", 0),
                "is_aligned": validation_data.get("score", 0) >= 80,
                "misalignments": validation_data.get("issues", []),
                "recommendations": validation_data.get("recommendations", []),
                "analysis": validation_analysis,
                "validated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CEFR validation failed: {e}")
            return {
                "target_level": target_level,
                "alignment_score": 0,
                "is_aligned": False,
                "error": str(e)
            }
    
    async def _extract_validation_data(self, analysis: str, target_level: str) -> Dict[str, Any]:
        """Extract structured validation data from AI analysis."""
        
        # Extract score using regex
        score_match = re.search(r"validation score.*?(\d+)", analysis.lower())
        score = int(score_match.group(1)) if score_match else 75
        
        # Extract issues
        issues = []
        if "too simple" in analysis.lower() or "below level" in analysis.lower():
            issues.append({
                "type": "content_too_simple",
                "description": "Content appears below target CEFR level",
                "severity": "major"
            })
        elif "too complex" in analysis.lower() or "above level" in analysis.lower():
            issues.append({
                "type": "content_too_complex", 
                "description": "Content appears above target CEFR level",
                "severity": "major"
            })
        
        return {
            "score": score,
            "issues": issues,
            "recommendations": []
        }

class GrammarChecker:
    """Comprehensive grammar and linguistic accuracy checker."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Try to load spaCy model, fallback if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not available, using AI-only grammar checking")
            self.nlp = None
    
    async def comprehensive_grammar_check(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive grammar and language checking."""
        
        try:
            # Extract text content from various fields
            text_content = self._extract_text_content(content)
            
            # AI-based grammar checking
            ai_results = await self._ai_grammar_check(text_content)
            
            # Rule-based checking if spaCy is available
            rule_results = self._rule_based_check(text_content) if self.nlp else {}
            
            # Combine results
            combined_results = self._combine_grammar_results(ai_results, rule_results)
            
            return {
                "content_checked": len(text_content),
                "grammar_score": combined_results.get("score", 100),
                "issues_found": combined_results.get("issues", []),
                "suggestions": combined_results.get("suggestions", []),
                "check_date": datetime.utcnow().isoformat(),
                "accuracy_level": self._determine_accuracy_level(combined_results.get("score", 100))
            }
            
        except Exception as e:
            logger.error(f"Grammar check failed: {e}")
            return {
                "content_checked": 0,
                "grammar_score": 0,
                "error": str(e)
            }
    
    def _extract_text_content(self, content: Dict[str, Any]) -> List[str]:
        """Extract text content from content structure."""
        
        text_pieces = []
        
        # Common text fields to check
        text_fields = [
            "title", "description", "instructions", "content",
            "text", "question", "answer", "feedback"
        ]
        
        def extract_recursive(obj, parent_key=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in text_fields and isinstance(value, str):
                        text_pieces.append(value)
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, key)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, str) and parent_key in text_fields:
                        text_pieces.append(item)
                    elif isinstance(item, (dict, list)):
                        extract_recursive(item, parent_key)
        
        extract_recursive(content)
        return text_pieces
    
    async def _ai_grammar_check(self, text_content: List[str]) -> Dict[str, Any]:
        """Use AI for grammar checking."""
        
        if not text_content:
            return {"score": 100, "issues": [], "suggestions": []}
        
        combined_text = "\n\n".join(text_content)
        
        grammar_prompt = f"""
        Check this text for grammar, spelling, and language accuracy issues:
        
        {combined_text}
        
        Identify:
        1. Grammar errors (subject-verb agreement, tense consistency, etc.)
        2. Spelling mistakes
        3. Punctuation errors
        4. Word choice issues
        5. Sentence structure problems
        
        For each issue:
        - Exact location/sentence
        - Type of error
        - Correction suggestion
        - Severity (critical/major/minor)
        
        Provide overall accuracy score (0-100).
        """
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert grammar checker and language accuracy analyst."},
                    {"role": "user", "content": grammar_prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            grammar_analysis = response.choices[0].message.content
            
            # Extract issues and score
            issues = self._parse_grammar_issues(grammar_analysis)
            score = self._extract_grammar_score(grammar_analysis)
            
            return {
                "score": score,
                "issues": issues,
                "suggestions": [],
                "ai_analysis": grammar_analysis
            }
            
        except Exception as e:
            logger.error(f"AI grammar check failed: {e}")
            return {"score": 100, "issues": [], "error": str(e)}
    
    def _rule_based_check(self, text_content: List[str]) -> Dict[str, Any]:
        """Rule-based grammar checking using spaCy."""
        
        if not self.nlp:
            return {}
        
        issues = []
        
        for text in text_content:
            doc = self.nlp(text)
            
            # Check for common issues
            for token in doc:
                # Check spelling (simplified)
                if token.is_alpha and not token.is_stop and token.is_oov:
                    issues.append({
                        "type": "potential_spelling",
                        "text": token.text,
                        "location": f"Token: {token.text}",
                        "severity": "minor"
                    })
        
        # Calculate score based on issues found
        score = max(0, 100 - len(issues) * 5)
        
        return {
            "score": score,
            "issues": issues
        }
    
    def _combine_grammar_results(self, ai_results: Dict[str, Any], rule_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine AI and rule-based results."""
        
        # Use AI results as primary, supplement with rule-based
        combined_issues = ai_results.get("issues", [])
        if rule_results:
            combined_issues.extend(rule_results.get("issues", []))
        
        # Average scores if both available
        ai_score = ai_results.get("score", 100)
        rule_score = rule_results.get("score", ai_score)
        combined_score = (ai_score + rule_score) / 2 if rule_results else ai_score
        
        return {
            "score": round(combined_score, 1),
            "issues": combined_issues,
            "suggestions": ai_results.get("suggestions", [])
        }
    
    def _parse_grammar_issues(self, analysis: str) -> List[Dict[str, Any]]:
        """Parse grammar issues from AI analysis."""
        
        issues = []
        
        # Simple pattern matching for issues
        error_patterns = [
            r"Error:\s*(.+?)\nLocation:\s*(.+?)\nCorrection:\s*(.+?)\n",
            r"Issue:\s*(.+?)\nSentence:\s*(.+?)\nFix:\s*(.+?)\n"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, analysis, re.DOTALL)
            for match in matches:
                issues.append({
                    "type": "grammar_error",
                    "description": match[0].strip(),
                    "location": match[1].strip(),
                    "suggestion": match[2].strip(),
                    "severity": "major"
                })
        
        return issues
    
    def _extract_grammar_score(self, analysis: str) -> int:
        """Extract grammar score from analysis."""
        
        score_patterns = [
            r"accuracy score.*?(\d+)",
            r"overall score.*?(\d+)",
            r"grammar score.*?(\d+)"
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, analysis.lower())
            if match:
                return int(match.group(1))
        
        # Default score if no issues mentioned
        return 95 if "no issues" in analysis.lower() or "no errors" in analysis.lower() else 85
    
    def _determine_accuracy_level(self, score: float) -> str:
        """Determine accuracy level based on score."""
        
        if score >= 95:
            return "excellent"
        elif score >= 85:
            return "good"
        elif score >= 75:
            return "acceptable"
        else:
            return "needs_improvement"

class CulturalSensitivityChecker:
    """Analyzes content for cultural sensitivity and inclusivity."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sensitivity_guidelines = self._load_sensitivity_guidelines()
    
    def _load_sensitivity_guidelines(self) -> Dict[str, List[str]]:
        """Load cultural sensitivity guidelines."""
        return {
            "inclusive_language": [
                "Use gender-neutral language where appropriate",
                "Avoid assumptions about family structures",
                "Include diverse names and backgrounds",
                "Respect religious and cultural differences"
            ],
            "avoid_stereotypes": [
                "Don't generalize about cultures or nationalities",
                "Avoid occupational or gender stereotypes",
                "Present diverse role models",
                "Consider global perspectives"
            ],
            "accessibility": [
                "Consider learners with different abilities",
                "Provide alternative formats when needed",
                "Use clear, simple language in instructions",
                "Avoid cultural references that may exclude"
            ]
        }
    
    async def analyze_cultural_appropriateness(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for cultural sensitivity issues."""
        
        try:
            # Extract text for analysis
            text_content = self._extract_text_for_cultural_analysis(content)
            
            cultural_prompt = f"""
            Analyze this content for cultural sensitivity and inclusivity:
            
            Content: {json.dumps(content, indent=2)}
            
            Text Content: {' '.join(text_content)}
            
            Check for:
            1. **Inclusive Language**: Gender-neutral language, diverse representation
            2. **Cultural Stereotypes**: Generalizations, biased assumptions
            3. **Global Accessibility**: Universal relevance, cultural barriers
            4. **Diverse Representation**: Names, scenarios, perspectives
            5. **Religious/Cultural Sensitivity**: Respectful treatment of beliefs
            
            Guidelines:
            {json.dumps(self.sensitivity_guidelines, indent=2)}
            
            For each issue:
            - Specific problematic content
            - Type of sensitivity issue
            - Potential impact
            - Improvement suggestion
            
            Provide cultural sensitivity score (0-100).
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in cultural sensitivity and inclusive content design."},
                    {"role": "user", "content": cultural_prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            cultural_analysis = response.choices[0].message.content
            
            # Parse results
            sensitivity_data = self._parse_cultural_analysis(cultural_analysis)
            
            return {
                "sensitivity_score": sensitivity_data.get("score", 90),
                "is_culturally_appropriate": sensitivity_data.get("score", 90) >= 80,
                "issues_found": sensitivity_data.get("issues", []),
                "recommendations": sensitivity_data.get("recommendations", []),
                "analysis": cultural_analysis,
                "checked_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cultural sensitivity check failed: {e}")
            return {
                "sensitivity_score": 0,
                "is_culturally_appropriate": False,
                "error": str(e)
            }
    
    def _extract_text_for_cultural_analysis(self, content: Dict[str, Any]) -> List[str]:
        """Extract text content for cultural analysis."""
        
        text_pieces = []
        
        def extract_text(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        text_pieces.append(value)
                    elif isinstance(value, (dict, list)):
                        extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(content)
        return text_pieces
    
    def _parse_cultural_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse cultural sensitivity analysis results."""
        
        # Extract sensitivity score
        score_match = re.search(r"sensitivity score.*?(\d+)", analysis.lower())
        score = int(score_match.group(1)) if score_match else 90
        
        # Extract issues
        issues = []
        if "stereotype" in analysis.lower():
            issues.append({
                "type": "cultural_stereotype",
                "description": "Potential cultural stereotyping detected",
                "severity": "major"
            })
        
        if "bias" in analysis.lower() or "exclusionary" in analysis.lower():
            issues.append({
                "type": "cultural_bias",
                "description": "Potential cultural bias or exclusionary content",
                "severity": "major"
            })
        
        return {
            "score": score,
            "issues": issues,
            "recommendations": []
        }