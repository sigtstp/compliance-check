import sys
import json
import os
import datetime


class ReportHandler:
    """Handles the processing of compliance reports, including printing and file management."""
    @staticmethod
    def handle(report: str):
        """Process the compliance report by printing it and saving to a file."""
        ReportHandler.__provide_report(report)
        ReportHandler.__create_file(report)

    @staticmethod
    def __provide_report(report: str):
        """Print the compliance report to the console in a readable format."""
        print("\n--- Compliance Report ---")

        try:
            report_json = json.loads(report)
            print(json.dumps(report_json, indent=2))
        except json.JSONDecodeError:
            # Fallback to printing the raw string if the model hallucinated formatting
            print(report)

        print("-------------------------\n")

    @staticmethod
    def __create_file(content: str):
        """Save the compliance report to a timestamped file in the reports directory at the root of compliance-check."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"compliance_report_{timestamp}.txt"

        try:
            file_path = ReportHandler.__determine_file_path(file_name)

            with open(file_path, "w") as file:
                file.write(content)

            print(f"Compliance report saved to {file_path}")
        except Exception as e:
            print(f"Error saving report to file: {e}", file=sys.stderr)

    @staticmethod
    def __determine_file_path(file_name: str) -> str:
        """Determine the path to the reports directory relative to this file."""
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")

        os.makedirs(reports_dir, exist_ok=True)

        return os.path.join(reports_dir, file_name)
