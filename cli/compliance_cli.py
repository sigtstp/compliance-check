import cmd
import sys
from services.analysis_service import AnalysisService
from clients.analysis_client import ModelAPIError
from helpers.report_handler import ReportHandler


class ComplianceCLI(cmd.Cmd):
    """Command-line interface for the Compliance Checker application."""
    intro = 'Welcome to the Compliance Checker.\nType "help" or "?" to list commands.\n'
    prompt = "(compliance) "

    def __init__(self, analysis_service: AnalysisService):
        super().__init__()
        self.__service = analysis_service

    def cmdloop(self, intro=None):
        """Override cmdloop to handle CTRL+C gracefully without crashing."""
        if intro is not None:
            self.intro = intro
        if self.intro:
            print(self.intro, end="")

        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")

    def do_story(self, arg: str):
        """Analyze an Azure DevOps User Story by ID:
        Example: story 1234
        """
        if not arg:
            print("Error: Please provide a story ID.", file=sys.stderr)
            return

        try:
            report = self.__service.analyze_user_story(arg)
            
            ReportHandler.handle(report)
        except Exception as e:
            print(f"Error analyzing story: {e}", file=sys.stderr)

    def do_text(self, arg: str):
        """Analyze raw text requirements:
        Example: text The system shall allow users to upload profile pictures.
        """
        if not arg:
            print("Error: Please provide text to analyze.", file=sys.stderr)
            return

        try:
            raw_report = self.__service.analyze_requirements(arg)
            
            ReportHandler.handle(raw_report)
        except ModelAPIError as e:
            print(f"API Error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error analyzing text: {e}", file=sys.stderr)

    def do_exit(self, arg: str):
        """Exit the interactive application."""
        print("Exiting Compliance Checker...")
        
        # Returning True stops the command loop
        return True

    def do_quit(self, arg: str):
        """Alias for exit."""
        
        return self.do_exit(arg)

    def do_q(self, arg: str):
        """Alias for exit."""
        
        return self.do_exit(arg)

    def do_EOF(self, arg: str):
        """Exit on EOF (Ctrl+D)"""
        print()

        return True
