from typing import List, Optional, Dict, Any

RESUME_SECTIONS = {
    "Personal Details": [
        ("full_name", "Full Name", "Candidate's complete legal name"),
        ("email", "Email Address", "Primary contact email"),
        ("phone", "Phone Number", "Telephone / mobile number"),
        ("location", "Current Location", "City, State / Country"),
        ("linkedin_url", "LinkedIn Profile", "URL or handle for LinkedIn"),
        ("github_or_portfolio", "Portfolio / GitHub", "Portfolio site or repository URL"),
        ("summary", "Executive Summary", "Short career profile or summary")
    ],
    "Professional Profile": [
        ("current_title", "Current / Target Title", "Job title or specialization"),
        ("years_of_experience", "Total Years Experience", "Calculated or stated experience in years"),
        ("primary_skills", "Primary Skills", "Key technical or functional competencies"),
        ("tools_frameworks", "Tools & Frameworks", "Software, libraries, frameworks"),
        ("certifications", "Certifications", "Professional licenses and certs")
    ],
    "Education Summary": [
        ("highest_degree", "Highest Degree", "e.g. Master of Science, Bachelor of Engineering"),
        ("field_of_study", "Field of Study", "Computer Science, Economics, etc."),
        ("institution", "Institution", "University or College attended"),
        ("graduation_year", "Graduation Year", "Year of graduation or anticipated date"),
        ("gpa_or_honors", "GPA / Honors", "Academic performance indicator")
    ]
}

RESUME_TOOL_SPEC = {
    "name": "extract_resume_data",
    "description": "Extract candidate details, profile sections, work history table, and education table from a resume.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_name": {"type": "string"},
                        "field_label": {"type": "string"},
                        "section": {"type": "string"},
                        "value": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "page_number": {"type": "integer", "default": 1},
                        "bounding_box": {
                            "type": "object",
                            "properties": {
                                "ymin": {"type": "number"},
                                "xmin": {"type": "number"},
                                "ymax": {"type": "number"},
                                "xmax": {"type": "number"},
                                "page": {"type": "integer", "default": 1}
                            },
                            "required": ["ymin", "xmin", "ymax", "xmax"]
                        }
                    },
                    "required": ["field_name", "field_label", "section", "value", "confidence"]
                }
            },
            "work_history_table": {
                "type": "object",
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                },
                "required": ["columns", "rows"]
            },
            "education_table": {
                "type": "object",
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        },
        "required": ["fields", "work_history_table"]
    }
}
