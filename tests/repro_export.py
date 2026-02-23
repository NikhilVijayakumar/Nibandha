import sys
import shutil
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

# Add src to path
project_root = Path("e:/Python/Nibandha")
sys.path.append(str(project_root / "src"))

try:
    from nibandha.reporting.shared.application.orchestration.steps.export_step import ExportStep
    from nibandha.reporting.shared.application.context import ReportingContext
    from nibandha.export.application.export_service import ExportService
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_export_step_call_signature():
    """ Verify ExportStep calls export_unified_report with correct signature """
    print("\n--- Testing ExportStep Signature ---")
    
    # Mock Context
    context = MagicMock(spec=ReportingContext)
    context.output_dir = Path("mock_output")
    context.export_formats = ["html", "docx"]
    context.project_name = "Test Project"
    context.data = {}
    context.timings = {}
    
    # Create fake methods for visualization to support ExportStep execution
    context.viz_provider = MagicMock()
    
    # Mock ExportService with autospec to enforce signature check
    service_mock = create_autospec(ExportService, instance=True, spec_set=True)
    context.export_service = service_mock
    
    # Setup mock directories within current dir
    temp_dir = Path("repro_temp_output")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    context.output_dir = temp_dir
    (temp_dir / "details").mkdir(parents=True, exist_ok=True)
    (temp_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    
    # Create a dummy report file so ExportStep has something to do
    # Using specific name that ExportStep looks for
    (temp_dir / "details" / "introduction.md").touch() # REPORT_FILENAME_INTRO likely matches this? 
    # Actually constants defined in step: REPORT_FILENAME_INTRO
    # I don't know the constant value, but ExportStep imports it.
    # Let's inspect the step to see what filenames it uses.
    # It imports from nibandha.reporting.shared.constants
    # Mock files to match standard names to ensure list is populated
    from nibandha.reporting.shared.constants import REPORT_FILENAME_INTRO
    (temp_dir / "details" / REPORT_FILENAME_INTRO).touch()
    
    step = ExportStep()
    
    result = False
    
    try:
        step.execute(context)
        print("ExportStep executed successfully (Unexpected if signature is wrong)")
        
        # Check call args manually if no exception
        if service_mock.export_unified_report.called:
            args = service_mock.export_unified_report.call_args
            # format: call(summary_path, detail_paths, output_dir, formats, project_info)
            # real signature: (self, summary_path, detail_paths, project_info=None, metrics_loader=None)
            passed_args = args[0] # positional args
            passed_kwargs = args[1] # kwargs
            
            print(f"Called with args: {passed_args}")
            print(f"Called with kwargs: {passed_kwargs}")
            
            # ExportStep passes 5 positional args
            if len(passed_args) == 5:
                print("Confirmed: ExportStep passes 5 args. ExportService expects 4.")
                result = True
            else:
                print("ExportStep passes compatible number of args?")
                
    except TypeError as e:
        print(f"Caught Expected TypeError: {e}")
        result = True
    except Exception as e:
        print(f"Caught Unexpected Exception: {type(e).__name__}: {e}")
        # raise # Don't raise, let verify logic check
    finally:
       if temp_dir.exists():
           shutil.rmtree(temp_dir)

    return result

def check_file_discovery_logic():
    pass # Will implement later if needed, but signature check is key first.
    return True

if __name__ == "__main__":
    sig_result = test_export_step_call_signature()
    
    if sig_result:
        print("\nOVERALL: Reproduction confirmed (Signature mismatch detected).")
    else:
        print("\nOVERALL: Failed to detect signature mismatch.")
