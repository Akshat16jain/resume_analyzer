from openai import OpenAI
import json

client = OpenAI()


def analyze_resume(resume_text, user_goal):

    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's target job role.

TARGET ROLE:
{user_goal}

STRICT RULES:
1. Extract only skills relevant to the target role.
2. Ignore irrelevant skills.
3. Identify genuine missing skills.
4. Create a roadmap only for missing skills.
5. Generate interview questions relevant to the target role.
6. The answer must be different for different target roles.
7. Return ONLY valid JSON.

Required JSON format:

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

RESUME:
{resume_text}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict technical hiring manager."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        print("OPENAI RESPONSE:")
        print(content)

        # Find JSON
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("OpenAI did not return valid JSON.")

        json_text = content[start:end]

        result = json.loads(json_text)

        return result

    except Exception as e:

        print("OPENAI ERROR:")
        print(type(e).__name__)
        print(str(e))

        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": f"{type(e).__name__}: {str(e)}"
        }