import sys
from pathlib import Path
from pprint import pprint

# Ensure src module can be imported
sys.path.append(str(Path(__file__).parent))

from src.parser import parse_unsc_xml

def run_milestone1_verification(xml_file_path):
    print(f"--- Running Milestone 1 Verification ---")
    print(f"Target File: {xml_file_path}\n")

    sync_run_id = "UNSC_MILESTONE1_TEST"
    
    # Run Parser
    documents = parse_unsc_xml(xml_file_path, sync_run_id=sync_run_id)

    # Count breakdown
    individual_count = sum(1 for doc in documents if doc["record_type"] == "INDIVIDUAL")
    entity_count = sum(1 for doc in documents if doc["record_type"] == "ENTITY")
    total_count = len(documents)

    print("========================================")
    print(f" Individual Count : {individual_count}")
    print(f" Entity Count     : {entity_count}")
    print(f" Total Records    : {total_count}")
    print("========================================\n")

    # Verify document structure samples
    if individual_count > 0:
        sample_ind = next(doc for doc in documents if doc["record_type"] == "INDIVIDUAL")
        print("--- Sample Individual Document ---")
        pprint(sample_ind)
        print("\n" + "-"*40 + "\n")

    if entity_count > 0:
        sample_ent = next(doc for doc in documents if doc["record_type"] == "ENTITY")
        print("--- Sample Entity Document ---")
        pprint(sample_ent)
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    # Point this to your local UNSC XML file path
    xml_path = "data/raw/unsc_consolidated_list_2026-08-25.xml" 
    
    if Path(xml_path).exists():
        run_milestone1_verification(xml_path)
    else:
        print(f"Error: File '{xml_path}' not found. Place your UNSC XML file there and rerun.")