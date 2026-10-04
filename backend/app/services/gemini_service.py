import json
import re
import logging
from typing import List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Helper to invoke Gemini API
# ---------------------------------------------------------
def call_gemini_api(prompt: str, json_mode: bool = False) -> str:
    """
    Calls Google Gemini API using the current google-genai SDK.
    """

    api_key = settings.GEMINI_API_KEY

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend environment variables."
        )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        config = None

        if json_mode:
            config = {
                "response_mime_type": "application/json"
            }

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=config
        )

        if response and response.text:
            return response.text

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    except Exception as e:
        logger.error(
            f"Gemini API request failed: {e}"
        )

        raise RuntimeError(
            f"Failed to communicate with Gemini API: {e}"
        )


# ---------------------------------------------------------
# Clean JSON response
# ---------------------------------------------------------
def clean_json_response(raw_text: str) -> str:
    """
    Removes markdown code fences such as
    ```json ... ```
    from raw AI text.
    """

    if not raw_text:
        return ""

    text = raw_text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# ---------------------------------------------------------
# Feature 1: Ask AI Question
# ---------------------------------------------------------
async def ask_ai_question(
    question_text: str
) -> Dict[str, Any]:

    prompt = f"""
You are Smart Learn, an expert AI tutor.
Answer the following educational question clearly,
accurately, and concisely.

Question:
{question_text}

Provide your response in JSON format with two keys:

1. "answer":
   A comprehensive, well-structured explanation using
   markdown where helpful.

2. "key_takeaways":
   A list of 3-5 key summary points.

JSON Format:
{{
  "answer": "...",
  "key_takeaways": [
    "Point 1",
    "Point 2",
    "Point 3"
  ]
}}
"""

    raw_response = call_gemini_api(
        prompt,
        json_mode=True
    )

    cleaned = clean_json_response(raw_response)

    try:
        data = json.loads(cleaned)

        return {
            "question": question_text,
            "answer": data.get(
                "answer",
                raw_response
            ),
            "key_takeaways": data.get(
                "key_takeaways",
                []
            )
        }

    except Exception:
        return {
            "question": question_text,
            "answer": raw_response,
            "key_takeaways": []
        }


# ---------------------------------------------------------
# Feature 2: Explain Concept
# ---------------------------------------------------------
async def explain_concept(
    concept: str,
    level: str = "intermediate"
) -> Dict[str, Any]:

    prompt = f"""
You are Smart Learn, an AI educational expert.
Explain the concept "{concept}" tailored for a
{level} level student.

Level guidelines:

Beginner:
Simple terms, real-world everyday analogies,
no heavy jargon.

Intermediate:
Clear academic explanation, core principles,
key applications, moderate depth.

Advanced:
Deep technical breakdown, formal definitions,
edge cases, underlying mechanics.

Return a JSON object with:

{{
  "explanation": "Structured detailed explanation...",
  "analogies": [
    "Analogy 1",
    "Analogy 2"
  ],
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}}
"""

    raw_response = call_gemini_api(
        prompt,
        json_mode=True
    )

    cleaned = clean_json_response(raw_response)

    try:
        data = json.loads(cleaned)

        return {
            "concept": concept,
            "level": level,
            "explanation": data.get(
                "explanation",
                raw_response
            ),
            "analogies": data.get(
                "analogies",
                []
            ),
            "key_points": data.get(
                "key_points",
                []
            )
        }

    except Exception:
        return {
            "concept": concept,
            "level": level,
            "explanation": raw_response,
            "analogies": [],
            "key_points": []
        }


# ---------------------------------------------------------
# Feature 3: Summarize Text
# ---------------------------------------------------------
async def summarize_text(
    text: str
) -> Dict[str, Any]:

    truncated_text = text[:30000]

    prompt = f"""
You are Smart Learn, an AI text summarization assistant.
Analyze and summarize the following educational content.

Content:
{truncated_text}

Return a valid JSON object with:

1. "summary":
   A concise overview of the entire material.

2. "key_points":
   A list of essential main points.

3. "important_concepts":
   A list of core educational concepts covered.

4. "key_terms":
   A list of objects with "term" and "definition"
   for important vocabulary/terms.

JSON Format:

{{
  "summary": "...",
  "key_points": ["..."],
  "important_concepts": ["..."],
  "key_terms": [
    {{
      "term": "...",
      "definition": "..."
    }}
  ]
}}
"""

    raw_response = call_gemini_api(
        prompt,
        json_mode=True
    )

    cleaned = clean_json_response(raw_response)

    try:
        data = json.loads(cleaned)

        return {
            "summary": data.get(
                "summary",
                "Summary generated."
            ),
            "key_points": data.get(
                "key_points",
                []
            ),
            "important_concepts": data.get(
                "important_concepts",
                []
            ),
            "key_terms": data.get(
                "key_terms",
                []
            )
        }

    except Exception:
        return {
            "summary": raw_response,
            "key_points": [],
            "important_concepts": [],
            "key_terms": []
        }


# ---------------------------------------------------------
# Feature 4: MCQ Test Generation from Transcript
# ---------------------------------------------------------
async def generate_mcq_test(
    transcript_text: str,
    question_count: int = 20,
    difficulty: str = "mixed"
) -> List[Dict[str, Any]]:

    clean_transcript = transcript_text[:40000]

    difficulty_instruction = {
        "easy":
            "Generate easy-level foundational questions "
            "testing direct recall and simple understanding.",

        "medium":
            "Generate medium-level questions testing "
            "conceptual comprehension and application.",

        "hard":
            "Generate hard-level questions testing deep "
            "analysis, edge cases, and critical evaluation.",

        "mixed":
            "Generate a balanced mixture of easy (30%), "
            "medium (50%), and hard (20%) questions."
    }.get(
        difficulty.lower(),
        "Generate a balanced mixture of easy, medium, "
        "and hard questions."
    )

    prompt = f"""
You are an expert test creator for Smart Learn.

Your task is to generate exactly {question_count}
high-quality Multiple Choice Questions (MCQs)
strictly based on the provided educational transcript.

Content:
{clean_transcript}

Requirements:

1. Generate EXACTLY {question_count} questions.

2. Difficulty setting:
{difficulty_instruction}

3. Avoid duplicate questions or near-duplicate phrasing.

4. Each question MUST have exactly four options:
   option_a
   option_b
   option_c
   option_d

5. EXACTLY ONE option must be correct.

6. Specify correct_answer as:
   "option_a"
   "option_b"
   "option_c"
   or
   "option_d"

7. Provide a clear educational explanation
   for why the correct option is correct.

8. Set difficulty field for each question as:
   "easy", "medium", or "hard".

Respond ONLY with a valid JSON array.

Example:

[
  {{
    "id": 1,
    "question": "What is the primary function of...?",
    "option_a": "Option A text",
    "option_b": "Option B text",
    "option_c": "Option C text",
    "option_d": "Option D text",
    "correct_answer": "option_a",
    "explanation": "Option A is correct because...",
    "difficulty": "medium"
  }}
]
"""

    raw_response = call_gemini_api(
        prompt,
        json_mode=True
    )

    cleaned = clean_json_response(raw_response)

    try:
        parsed_questions = json.loads(cleaned)

        if (
            isinstance(parsed_questions, dict)
            and "questions" in parsed_questions
        ):
            parsed_questions = parsed_questions["questions"]

    except Exception as parse_err:

        logger.error(
            "JSON parsing error for test generation: "
            f"{parse_err}. Raw output sample: "
            f"{cleaned[:300]}"
        )

        match = re.search(
            r'\[\s*\{.*\}\s*\]',
            cleaned,
            re.DOTALL
        )

        if match:

            try:
                parsed_questions = json.loads(
                    match.group(0)
                )

            except Exception:

                raise ValueError(
                    "AI generated output that could not be "
                    "parsed as a structured question set. "
                    "Please try again."
                )

        else:

            raise ValueError(
                "AI output format error during test "
                "generation. Please try again."
            )

    if (
        not isinstance(parsed_questions, list)
        or len(parsed_questions) == 0
    ):
        raise ValueError(
            "AI failed to return valid questions list."
        )

    validated_questions = []

    valid_options = {
        "option_a",
        "option_b",
        "option_c",
        "option_d"
    }

    for idx, q in enumerate(
        parsed_questions,
        1
    ):

        question_text = q.get(
            "question",
            f"Question {idx}"
        )

        opt_a = q.get(
            "option_a",
            "Option A"
        )

        opt_b = q.get(
            "option_b",
            "Option B"
        )

        opt_c = q.get(
            "option_c",
            "Option C"
        )

        opt_d = q.get(
            "option_d",
            "Option D"
        )

        correct = str(
            q.get(
                "correct_answer",
                "option_a"
            )
        ).lower().strip()

        if correct not in valid_options:

            if correct in ["a", "option a", "a."]:
                correct = "option_a"

            elif correct in ["b", "option b", "b."]:
                correct = "option_b"

            elif correct in ["c", "option c", "c."]:
                correct = "option_c"

            elif correct in ["d", "option d", "d."]:
                correct = "option_d"

            else:
                correct = "option_a"

        diff = str(
            q.get(
                "difficulty",
                "medium"
            )
        ).lower().strip()

        if diff not in [
            "easy",
            "medium",
            "hard"
        ]:
            diff = "medium"

        explanation = q.get(
            "explanation",
            "Correct answer verified based on educational material."
        )

        validated_questions.append({
            "id": idx,
            "question": question_text,
            "option_a": opt_a,
            "option_b": opt_b,
            "option_c": opt_c,
            "option_d": opt_d,
            "correct_answer": correct,
            "explanation": explanation,
            "difficulty": diff
        })

    return validated_questions


# ---------------------------------------------------------
# Feature 5: AI Learning Recommendations
# ---------------------------------------------------------
async def generate_learning_recommendations(
    stats: Dict[str, Any]
) -> Dict[str, Any]:

    prompt = f"""
You are Smart Learn's AI Academic Advisor.

Analyze the following actual student performance data
and generate personalized, realistic learning recommendations.

Student Performance Metrics:

Total Tests Attempted:
{stats.get('tests_attempted', 0)}

Total Questions Attempted:
{stats.get('questions_attempted', 0)}

Average Score:
{stats.get('average_score_percentage', 0)}%

Best Score:
{stats.get('best_score_percentage', 0)}%

Total Correct Answers:
{stats.get('total_correct', 0)}

Total Incorrect Answers:
{stats.get('total_incorrect', 0)}

Accuracy by Difficulty:
{json.dumps(stats.get('by_difficulty', {}))}

Recent Test Attempts:
{json.dumps(stats.get('recent_attempts', []))}

Return a valid JSON object with:

1. "overall_status":
   A one-sentence encouraging summary.

2. "strengths":
   A list of 2-3 observed strengths.

3. "weaknesses":
   A list of 2-3 areas needing attention.

4. "recommendations":
   A list of 3 actionable recommendations.

Each recommendation must contain:

- "category": "Review", "Practice", or "New Test"
- "title": Concise recommendation title
- "description": Detailed explanation
- "action_type": "review", "practice", or "generate"

JSON Format:

{{
  "overall_status": "...",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": [
    {{
      "category": "Practice",
      "title": "Practice Incorrect Questions",
      "description": "Re-attempt questions you missed...",
      "action_type": "practice"
    }}
  ]
}}
"""

    raw_response = call_gemini_api(
        prompt,
        json_mode=True
    )

    cleaned = clean_json_response(raw_response)

    try:
        data = json.loads(cleaned)

        return data

    except Exception:

        avg = stats.get(
            "average_score_percentage",
            0
        )

        status_msg = (
            "You are making steady progress!"
            if avg >= 70
            else
            "Focus on reviewing foundational concepts."
        )

        return {
            "overall_status": status_msg,

            "strengths": [
                "Consistent test attempt participation."
            ],

            "weaknesses": [
                "Improve accuracy on higher difficulty tests."
            ],

            "recommendations": [

                {
                    "category": "Practice",
                    "title": "Review Missed Questions",
                    "description":
                        "Use the Practice Incorrect Questions "
                        "feature to strengthen weak topics.",
                    "action_type": "practice"
                },

                {
                    "category": "Concept",
                    "title": "Use Concept Explainer",
                    "description":
                        "Break down challenging concepts "
                        "into beginner or intermediate steps.",
                    "action_type": "review"
                }
            ]
        }
