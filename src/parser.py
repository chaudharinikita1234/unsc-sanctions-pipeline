import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# -------------------------------------------------------------------
# Helper Parsing Functions
# -------------------------------------------------------------------

def get_text(element):
    """
    Safely extracts and cleans text from an XML element.
    Handles self-closing tags (<COUNTRY/>) as None and strips whitespace.
    """
    if element is None or element.text is None:
        return None
    
    cleaned = element.text.strip()
    return cleaned if cleaned else None


def parse_text(parent_element, tag_name):
    """Safely extracts child elements using get_text()."""
    if parent_element is None:
        return None
    child = parent_element.find(tag_name)
    return get_text(child)


def parse_value_list(element, container_tag):
    """
    Extracts lists of <VALUE> strings (e.g., nationalities, designations, titles).
    ALWAYS returns a list/array: [], ["India"], or ["India", "Pakistan"].
    """
    if element is None:
        return []
    
    container = element.find(container_tag)
    if container is None:
        return []
    
    values = []
    for val in container.findall("VALUE"):
        val_text = get_text(val)
        if val_text:
            values.append(val_text)
            
    return values


# -------------------------------------------------------------------
# Parser Logic for INDIVIDUAL Records
# -------------------------------------------------------------------

def parse_individual(ind_elem, source_generated_at=None, sync_run_id=None):
    """Parses an <INDIVIDUAL> XML element into the standard MongoDB individual document schema."""
    name_obj = {
        "first": parse_text(ind_elem, "FIRST_NAME"),
        "second": parse_text(ind_elem, "SECOND_NAME"),
        "third": parse_text(ind_elem, "THIRD_NAME"),
        "fourth": parse_text(ind_elem, "FOURTH_NAME"),
        "original_script": parse_text(ind_elem, "NAME_ORIGINAL_SCRIPT")
    }

    aliases = []
    for alias in ind_elem.findall("INDIVIDUAL_ALIAS"):
        aliases.append({
            "quality": parse_text(alias, "QUALITY"),
            "name": parse_text(alias, "ALIAS_NAME"),
            "note": parse_text(alias, "NOTE")
        })

    dobs = []
    for dob in ind_elem.findall("INDIVIDUAL_DATE_OF_BIRTH"):
        year_val = parse_text(dob, "YEAR")
        dobs.append({
            "type": parse_text(dob, "TYPE_OF_DATE"),
            "date": parse_text(dob, "DATE"),
            "year": int(year_val) if year_val and year_val.isdigit() else None,
            "from_year": parse_text(dob, "FROM_YEAR"),
            "to_year": parse_text(dob, "TO_YEAR")
        })

    addresses = []
    for addr in ind_elem.findall("INDIVIDUAL_ADDRESS"):
        addresses.append({
            "street": parse_text(addr, "STREET"),
            "city": parse_text(addr, "CITY"),
            "state_province": parse_text(addr, "STATE_PROVINCE"),
            "country": parse_text(addr, "COUNTRY"),
            "note": parse_text(addr, "NOTE")
        })

    documents = []
    for doc in ind_elem.findall("INDIVIDUAL_DOCUMENT"):
        documents.append({
            "type": parse_text(doc, "TYPE_OF_DOCUMENT"),
            "number": parse_text(doc, "NUMBER"),
            "issuing_country": parse_text(doc, "ISSUING_COUNTRY"),
            "date_of_issue": parse_text(doc, "DATE_OF_ISSUE"),
            "note": parse_text(doc, "NOTE")
        })

    return {
        "reference_number": parse_text(ind_elem, "REFERENCE_NUMBER"),
        "data_id": parse_text(ind_elem, "DATAID"),
        "record_type": "INDIVIDUAL",
        "name": name_obj,
        "aliases": aliases,
        "dates_of_birth": dobs,
        "nationalities": parse_value_list(ind_elem, "NATIONALITY"),
        "addresses": addresses,
        "documents": documents,
        "designations": parse_value_list(ind_elem, "DESIGNATION"),
        "titles": parse_value_list(ind_elem, "TITLE"),
        "listed_on": parse_text(ind_elem, "LISTED_ON"),
        "last_day_updated": parse_value_list(ind_elem, "LAST_DAY_UPDATED"),
        "last_reviewed_on": parse_value_list(ind_elem, "LAST_REVIEWED_ON"),
        "other_information": parse_text(ind_elem, "COMMENTS1"),
        "list_type": parse_value_list(ind_elem, "UN_LIST_TYPE"),
        "metadata": {
            "source": "UNSC",
            "source_generated_at": source_generated_at,
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "sync_run_id": sync_run_id
        }
    }


# -------------------------------------------------------------------
# Parser Logic for ENTITY Records
# -------------------------------------------------------------------

def parse_entity(ent_elem, source_generated_at=None, sync_run_id=None):
    """Parses an <ENTITY> XML element into the standard MongoDB entity document schema."""
    aka_list = []
    fka_list = []
    
    for alias in ent_elem.findall("ENTITY_ALIAS"):
        quality = parse_text(alias, "QUALITY")
        alias_obj = {
            "name": parse_text(alias, "ALIAS_NAME"),
            "quality": quality,
            "note": parse_text(alias, "NOTE")
        }
        
        if quality and "fka" in quality.lower():
            fka_list.append(alias_obj)
        else:
            aka_list.append(alias_obj)

    addresses = []
    for addr in ent_elem.findall("ENTITY_ADDRESS"):
        addresses.append({
            "street": parse_text(addr, "STREET"),
            "city": parse_text(addr, "CITY"),
            "state_province": parse_text(addr, "STATE_PROVINCE"),
            "country": parse_text(addr, "COUNTRY"),
            "note": parse_text(addr, "NOTE")
        })

    return {
        "reference_number": parse_text(ent_elem, "REFERENCE_NUMBER"),
        "data_id": parse_text(ent_elem, "DATAID"),
        "record_type": "ENTITY",
        "name": parse_text(ent_elem, "FIRST_NAME"),
        "original_script": parse_text(ent_elem, "NAME_ORIGINAL_SCRIPT"),
        "aliases": {
            "also_known_as": aka_list,
            "formerly_known_as": fka_list
        },
        "addresses": addresses,
        "listed_on": parse_text(ent_elem, "LISTED_ON"),
        "last_day_updated": parse_value_list(ent_elem, "LAST_DAY_UPDATED"),
        "last_reviewed_on": parse_value_list(ent_elem, "LAST_REVIEWED_ON"),
        "other_information": parse_text(ent_elem, "COMMENTS1"),
        "list_type": parse_value_list(ent_elem, "UN_LIST_TYPE"),
        "metadata": {
            "source": "UNSC",
            "source_generated_at": source_generated_at,
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "sync_run_id": sync_run_id
        }
    }


# -------------------------------------------------------------------
# Main XML Orchestration Function
# -------------------------------------------------------------------

def parse_unsc_xml(xml_file_path, sync_run_id=None):
    """Parses full UNSC XML file and yields individual and entity MongoDB documents."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # Extract root attribute dateGenerated
    date_generated = root.attrib.get("dateGenerated")
    parsed_documents = []

    # 1. Process Individuals
    individuals_container = root.find("INDIVIDUALS")
    if individuals_container is not None:
        for ind in individuals_container.findall("INDIVIDUAL"):
            doc = parse_individual(ind, source_generated_at=date_generated, sync_run_id=sync_run_id)
            parsed_documents.append(doc)

    # 2. Process Entities
    entities_container = root.find("ENTITIES")
    if entities_container is not None:
        for ent in entities_container.findall("ENTITY"):
            doc = parse_entity(ent, source_generated_at=date_generated, sync_run_id=sync_run_id)
            parsed_documents.append(doc)

    return parsed_documents