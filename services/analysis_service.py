import json

from clients.analysis_client import AnalysisClient


class AnalysisService:
    """Processes user stories and raw text requirements, preparing prompts for the AnalysisClient and handling responses."""
    def __init__(self, client: AnalysisClient):
        self.__client = client

    def analyze_requirements(self, analysis_text: str) -> str:
        """Prepare a prompt for the AnalysisClient based on the provided analysis text and return the response."""
        prompt = self.__prepare_prompt(analysis_text)

        return self.__client.get_response(prompt)

    def analyze_user_story(self, user_story_id: str) -> str:
        """Fetch and analyze a user story from Azure DevOps by its ID, returning the compliance report. Now a placeholder implementation."""
        print(f"Analyzing user story with ID: {user_story_id}")

        compliance_report = f"Compliance report for user story {user_story_id}"
        
        return compliance_report

    def __prepare_prompt(self, analysis_text: str) -> str:
        """Prepare a structured prompt for the AnalysisClient, requesting a JSON response with specific keys for compliance analysis."""
        prompt = (
            f"Analyze this user story for OWASP Top 10, STRIDE threats, GDPR, NIS2, EHDS gaps. "
            f"Flag risks with mitigations:\n{analysis_text}\n\n"
            "Provide the response as a JSON object with the following keys:\n"
            "- 'owasp_risks': [List any relevant OWASP Top 10 risks and mitigations]\n"
            "- 'stride_threats': [List any relevant STRIDE threats and mitigations]\n"
            "- 'gdpr_issues': [Identify any GDPR compliance issues and mitigations]\n"
            "- 'nis2_issues': [Identify any NIS2 compliance issues and mitigations]\n"
            "- 'ehds_issues': [Identify any EHDS compliance issues and mitigations]\n"
            "- 'is_compliant': true/false (boolean evaluation)"
        )

        return prompt
