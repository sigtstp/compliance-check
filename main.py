import sys
from dotenv import load_dotenv
from cli.compliance_cli import ComplianceCLI
from services.analysis_service import AnalysisService
from clients.analysis_client import AnalysisClient


def main():
    # Load configuration from .env file
    load_dotenv()

    try:
        # Configure Dependency Injection
        client = AnalysisClient()
        service = AnalysisService(client)
        app = ComplianceCLI(service)

        # Start the application
        app.cmdloop()

    except Exception as e:
        print(f"A fatal error occurred during startup: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
