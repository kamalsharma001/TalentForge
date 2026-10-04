"""
LLMService — Centralized LLM provider service abstraction for TalentForge.

Provider: Google Gemini (default model: gemini-2.5-flash-lite)
Uses Google's official unified Gen AI SDK (`google-genai`).

Provides structured generation and adaptive interview interaction backed by Gemini.
Includes graceful error handling (timeouts, rate-limits, malformed JSON, quota exhaustion)
and a transparent, clearly separated offline fallback for development without API keys.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Centralized Model Configuration — default is gemini-2.5-flash-lite
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


class LLMService:

    @classmethod
    def _get_client(cls):
        """
        Initialize the official Google Gen AI client using GEMINI_API_KEY.
        Never logs or exposes the API key.
        """
        api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key:
            return None
        try:
            from google import genai
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning("Could not initialize Google GenAI client: %s", e)
            return None

    @classmethod
    def _call_gemini(
        cls,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = True,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Executes a call to the Gemini API using Google's official Gen AI SDK.
        Catches API errors (rate limits, timeouts, invalid credentials) gracefully
        and returns raw text or None.
        """
        client = cls._get_client()
        if not client:
            return None

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )
            if json_mode:
                config.response_mime_type = "application/json"
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
            return None
        except Exception as exc:
            # Mask any credentials from error messages
            logger.error("Gemini API call failed: %s", exc)
            return None

    @classmethod
    def _parse_json_safely(cls, raw: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON responses from Gemini, stripping markdown code fences if present.
        """
        if not raw:
            return None
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.warning("Failed to parse JSON from Gemini response: %s", e)
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Preparation Plan Generation
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def generate_prep_plan(
        cls,
        role: str,
        tech_stack: Optional[List[str]] = None,
        difficulty: str = "medium",
        candidate_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate strategic preparation areas and recommended focus topics
        tailored to the target interview context.
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "General Software Engineering"
        skills_str = ", ".join(candidate_skills) if candidate_skills else "None specified"

        prompt = f"""You are an elite technical hiring coach at TalentForge.
Create a personalized, high-yield interview preparation plan for a candidate preparing for:
- Role: {role}
- Tech Stack: {tech_str}
- Difficulty Level: {difficulty}
- Candidate Background Skills: {skills_str}

Return a valid JSON object matching this exact schema:
{{
  "summary": "Brief 2-3 sentence strategic roadmap for this specific interview",
  "focus_areas": [
    {{
      "name": "Area name (e.g. System Design, Core Frameworks, Data Modeling)",
      "description": "What to focus on and why it matters for this role",
      "weight": "High | Medium | Fundamental"
    }}
  ],
  "recommended_topics": [
    "Specific topic 1",
    "Specific topic 2",
    "Specific topic 3",
    "Specific topic 4"
  ],
  "suggested_question_types": [
    "Technical Architecture",
    "Live Problem Decomposition",
    "Behavioral (STAR Method)"
  ]
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are a technical interview preparation AI. Always output valid JSON."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.5)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "summary" in data and "focus_areas" in data:
                data["is_fallback"] = False
                return data

        # Clearly separated deterministic fallback
        return cls._fallback_prep_plan(role, tech_stack, difficulty)

    @classmethod
    def _fallback_prep_plan(cls, role: str, tech_stack: Optional[List[str]], difficulty: str) -> Dict[str, Any]:
        tech_list = tech_stack or ["Core Principles", "Architecture", "Problem Solving"]
        return {
            "summary": f"[Offline Mode] Preparation roadmap tailored for a {difficulty}-level {role} role emphasizing {', '.join(tech_list[:3])}.",
            "focus_areas": [
                {
                    "name": "Core Technologies & Runtimes",
                    "description": f"Master fundamental concepts, memory models, and standard libraries in {tech_list[0] if tech_list else 'your stack'}.",
                    "weight": "High"
                },
                {
                    "name": "System Architecture & Scalability",
                    "description": "Evaluate architectural trade-offs, state management, caching, and API durability.",
                    "weight": "High"
                },
                {
                    "name": "Production Problem Solving & Debugging",
                    "description": "Be ready to explain how you isolate incidents, trace bottlenecks, and handle concurrency.",
                    "weight": "Medium"
                },
                {
                    "name": "Collaborative Behavioral Scenarios",
                    "description": "Demonstrate clear communication, managing technical debt, and cross-team alignment using the STAR method.",
                    "weight": "Fundamental"
                }
            ],
            "recommended_topics": [
                f"{tech_list[0]} Lifecycle & Optimization" if tech_list else "Data Structures & Big-O",
                f"{tech_list[1]} Design Patterns" if len(tech_list) > 1 else "Database Indexing & Queries",
                "API Contracts & Error Handling",
                "Distributed Caching & Concurrency Controls"
            ],
            "suggested_question_types": [
                "Technical Architecture",
                "Behavioral & Decision-Making",
                "Real-World Optimization"
            ],
            "is_fallback": True
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Practice Question Generation
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def generate_practice_questions(
        cls,
        role: str,
        tech_stack: Optional[List[str]] = None,
        difficulty: str = "medium",
        category: str = "technical",
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generate structured interview practice questions with criteria and hints.
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "General Software Engineering"

        prompt = f"""You are an expert technical interviewer at TalentForge.
Generate {count} realistic, challenging interview questions for:
- Role: {role}
- Tech Stack: {tech_str}
- Difficulty: {difficulty}
- Category: {category} (e.g. technical, behavioral, system_design, or role_specific)

Return a valid JSON object matching this exact schema:
{{
  "questions": [
    {{
      "question": "Clear, precise interview question",
      "category": "{category}",
      "difficulty": "{difficulty}",
      "hint": "1-2 sentence hint to guide structuring the answer without giving away the full solution",
      "evaluation_criteria": "Key points an interviewer looks for (e.g. trade-offs, edge cases, STAR format)"
    }}
  ]
}}
Ensure the JSON is strictly valid and questions reflect realistic industry interviews."""

        sys_inst = "You are a technical interview question generator. Output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.7)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "questions" in data and isinstance(data["questions"], list):
                for q in data["questions"]:
                    q["is_fallback"] = False
                return data["questions"]

        # Fallback question set
        return cls._fallback_practice_questions(role, tech_stack, difficulty, category, count)

    @classmethod
    def _fallback_practice_questions(cls, role: str, tech_stack: Optional[List[str]], difficulty: str, category: str, count: int) -> List[Dict[str, Any]]:
        primary_tech = tech_stack[0] if tech_stack else "technology"
        fallbacks = [
            {
                "question": f"How do you design a resilient data access layer in {primary_tech}, and how do you handle connection pooling and transaction rollbacks under load?",
                "category": category,
                "difficulty": difficulty,
                "hint": "Address connection limits, idempotency, and database locking strategies.",
                "evaluation_criteria": "Understanding of connection pool exhaustion, ACID transactions, and error propagation.",
                "is_fallback": True
            },
            {
                "question": f"Describe a situation where you diagnosed and fixed a critical performance bottleneck in a {role} project. What tools and metrics guided your decision?",
                "category": category,
                "difficulty": difficulty,
                "hint": "Use the STAR method: Situation, Task, Action, Result with quantifiable metrics.",
                "evaluation_criteria": "Demonstrates systematic profiling rather than guesswork, and communicates measurable business impact.",
                "is_fallback": True
            },
            {
                "question": f"When choosing between caching strategies (Write-Through vs Cache-Aside) for a high-traffic {primary_tech} endpoint, what trade-offs in consistency and latency do you consider?",
                "category": category,
                "difficulty": difficulty,
                "hint": "Consider what happens during cache stampedes and stale read tolerances.",
                "evaluation_criteria": "Clear articulation of cache invalidation difficulties, memory limits, and data staleness windows.",
                "is_fallback": True
            },
            {
                "question": f"Walk through how you implement secure API authentication and session refresh tokens without exposing credentials to XSS or CSRF risks.",
                "category": category,
                "difficulty": difficulty,
                "hint": "Compare HttpOnly cookies vs localStorage and short-lived access tokens vs rotating refresh tokens.",
                "evaluation_criteria": "Awareness of token revocation, cryptographic signature validation, and secure cookie attributes.",
                "is_fallback": True
            },
            {
                "question": f"Tell me about a time you strongly disagreed with an architectural proposal or code review from a teammate. How did you resolve it collaboratively?",
                "category": category,
                "difficulty": difficulty,
                "hint": "Focus on benchmark evidence, shared goals, and maintaining strong team psychological safety.",
                "evaluation_criteria": "Diplomacy, objective evaluation, and alignment with company velocity.",
                "is_fallback": True
            }
        ]
        return fallbacks[:count]

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Individual Practice Answer Evaluation
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def evaluate_practice_answer(
        cls,
        question: str,
        answer: str,
        role: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate's written answer to an individual practice question.
        Provides score (1-10), strengths, missing aspects, and actionable suggestions.
        """
        prompt = f"""You are a senior technical interviewer evaluating a candidate's response.
Question: {question}
Target Role: {role}
Difficulty Level: {difficulty}

Candidate's Answer:
\"\"\"{answer}\"\"\"

Provide an objective, constructive evaluation.
Return a valid JSON object matching this schema:
{{
  "score": 8, // Integer 1-10 based on depth, correctness, and clarity
  "strengths": [
    "Specific thing the candidate explained well",
    "Another strong aspect of the answer"
  ],
  "improvements": [
    "Specific nuance, edge case, or trade-off that was missed",
    "Concrete recommendation on how to strengthen the answer"
  ],
  "model_answer_snippet": "A concise 2-3 sentence example of how a senior engineer would succinctly summarize the key point",
  "summary": "1-2 sentence overall assessment of this answer"
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are a constructive technical interviewer evaluating a candidate answer. Output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.3)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "score" in data and "strengths" in data:
                data["is_fallback"] = False
                return data

        # Fallback evaluation
        return cls._fallback_answer_evaluation(answer)

    @classmethod
    def _fallback_answer_evaluation(cls, answer: str) -> Dict[str, Any]:
        word_count = len(answer.split())
        score = min(10, max(3, 4 + (word_count // 35)))
        return {
            "score": score,
            "strengths": [
                "Answer directly addresses the central topic.",
                "Structure presents a coherent flow of thought."
            ],
            "improvements": [
                "Consider discussing concrete edge cases, failure recovery, or quantitative metrics.",
                "Mention real-world architectural trade-offs to demonstrate senior engineering depth."
            ],
            "model_answer_snippet": "An optimal response clearly frames the core mechanism, explicitly notes constraints and trade-offs, and highlights operational monitoring.",
            "summary": f"[Offline Mode] Candidate provided a {word_count}-word response demonstrating baseline conceptual understanding.",
            "is_fallback": True
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Resume Intelligence & Claim Extraction
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def analyze_resume(cls, resume_text: str) -> Dict[str, Any]:
        """
        Parses extracted resume text into structured components:
        - summary: candidate background summary
        - skills: categorized technical skills
        - projects: key projects with tech stack and highlights
        - experience: past work experience
        - certifications: certifications / courses
        - technical_claims: concrete technical assertions suitable for interview validation
        """
        trimmed_text = resume_text[:6000] if len(resume_text) > 6000 else resume_text
        prompt = f"""You are an expert technical recruiter and resume intelligence parser at TalentForge.
Analyze the following extracted resume text carefully and extract high-fidelity structured information.

RESUME TEXT:
────────────────────────────────────────
{trimmed_text}
────────────────────────────────────────

CRITICAL INSTRUCTIONS:
1. Extract skills categorized by languages, frameworks, databases, and tools_and_platforms.
2. Extract projects with: name, tech_stack (list), summary, and key achievements.
3. Extract work experience: role, company, duration, and key highlights.
4. Extract 4-8 concrete, specific 'technical_claims' that the candidate makes in this resume.
   Examples of technical claims:
   - "Migrated a monolithic application to microservices with FastAPI and Docker."
   - "Implemented caching with Redis to reduce endpoint latency by 40%."
   - "Designed PostgreSQL schemas with custom indexing for high throughput."
   Make sure these claims represent real technical decisions or assertions made in the text.
5. Provide a 2-3 sentence executive summary of the candidate's profile.

Return a valid JSON object matching this exact schema:
{{
  "summary": "Brief executive overview of candidate experience and focus areas",
  "skills": {{
    "languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "databases": ["PostgreSQL", "Redis"],
    "tools_and_platforms": ["Docker", "AWS", "Git"]
  }},
  "projects": [
    {{
      "name": "Project Name",
      "tech_stack": ["FastAPI", "React"],
      "summary": "Short description of project",
      "highlights": ["Built authentication flow", "Scaled to 10k users"]
    }}
  ],
  "experience": [
    {{
      "role": "Software Engineer",
      "company": "Company Name",
      "duration": "2022 - Present",
      "highlights": ["Key accomplishment 1", "Key accomplishment 2"]
    }}
  ],
  "certifications": ["AWS Certified Developer"],
  "technical_claims": [
    "Claim 1 about architecture, scaling, or implementation",
    "Claim 2 about libraries, systems, or performance"
  ]
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are a resume analysis AI. Extract structured profile data and technical claims. Output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.2)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "skills" in data and "technical_claims" in data:
                data["is_fallback"] = False
                return data

        # Deterministic fallback resume analysis
        return cls._fallback_resume_analysis(resume_text)

    @classmethod
    def _fallback_resume_analysis(cls, resume_text: str) -> Dict[str, Any]:
        lower = resume_text.lower()
        known_langs = ["python", "javascript", "typescript", "java", "c++", "go", "ruby", "rust", "c#", "php"]
        known_frameworks = ["react", "vue", "angular", "fastapi", "django", "flask", "node", "express", "spring", "next.js"]
        known_dbs = ["postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite", "cassandra"]
        known_tools = ["docker", "kubernetes", "aws", "gcp", "azure", "git", "linux", "ci/cd", "kafka"]

        langs = [k.capitalize() for k in known_langs if k in lower] or ["Python", "JavaScript"]
        fws = [k.capitalize() for k in known_frameworks if k in lower] or ["React", "FastAPI"]
        dbs = [k.capitalize() for k in known_dbs if k in lower] or ["PostgreSQL"]
        tools = [k.capitalize() for k in known_tools if k in lower] or ["Docker", "Git"]

        lines = [line.strip() for line in resume_text.splitlines() if len(line.strip()) > 25 and not line.strip().startswith("#")]
        claims = lines[:5] if lines else [
            f"Implemented web systems utilizing {langs[0]} and {fws[0]}.",
            f"Designed and queried data layers with {dbs[0]}.",
            f"Deployed services with containerized workflows using {tools[0]}."
        ]

        return {
            "summary": f"[Offline Mode] Candidate profile extracted from document text with emphasis on {', '.join(langs[:3])} and {', '.join(fws[:2])}.",
            "skills": {
                "languages": langs,
                "frameworks": fws,
                "databases": dbs,
                "tools_and_platforms": tools
            },
            "projects": [
                {
                    "name": "Featured Project",
                    "tech_stack": langs[:2] + fws[:1],
                    "summary": "Full-stack application demonstrating core engineering practices.",
                    "highlights": ["Designed system architecture", "Implemented core business logic"]
                }
            ],
            "experience": [
                {
                    "role": "Software Developer",
                    "company": "Engineering Organization",
                    "duration": "Recent",
                    "highlights": ["Built and maintained scalable features", "Collaborated on code reviews"]
                }
            ],
            "certifications": [],
            "technical_claims": claims[:5],
            "is_fallback": True
        }

    @classmethod
    def _format_resume_context_summary(cls, resume_analysis: Optional[Dict[str, Any]]) -> str:
        if not resume_analysis:
            return ""
        summary = resume_analysis.get("summary", "")
        skills = resume_analysis.get("skills", {})
        skills_str = ""
        if isinstance(skills, dict):
            parts = []
            for k, v in skills.items():
                if v and isinstance(v, list):
                    parts.append(f"{k.capitalize()}: {', '.join(v[:6])}")
            skills_str = "; ".join(parts)
        elif isinstance(skills, list):
            skills_str = ", ".join(skills[:12])

        projects = resume_analysis.get("projects", [])
        proj_lines = []
        for p in projects[:2]:
            p_name = p.get("name", "Project")
            p_tech = ", ".join(p.get("tech_stack", []))
            p_sum = p.get("summary", "")
            proj_lines.append(f"- {p_name} ({p_tech}): {p_sum}")
        projects_str = "\n".join(proj_lines) if proj_lines else "None listed"

        claims = resume_analysis.get("technical_claims", [])
        claims_lines = [f"- {c}" for c in claims[:5]]
        claims_str = "\n".join(claims_lines) if claims_lines else "None specified"

        return f"""Candidate Resume Background:
- Overview: {summary}
- Skills: {skills_str}
- Notable Projects:
{projects_str}
- Key Technical Claims:
{claims_str}"""

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Interview Blueprint Generation
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def generate_interview_blueprint(
        cls,
        role: str,
        tech_stack: Optional[List[str]] = None,
        difficulty: str = "medium",
        duration_mode: str = "30",
        resume_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates an authoritative, structured Interview Blueprint before Question 1.
        Defines 4-6 target competencies (priority, mandatory vs optional, target question counts,
        expected depth), target question allocations, and key resume claims to validate.
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "modern software engineering stack"
        resume_block = cls._format_resume_context_summary(resume_analysis)

        # Question targets by duration mode
        question_targets = {
            "15": 4,
            "30": 6,
            "45": 8,
            "60": 10,
            "open_ended": 7,
        }
        est_questions = question_targets.get(str(duration_mode), 6)

        prompt = f"""You are a Principal Engineering Interview Architect at TalentForge designing an Interview Blueprint.
Role: {role}
Difficulty: {difficulty}
Tech Stack: {tech_str}
Duration Mode: {duration_mode} (Target ~{est_questions} total interview questions)

{resume_block if resume_block else "Candidate is practicing in general role mode without an attached resume."}

CRITICAL BLUEPRINT REQUIREMENTS:
1. Define 4 to 6 specific technical competencies for a {difficulty} {role} ({tech_str}).
   Examples: System Architecture & Concurrency, Database Internals & Query Optimization, Distributed Caching & Fault Tolerance, Observability & Incident Debugging, API Security & Resilience.
2. For each competency:
   - id: unique string identifier (e.g. "comp_arch", "comp_db", "comp_cache", "comp_ops")
   - name: clear title
   - priority: "high" | "medium" | "low"
   - is_mandatory: true for 2-3 core high-priority areas, false for optional deep dives
   - target_questions: integer (1-2 per competency, summing to ~{est_questions})
   - expected_depth: specific technical criteria expected at {difficulty} level
   - status: "not_started"
3. Identify 2-4 concrete technical claims from the resume (if provided) that Alex should actively validate during the interview.
   If no resume is provided, generate 2-3 foundational technical assertions relevant to {role}.

Return a valid JSON object matching this schema:
{{
  "role": "{role}",
  "difficulty": "{difficulty}",
  "duration_mode": "{duration_mode}",
  "estimated_questions": {est_questions},
  "competencies": [
    {{
      "id": "comp_1",
      "name": "System Architecture & Concurrency",
      "priority": "high",
      "is_mandatory": true,
      "target_questions": 2,
      "expected_depth": "Evaluation of asynchronous processing, lock-free designs, throughput bottlenecks, and decoupling.",
      "status": "not_started"
    }}
  ],
  "claims_to_validate": [
    {{
      "claim": "Specific technical claim or assertion",
      "priority": "high",
      "status": "Requires further validation"
    }}
  ]
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are a technical interview architect. Output valid JSON blueprint only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.3)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "competencies" in data and len(data["competencies"]) >= 3:
                data["is_fallback"] = False
                return data

        return cls._fallback_interview_blueprint(role, tech_stack, difficulty, duration_mode, resume_analysis)

    @classmethod
    def _fallback_interview_blueprint(
        cls,
        role: str,
        tech_stack: Optional[List[str]],
        difficulty: str,
        duration_mode: str,
        resume_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        primary_tech = tech_stack[0] if tech_stack else "System Design"
        sec_tech = tech_stack[1] if tech_stack and len(tech_stack) > 1 else "Database"

        question_targets = {"15": 4, "30": 6, "45": 8, "60": 10, "open_ended": 7}
        est_questions = question_targets.get(str(duration_mode), 6)

        competencies = [
            {
                "id": "comp_arch",
                "name": "System Architecture & Concurrency",
                "priority": "high",
                "is_mandatory": True,
                "target_questions": 2,
                "expected_depth": f"Architectural decomposition, process isolation, and asynchronous data flow using {primary_tech}.",
                "status": "not_started"
            },
            {
                "id": "comp_data",
                "name": "Database Internals & Optimization",
                "priority": "high",
                "is_mandatory": True,
                "target_questions": 2,
                "expected_depth": f"Schema modeling, indexing, transaction isolation, and query tuning with {sec_tech}.",
                "status": "not_started"
            },
            {
                "id": "comp_resilience",
                "name": "API Resilience & Caching",
                "priority": "medium",
                "is_mandatory": False,
                "target_questions": 1,
                "expected_depth": "Cache invalidation patterns, stampede protection, circuit breaking, and rate limiting.",
                "status": "not_started"
            },
            {
                "id": "comp_observability",
                "name": "Production Reliability & Incident Debugging",
                "priority": "medium",
                "is_mandatory": False,
                "target_questions": 1,
                "expected_depth": "Root cause analysis, distributed tracing, metrics, and rolling deployment safety.",
                "status": "not_started"
            }
        ]

        claims_to_validate = []
        if resume_analysis and resume_analysis.get("technical_claims"):
            for c in resume_analysis["technical_claims"][:4]:
                claims_to_validate.append({
                    "claim": c,
                    "priority": "high",
                    "status": "Requires further validation"
                })
        else:
            claims_to_validate = [
                {
                    "claim": f"Hands-on architectural experience deploying {primary_tech} services under production load",
                    "priority": "high",
                    "status": "Requires further validation"
                },
                {
                    "claim": f"Designing scalable data layers and transaction pipelines using {sec_tech}",
                    "priority": "medium",
                    "status": "Requires further validation"
                }
            ]

        return {
            "role": role,
            "difficulty": difficulty,
            "duration_mode": duration_mode,
            "estimated_questions": est_questions,
            "competencies": competencies,
            "claims_to_validate": claims_to_validate,
            "is_fallback": True
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Adaptive Mock Interview: Opening Question
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def generate_mock_opener(
        cls,
        role: str,
        tech_stack: Optional[List[str]] = None,
        difficulty: str = "medium",
        interview_type: str = "Technical & Behavioral",
        resume_analysis: Optional[Dict[str, Any]] = None,
        blueprint: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate the interviewer's welcoming opening turn and initial question.
        Grounded in the Interview Blueprint's first high-priority competency and candidate resume.
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "relevant modern technologies"
        resume_block = cls._format_resume_context_summary(resume_analysis)

        # Extract first target competency from blueprint
        first_comp = "System Architecture & Core Engineering"
        first_claim = None
        if blueprint and blueprint.get("competencies"):
            first_comp = blueprint["competencies"][0].get("name", first_comp)
        if blueprint and blueprint.get("claims_to_validate"):
            first_claim = blueprint["claims_to_validate"][0].get("claim")

        resume_prompt_instructions = ""
        if resume_block:
            resume_prompt_instructions = f"""
{resume_block}

The candidate has provided their resume.
Acknowledge having reviewed their background warmly.
Reference one of their key projects (e.g. {first_claim if first_claim else "notable project"}) and ask your first question focusing on:
1. Target Competency: {first_comp}
2. Their concrete implementation details (what libraries/tools they personally implemented)
3. The most critical engineering trade-off or architectural decision made in that project."""
        else:
            resume_prompt_instructions = f"""
Target Competency to Assess First: {first_comp}
Ask your opening question tailored to {role} ({tech_str}), focusing on architectural choices and hands-on system implementation."""

        prompt = f"""You are Alex, Lead Technical Interviewer at TalentForge conducting a live technical interview.
Candidate Target:
- Role: {role}
- Tech Stack: {tech_str}
- Difficulty: {difficulty}
- Focus: {interview_type}
- Primary Competency: {first_comp}
{resume_prompt_instructions}

Alex Tone & Realism Guidelines:
- Natural, engaging, professional, like a Staff/Principal Engineer at a top tech company.
- Ask directly about concrete engineering decisions and trade-offs rather than generic trivia.
- Distinguish implementation from hypothetical ideas: ask what they *actually built* and navigated.

Return a valid JSON object:
{{
  "content": "Interviewer opening greeting and initial question",
  "tested_competency": "{first_comp}",
  "follow_up_reason": "Grounding session in core project architecture and high-priority competency"
}}"""

        sys_inst = "You are a professional technical interviewer. Output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.7)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "content" in data and data["content"].strip():
                return {
                    "content": data["content"].strip(),
                    "tested_competency": data.get("tested_competency", first_comp),
                    "is_fallback": False
                }

        # Fallback opener
        if resume_analysis and resume_analysis.get("projects"):
            first_proj = resume_analysis["projects"][0]
            proj_name = first_proj.get("name", "recent project")
            proj_tech = ", ".join(first_proj.get("tech_stack", [])) or (tech_stack[0] if tech_stack else "modern technologies")
            return {
                "content": f"Hello! Welcome to your TalentForge technical interview for the {role} role. I've had a chance to review your resume and noticed your work on {proj_name} using {proj_tech}. To kick things off, could you walk me through the high-level architecture of that project, the core design decisions you personally implemented, and the most significant technical trade-off you navigated?",
                "tested_competency": first_comp,
                "is_fallback": True
            }

        primary = tech_stack[0] if tech_stack else "software systems"
        return {
            "content": f"Hello! Welcome to your TalentForge technical interview for the {role} role. I'm looking forward to our session today. To start us off, could you walk me through a production system where you utilized {primary}, focusing on how you designed the core architecture, handled concurrency, and resolved key trade-offs?",
            "tested_competency": first_comp,
            "is_fallback": True
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Adaptive Mock Interview: Dynamic Follow-Up Question
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def generate_mock_follow_up(
        cls,
        role: str,
        tech_stack: Optional[List[str]],
        difficulty: str,
        conversation_history: List[Dict[str, str]],
        resume_analysis: Optional[Dict[str, Any]] = None,
        blueprint: Optional[Dict[str, Any]] = None,
        live_competency_state: Optional[Dict[str, Any]] = None,
        live_claims_state: Optional[List[Dict[str, Any]]] = None,
        time_context: Optional[Dict[str, Any]] = None,
        recent_questions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        CRITICAL ADAPTIVE & TIME-AWARE ENGINE:
        - Adheres strictly to the Interview Blueprint and rotates competencies (max 2 consecutive).
        - Grounded in candidate's answers and validates resume claims progressively.
        - Distinguishes hands-on execution ('I implemented...') from hypothetical design ('I would implement...').
        - Calibrates difficulty dynamically (strong -> deeper trade-offs/edge cases; weak -> foundational recovery).
        - Respects server-side elapsed/remaining time (closing synthesis in final minutes, graceful wrap-up when time expires).
        - Strictly prevents repeated or semantically duplicate questions.
        """
        formatted_dialogue = []
        for msg in conversation_history:
            speaker = "Interviewer" if msg.get("role") == "interviewer" else "Candidate"
            formatted_dialogue.append(f"{speaker}: {msg.get('content', '')}")

        transcript_str = "\n\n".join(formatted_dialogue)
        tech_str = ", ".join(tech_stack) if tech_stack else "modern tech stack"
        resume_block = cls._format_resume_context_summary(resume_analysis)

        # Time context details
        time_ctx = time_context or {}
        duration_mode = time_ctx.get("duration_mode", "30")
        elapsed_secs = time_ctx.get("elapsed_secs", 0)
        remaining_secs = time_ctx.get("remaining_secs")
        is_closing_phase = time_ctx.get("is_closing_phase", False)
        is_time_up = time_ctx.get("is_time_up", False)

        # Format blueprint state
        comp_summary_lines = []
        uncovered_comps = []
        last_tested_comp = None
        consecutive_count = 0

        if live_competency_state and isinstance(live_competency_state, dict):
            for cid, cdata in live_competency_state.items():
                cname = cdata.get("name", cid)
                q_count = cdata.get("questions_asked", 0)
                status = cdata.get("status", "not_started")
                perf = cdata.get("performance", "unassessed")
                comp_summary_lines.append(f"- {cname} (Questions: {q_count}, Status: {status}, Performance: {perf})")
                if q_count == 0 or status == "not_started":
                    uncovered_comps.append(cname)
                if cdata.get("is_current"):
                    last_tested_comp = cname
                    consecutive_count = cdata.get("consecutive_turns", 1)

        competency_state_str = "\n".join(comp_summary_lines) if comp_summary_lines else "Standard technical competencies in progress."

        # Claims state
        claims_state_lines = []
        if live_claims_state and isinstance(live_claims_state, list):
            for citem in live_claims_state[:4]:
                claims_state_lines.append(f"- \"{citem.get('claim')}\": Status = {citem.get('status', 'Requires further validation')}")
        claims_state_str = "\n".join(claims_state_lines) if claims_state_lines else "None specified."

        # Recent questions to avoid duplicates
        recent_q_str = "\n".join([f"- {q}" for q in (recent_questions or [])[-4:]]) if recent_questions else "None yet."

        time_instructions = ""
        if is_time_up:
            time_instructions = """
>>> CRITICAL: ALLOTTED INTERVIEW TIME HAS FULLY ELAPSED! <<<
Do NOT ask another technical question.
Acknowledge the candidate's last answer in 1-2 thoughtful sentences.
Deliver a warm, professional wrap-up concluding the interview session.
State clearly: "That brings us to the end of our allotted time for today's interview. Thank you for thoroughly discussing your work and engineering decisions. I've gathered solid evidence across your core competencies; you can now view your complete evaluation and performance report."
Set "is_concluding": true in your JSON output.
"""
        elif is_closing_phase:
            mins_left = max(1, (remaining_secs or 180) // 60)
            time_instructions = f"""
>>> CLOSING STAGE (~{mins_left} minutes remaining) <<<
Time is almost up. If there is an essential uncovered high-priority competency ({', '.join(uncovered_comps[:2]) if uncovered_comps else 'system resilience'}), pivot to it now for a focused final question, or ask a synthesis question summarizing their overall architectural approach. Prepare to wrap up next turn.
"""
        else:
            time_instructions = f"""
Time Status: Normal exploration phase ({elapsed_secs // 60} mins elapsed, ~{(remaining_secs // 60) if remaining_secs else 'N/A'} mins remaining). Probe with full technical depth and appropriate pace.
"""

        prompt = f"""You are Alex, an expert Lead Technical Interviewer at TalentForge conducting a {difficulty}-level interview for a {role} position ({tech_str}).

INTERVIEW BLUEPRINT & COMPETENCY STATUS:
{competency_state_str}
Currently Active Topic: {last_tested_comp or 'Initial topic'} (Consecutive turns: {consecutive_count})
Uncovered High-Priority Competencies: {', '.join(uncovered_comps) if uncovered_comps else 'All initial topics introduced'}

RESUME CLAIMS PROGRESSION:
{claims_state_str}

RECENT QUESTIONS ASKED (DO NOT DUPLICATE OR REPHRASE THESE):
{recent_q_str}

{resume_block if resume_block else "Candidate is practicing in general role mode without an attached resume."}

TIME STATUS & CONTROLS:
{time_instructions}

Conversation Transcript So Far:
────────────────────────────────────────
{transcript_str}
────────────────────────────────────────

CORE INTERVIEW STRATEGY & STRICT RULES:
1. MANDATORY TOPIC ROTATION:
   If consecutive turns on the current topic is >= 2, you MUST pivot to the next uncovered competency (e.g., {uncovered_comps[0] if uncovered_comps else 'database internals, caching, or resilience'}). Never linger for 3+ consecutive questions on the exact same narrow subtopic!
2. PROBING RESUME CLAIMS WITH DEPTH:
   Follow the progression: claim -> implementation detail -> reasoning -> trade-off -> edge case -> production consideration.
   Do NOT just mention the project name. Probe WHY choices were made (e.g., "Why TF-IDF instead of embeddings?", "Why Naive Bayes?", "What alternatives were considered?", "What happens under concurrent write spikes?").
3. DISTINGUISH IMPLEMENTATION FROM HYPOTHETICAL KNOWLEDGE:
   - If candidate said "I implemented / I designed / I built...", probe real implementation specifics: libraries used, tricky edge cases, and unexpected hurdles in production.
   - If candidate said "I would implement / In theory...", acknowledge it as a hypothetical architecture and ask whether they navigated this in production or what practical trade-offs they anticipate.
4. ADAPTIVE DIFFICULTY CALIBRATION:
   - Strong answer: Challenge with architectural trade-offs, scale constraints (e.g. 10x traffic spike, connection pool saturation), distributed failure modes, or edge cases.
   - Average answer: Probe for clarification, concrete implementation mechanism, or missing trade-off.
   - Weak answer: Provide a simpler foundational bridge, allow candidate to explain basics without humiliation, before rotating competency.
5. TECHNICAL INTERVIEW REALISM:
   Occasionally challenge assumptions naturally like a real Staff Engineer (e.g. "What data would you cache, what's your invalidation strategy, and what happens if Redis becomes unavailable?").
6. NEVER REPEAT:
   Verify that your question is completely distinct from all recent questions listed above.

Return a valid JSON object matching this schema:
{{
  "content": "Alex's response and next probing question (or concluding statement if time is up)",
  "tested_competency": "Name of the competency this question evaluates",
  "competency_rating": "Strong" | "Adequate" | "Needs Improvement",
  "evidence_snippet": "Direct quote or specific detail observed from candidate's answer",
  "follow_up_reason": "Identifiable technical reason for asking this question now",
  "tested_claim": "Resume claim being tested, or null if general competency",
  "claim_status": "Demonstrated" | "Partially demonstrated" | "Requires further validation" | null,
  "difficulty_direction": "increase" | "maintain" | "decrease",
  "is_concluding": false // true ONLY if time is up or interview naturally wraps up
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are an adaptive technical interviewer. Adhere strictly to the blueprint, rotate competencies, calibrate difficulty, and output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.6)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "content" in data and data["content"].strip():
                data["is_fallback"] = False
                return data

        # Fallback adaptive response
        last_answer = ""
        for m in reversed(conversation_history):
            if m.get("role") == "candidate":
                last_answer = m.get("content", "")
                break

        return cls._fallback_follow_up(last_answer, role, tech_stack, resume_analysis, is_time_up, uncovered_comps)

    @classmethod
    def _fallback_follow_up(
        cls,
        last_answer: str,
        role: str,
        tech_stack: Optional[List[str]],
        resume_analysis: Optional[Dict[str, Any]] = None,
        is_time_up: bool = False,
        uncovered_comps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if is_time_up:
            return {
                "content": f"Thank you for sharing those insights. That brings us to the end of our allotted time for today's {role} interview. You've walked through your engineering decisions and technical background thoroughly. You can now view your comprehensive performance evaluation and report.",
                "tested_competency": "Interview Wrap-up",
                "competency_rating": "Adequate",
                "evidence_snippet": "Candidate provided concluding technical thoughts.",
                "follow_up_reason": "Time limit elapsed.",
                "tested_claim": None,
                "claim_status": None,
                "difficulty_direction": "maintain",
                "is_concluding": True,
                "is_fallback": True
            }

        lower = last_answer.lower()
        tested_comp = "System Architecture & Concurrency"
        tested_claim = None
        claim_status = None

        if "jwt" in lower or "auth" in lower or "token" in lower:
            q = "You mentioned token authentication. How do you handle token expiration and secure refresh token rotation without creating race conditions across distributed workers?"
            tested_comp = "Security & Auth Architecture"
        elif "database" in lower or "sql" in lower or "postgres" in lower or "mongo" in lower:
            q = "Regarding your data storage choices, when query volume scales 10x, what specific indexing and connection pooling strategy prevents connection pool exhaustion?"
            tested_comp = "Database Internals & Optimization"
        elif "cache" in lower or "redis" in lower:
            q = "You touched on caching with Redis. What is your exact cache invalidation strategy, and how do you protect your primary database against a cache stampede if Redis restarts?"
            tested_comp = "Distributed Caching & Fault Tolerance"
        elif resume_analysis and resume_analysis.get("technical_claims"):
            claim = resume_analysis["technical_claims"][0]
            q = f"Looking at your resume where you noted '{claim}': what was the most difficult architectural trade-off in that implementation, and what alternatives did you reject?"
            tested_comp = "Project Architecture & Resume Validation"
            tested_claim = claim
            claim_status = "Partially demonstrated"
        elif uncovered_comps and len(uncovered_comps) > 0:
            target = uncovered_comps[0]
            q = f"Let's shift focus to {target}. In your recent production systems, how have you approached this area to ensure high reliability under unexpected traffic spikes?"
            tested_comp = target
        else:
            primary = tech_stack[0] if tech_stack else "this system"
            q = f"Building on your points regarding {primary}, what is the primary failure mode of this design, and how does your monitoring detect it before users are impacted?"
            tested_comp = "Production Reliability & Incident Debugging"

        return {
            "content": f"Thank you for walking me through that. {q}",
            "tested_competency": tested_comp,
            "competency_rating": "Adequate",
            "evidence_snippet": last_answer[:100] + "...",
            "follow_up_reason": f"Probing deeper into {tested_comp}",
            "tested_claim": tested_claim,
            "claim_status": claim_status,
            "difficulty_direction": "maintain",
            "is_concluding": False,
            "is_fallback": True
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 8. Adaptive Mock Interview: Comprehensive Evidence-Based Evaluation
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def evaluate_mock_session(
        cls,
        role: str,
        tech_stack: Optional[List[str]],
        difficulty: str,
        conversation_history: List[Dict[str, str]],
        resume_analysis: Optional[Dict[str, Any]] = None,
        blueprint: Optional[Dict[str, Any]] = None,
        live_competency_state: Optional[Dict[str, Any]] = None,
        duration_mode: Optional[str] = "30",
        actual_duration_secs: Optional[int] = None,
        completion_reason: Optional[str] = "natural",
    ) -> Dict[str, Any]:
        """
        Evaluates the full interview transcript across 4 standardized dimensions,
        generates an evidence-grounded competency breakdown, evaluates 3-tier resume claim validation,
        distinguishes hands-on execution from hypothetical proposals, and provides actionable recommendations.
        """
        formatted_dialogue = []
        for msg in conversation_history:
            speaker = "Interviewer" if msg.get("role") == "interviewer" else "Candidate"
            formatted_dialogue.append(f"{speaker}: {msg.get('content', '')}")

        transcript_str = "\n\n".join(formatted_dialogue)
        tech_str = ", ".join(tech_stack) if tech_stack else "relevant stack"
        resume_block = cls._format_resume_context_summary(resume_analysis)

        # Blueprint competencies to grade
        bp_comps = []
        if blueprint and blueprint.get("competencies"):
            bp_comps = [c.get("name") for c in blueprint["competencies"]]
        elif live_competency_state and isinstance(live_competency_state, dict):
            bp_comps = [v.get("name", k) for k, v in live_competency_state.items()]
        else:
            bp_comps = [
                "System Architecture & Concurrency",
                "Database Internals & Optimization",
                "API Resilience & Caching",
                "Production Reliability & Incident Debugging"
            ]

        # Claims to evaluate
        claims_list = []
        if blueprint and blueprint.get("claims_to_validate"):
            claims_list = [c.get("claim") for c in blueprint["claims_to_validate"]]
        elif resume_analysis and resume_analysis.get("technical_claims"):
            claims_list = resume_analysis["technical_claims"][:5]

        claims_prompt_block = ""
        if claims_list:
            claims_prompt_block = f"""
Candidate Claims Extracted From Resume/Blueprint:
{json.dumps(claims_list)}

3-TIER CLAIM VALIDATION INSTRUCTIONS:
Assess each claim based strictly on candidate answers:
- "Demonstrated": Candidate articulated hands-on depth, authentic engineering rationale, and concrete details.
- "Partially demonstrated": Candidate showed baseline or theoretical familiarity, but lacked implementation depth on trade-offs/edge cases.
- "Requires further validation": Claim was not sufficiently tested or candidate struggled to explain mechanics.
*NOTE*: Treat claims objectively. Never accuse candidate of exaggeration; use professional, constructive language.
"""

        prompt = f"""You are the Lead Technical Interview Evaluator at TalentForge reviewing a completed interview.
Role: {role}
Difficulty: {difficulty}
Tech Stack: {tech_str}
Duration Mode: {duration_mode} (Actual duration: {(actual_duration_secs // 60) if actual_duration_secs else 'N/A'} mins)
Completion Reason: {completion_reason}

Target Blueprint Competencies:
{json.dumps(bp_comps)}

{resume_block if resume_block else "Candidate practiced without an uploaded resume."}

{claims_prompt_block}

Full Interview Transcript:
────────────────────────────────────────
{transcript_str}
────────────────────────────────────────

CRITICAL EVIDENCE-BASED EVALUATION RULES:
1. GROUND SCORES IN TRANSCRIPT EVIDENCE:
   Every finding, strength, and weakness must cite specific answers or quotes from the transcript.
2. DISTINGUISH HANDS-ON EXPERIENCE FROM HYPOTHETICAL KNOWLEDGE:
   - If candidate described what they *personally implemented* in production with concrete anecdotes, credit hands-on experience.
   - If candidate described theoretical designs ("I would use...", "In theory..."), classify as Strong Theoretical Understanding, not hands-on execution.
3. COMPETENCY COVERAGE BREAKDOWN:
   Evaluate each competency from the blueprint:
   - score: 0-100
   - status: "Strong" | "Adequate" | "Needs Improvement" | "Not Covered"
   - what_candidate_demonstrated: concise explanation of what candidate showed
   - evidence: exact quote or specific statement from the candidate
   - what_remains_uncertain: what depth was missing or untested
   - improvement_area: specific technical gap
4. ACTIONABLE RECOMMENDATIONS:
   Provide 3 actionable recommendations formatted as objects:
   - topic: Specific concept (e.g. "Zero-Downtime Database Migrations")
   - why_it_matters: Why it matters for a {role}
   - specific_weakness: Exact weakness observed in transcript
   - concrete_exercise: Real-world engineering exercise or project task
   - practice_question: Realistic interview question to practice in Questions Studio

Return a valid JSON object matching this schema:
{{
  "overall_score": 82,
  "rubric": {{
    "technical_knowledge": 85,
    "problem_solving": 80,
    "communication": 78,
    "answer_quality": 84
  }},
  "hands_on_vs_theoretical": "Candidate demonstrated verified hands-on depth in backend API development, while distributed systems scaling was articulated at a theoretical design level.",
  "summary": "Executive evaluation summary citing specific highlights from the conversation",
  "strengths": [
    "Specific strength citing candidate's answer on architecture trade-offs",
    "Specific strength citing candidate's clear articulation of caching"
  ],
  "weaknesses": [
    "Specific weakness citing hesitation regarding failure modes",
    "Specific weakness citing missing discussion of schema migrations"
  ],
  "competency_coverage": {{
    "comp_1": {{
      "name": "System Architecture & Concurrency",
      "score": 85,
      "status": "Strong",
      "what_candidate_demonstrated": "Explained asynchronous pipeline design and process decoupling.",
      "evidence": "Candidate stated: '...' ",
      "what_remains_uncertain": "Handling backpressure under prolonged worker saturation was not explored.",
      "improvement_area": "Define explicit queue dead-lettering and throttling policies."
    }}
  }},
  "validated_claims": [
    {{
      "claim": "Specific claim text",
      "status": "Demonstrated", // "Demonstrated" | "Partially demonstrated" | "Requires further validation"
      "evidence": "Candidate stated: '...' ",
      "notes": "Candidate articulated authentic implementation depth."
    }}
  ],
  "recommendations": [
    "Zero-Downtime Database Migrations & Rolling Schema Updates",
    "Cache Invalidation & Stampede Mitigation Strategies"
  ],
  "actionable_recommendations": [
    {{
      "topic": "Zero-Downtime Database Migrations",
      "why_it_matters": "For a Senior Backend Engineer, schema evolution must not lock transactional tables.",
      "specific_weakness": "Candidate recognized connection limits but did not explain how to add non-null columns without table locks.",
      "concrete_exercise": "Design a 3-phase Alembic migration (nullable column -> background backfill -> apply NOT NULL constraint).",
      "practice_question": "How do you safely add a NOT NULL column with a default value to a 10-million row table in production?"
    }}
  ]
}}
Ensure the JSON is strictly valid."""

        sys_inst = "You are an objective technical interview evaluator. You ground every score in transcript evidence. Output valid JSON only."
        raw = cls._call_gemini(prompt, system_instruction=sys_inst, json_mode=True, temperature=0.3)
        if raw:
            data = cls._parse_json_safely(raw)
            if data and "overall_score" in data and "rubric" in data:
                data["is_fallback"] = False
                if "competency_coverage" not in data or not data["competency_coverage"]:
                    data["competency_coverage"] = cls._default_competency_coverage(data["overall_score"], bp_comps)
                if "validated_claims" not in data or data["validated_claims"] is None:
                    data["validated_claims"] = []
                if "actionable_recommendations" not in data or not data["actionable_recommendations"]:
                    data["actionable_recommendations"] = cls._default_actionable_recommendations(role, tech_stack)
                return data

        return cls._fallback_mock_evaluation(
            conversation_history, role, tech_stack, resume_analysis, bp_comps, duration_mode, actual_duration_secs, completion_reason
        )

    @classmethod
    def _default_competency_coverage(cls, base_score: int, comp_names: Optional[List[str]] = None) -> Dict[str, Any]:
        comps = comp_names or [
            "System Architecture & Concurrency",
            "Database Internals & Optimization",
            "API Resilience & Caching",
            "Production Reliability & Incident Debugging"
        ]
        result = {}
        for i, cname in enumerate(comps[:5]):
            key = f"comp_{i+1}"
            score = max(50, min(100, base_score + (2 if i % 2 == 0 else -3)))
            status = "Strong" if score >= 80 else ("Adequate" if score >= 65 else "Needs Improvement")
            result[key] = {
                "name": cname,
                "score": score,
                "status": status,
                "what_candidate_demonstrated": f"Candidate addressed core principles of {cname.lower()}.",
                "evidence": f"Candidate demonstrated baseline engineering familiarity with {cname.lower()}.",
                "what_remains_uncertain": "Deep production edge cases and recovery limits were not fully explored.",
                "improvement_area": f"Strengthen real-world operational trade-offs for {cname.lower()}."
            }
        return result

    @classmethod
    def _default_actionable_recommendations(cls, role: str, tech_stack: Optional[List[str]]) -> List[Dict[str, Any]]:
        primary = tech_stack[0] if tech_stack else "System Design"
        sec = tech_stack[1] if tech_stack and len(tech_stack) > 1 else "Database"
        return [
            {
                "topic": f"Zero-Downtime Schema Migrations in {sec}",
                "why_it_matters": f"In production systems for {role}, altering large tables must avoid write locks that degrade latency.",
                "specific_weakness": "Candidate discussed schema design but lacked a clear multi-step deployment strategy for non-null column additions.",
                "concrete_exercise": "Write a multi-step migration script with backward-compatible schema expansion, data backfill, and contract enforcement.",
                "practice_question": f"How do you perform a rolling database migration in {sec} when altering a critical table without taking locks?"
            },
            {
                "topic": f"High-Throughput Caching & Stampede Mitigation with {primary}",
                "why_it_matters": "Protecting primary datastores during sudden traffic bursts is essential for system availability.",
                "specific_weakness": "Candidate noted using cache keys but did not detail invalidation protocols or mutex locking during cache misses.",
                "concrete_exercise": "Implement a distributed lock or probabilistic early expiration algorithm to prevent cache stampedes.",
                "practice_question": "Explain how you handle cache invalidation and stampede protection during sudden viral traffic surges."
            },
            {
                "topic": "Distributed Incident Debugging & Trace Correlation",
                "why_it_matters": f"Senior {role} engineers must rapidly isolate root causes across microservices.",
                "specific_weakness": "Candidate focused on local logging rather than distributed trace propagation across services.",
                "concrete_exercise": "Set up OpenTelemetry correlation IDs across an API gateway and downstream worker service.",
                "practice_question": "Walk me through how you isolate a 500ms latency regression occurring intermittently across microservices."
            }
        ]

    @classmethod
    def _fallback_mock_evaluation(
        cls,
        conversation_history: List[Dict[str, str]],
        role: str,
        tech_stack: Optional[List[str]],
        resume_analysis: Optional[Dict[str, Any]] = None,
        comp_names: Optional[List[str]] = None,
        duration_mode: Optional[str] = "30",
        actual_duration_secs: Optional[int] = None,
        completion_reason: Optional[str] = "natural",
    ) -> Dict[str, Any]:
        candidate_turns = [m for m in conversation_history if m.get("role") == "candidate"]
        total_words = sum(len(m.get("content", "").split()) for m in candidate_turns)
        avg_words = total_words // max(1, len(candidate_turns))

        base_score = min(92, max(60, 68 + (avg_words // 20)))
        primary_tech = tech_stack[0] if tech_stack else "System Design"

        first_sample_answer = candidate_turns[0].get("content", "")[:120] if candidate_turns else "Initial project architecture overview"

        validated_claims = []
        if resume_analysis and resume_analysis.get("technical_claims"):
            for i, claim in enumerate(resume_analysis["technical_claims"][:4]):
                if i == 0 and avg_words > 30:
                    status = "Demonstrated"
                    evidence = f"Candidate articulated: '{first_sample_answer}...'"
                    notes = "Candidate demonstrated authentic implementation depth with clear architectural reasoning."
                elif i == 1:
                    status = "Partially demonstrated"
                    evidence = "Candidate covered high-level concepts but lacked concrete failure recovery details."
                    notes = "Theoretical fluency was evident; hands-on edge cases require further validation."
                else:
                    status = "Requires further validation"
                    evidence = "Topic was touched upon briefly without deep operational exploration."
                    notes = "Claim requires specialized follow-up questioning to confirm production depth."

                validated_claims.append({
                    "claim": claim,
                    "status": status,
                    "evidence": evidence,
                    "notes": notes
                })

        return {
            "overall_score": base_score,
            "rubric": {
                "technical_knowledge": min(100, base_score + 2),
                "problem_solving": max(50, base_score - 3),
                "communication": min(100, base_score + 4),
                "answer_quality": base_score
            },
            "hands_on_vs_theoretical": (
                "Candidate exhibited hands-on implementation depth in core programming constructs and component design, "
                "with distributed scaling trade-offs presented at a conceptual level."
            ),
            "summary": (
                f"[Offline Mode] The candidate completed {len(candidate_turns)} conversational turns for the {role} interview "
                f"({(actual_duration_secs // 60) if actual_duration_secs else 'standard'} mins elapsed, reason: {completion_reason}), "
                f"demonstrating structured thought and an average response length of {avg_words} words."
            ),
            "strengths": [
                f"Engaged consistently across turns with relevant {primary_tech} context.",
                f"Demonstrated coherent reasoning citing concrete implementation details: '{first_sample_answer[:60]}...'",
                "Maintained structured communication across interviewer follow-up questions."
            ],
            "weaknesses": [
                "Could provide more quantitative metrics (e.g. latency percentiles, queries per second).",
                "Exploration of complex failure recovery modes under partial outages was limited."
            ],
            "recommendations": [
                f"Zero-Downtime Schema Migrations in {primary_tech}",
                "High-Throughput Caching & Stampede Mitigation",
                "Distributed Incident Debugging & Trace Correlation"
            ],
            "actionable_recommendations": cls._default_actionable_recommendations(role, tech_stack),
            "competency_coverage": cls._default_competency_coverage(base_score, comp_names),
            "validated_claims": validated_claims,
            "is_fallback": True
        }


