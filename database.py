"""Database connection and operations for the warehouse scheduler."""

import chromadb
import json
import re
import Levenshtein
from typing import Dict, List, Any, Optional
from config import DB_PATH, ROLE_MAPPINGS

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=DB_PATH)
employee_collection = chroma_client.get_or_create_collection(name="employees")

def normalize_role(role: str) -> str:
    """
    Normalize role names for consistent matching.
    
    Args:
        role: Role name to normalize
        
    Returns:
        Normalized role name
    """
    role = role.lower().strip()
    # Remove trailing 's' if present (e.g., "drivers" -> "driver")
    role = re.sub(r's$', '', role)  
    # Replace spaces with underscores for consistency
    role = re.sub(r'\s+', '_', role)
    return role

def retrieve_employees(required_roles: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve employees from the database based on required roles.
    
    Args:
        required_roles: Dictionary of required roles (can be nested or flattened)
        
    Returns:
        Dictionary of employees by role
    """
    try:
        matched_employees = {}
        
        # Get all employees from the collection
        all_employees = employee_collection.get()
        if not all_employees or not all_employees.get("metadatas"):
            print("No employees found in database")
            return matched_employees
            
        # Handle both nested and flattened role structures
        roles_to_process = {}
        for key, value in required_roles.items():
            if isinstance(value, dict):
                # Nested structure
                for role, count in value.items():
                    roles_to_process[role] = count
            else:
                # Flattened structure
                roles_to_process[key] = value
                
        # Match employees to required roles
        for role, _ in roles_to_process.items():
            role_key = role
            matched_employees[role_key] = []
            
            # Create list of possible role names to search for
            role_search_terms = []
            
            # Handle composite role names (e.g., 'inbound_forklift_driver' -> 'forklift_driver')
            if '_' in role:
                base_role = role.split('_', 1)[-1]  # Get everything after the first underscore
                role_search_terms.extend(ROLE_MAPPINGS.get(base_role, []))
            
            # Also search using the full role name
            role_search_terms.extend(ROLE_MAPPINGS.get(role, []))
            
            # Add the role itself as a search term
            role_search_terms.append(role.lower())
            
            for i, metadata in enumerate(all_employees["metadatas"]):
                if not is_employee_available(metadata):
                    continue
                
                # Get the employee's job title
                job_title = metadata.get('original_job_title', '').lower()
                normalized_job_title = metadata.get('normalized_job_title', '').lower()
                
                # Check if employee's job title matches any of the role search terms
                matched = False
                for search_term in role_search_terms:
                    if (search_term.lower() in job_title or 
                        search_term.lower() in normalized_job_title or
                        job_title in search_term.lower() or
                        normalized_job_title in search_term.lower()):
                        employee = {
                            'id': all_employees["ids"][i],
                            **metadata
                        }
                        matched_employees[role_key].append(employee)
                        matched = True
                        break
                
                if matched:
                    continue
                        
        return matched_employees
        
    except Exception as e:
        print(f"Error retrieving employees: {str(e)}")
        return {}

def is_employee_available(metadata: Dict[str, Any]) -> bool:
    """
    Check if an employee is available for scheduling based on their metadata.
    
    Args:
        metadata: Employee metadata from ChromaDB
        
    Returns:
        bool: True if employee is available, False otherwise
    """
    try:
        # Check if employee is active
        if not metadata.get("active", True):
            return False
        
        # Check if employee is on leave
        if metadata.get("on_leave", False):
            return False
        
        # Check shift preferences if available
        shift_preferences = metadata.get("shift_preferences", "")
        if shift_preferences and "day" not in shift_preferences:
            return False
        
        return True
        
    except Exception:
        return False

def find_best_match(name: str, employee_list: List[str]) -> Optional[str]:
    """
    Find the best matching employee name using fuzzy matching.
    
    Args:
        name: Name to search for
        employee_list: List of employee IDs to search within
        
    Returns:
        Best matching employee ID or None if no good match found
    """
    best_match = None
    best_score = float('inf')  # Lower is better for Levenshtein distance
    
    name_lower = name.lower()
    
    for emp_id in employee_list:
        # Get name variations
        try:
            emp_data = employee_collection.get(ids=[emp_id])
            if not emp_data or not emp_data["metadatas"]:
                continue
            
            metadata = emp_data["metadatas"][0]
            name_variations_json = metadata.get("name_variations", "[]")
            name_variations = json.loads(name_variations_json)
            
            # If no variations stored, use the ID
            if not name_variations:
                name_variations = [emp_id]
            
            # Try all variations and find the best match
            for variation in name_variations:
                variation_lower = variation.lower()
                
                # Exact match
                if name_lower == variation_lower:
                    return emp_id
                
                # Calculate Levenshtein distance
                distance = Levenshtein.distance(name_lower, variation_lower)
                if distance < best_score:
                    best_score = distance
                    best_match = emp_id
        except Exception as e:
            print(f"Error in name matching for {emp_id}: {e}")
    
    # Only return a match if the score is below a threshold (30% of name length)
    if best_score <= len(name) * 0.3:
        return best_match
    return None

def get_employee_details(emp_id: str) -> Dict[str, Any]:
    """
    Get employee details from the database.
    
    Args:
        emp_id: Employee ID
        
    Returns:
        Dictionary containing employee details
    """
    try:
        emp_data = employee_collection.get(ids=[emp_id])
        if not emp_data or not emp_data["metadatas"]:
            return {}
        
        return emp_data["metadatas"][0]
    except Exception as e:
        print(f"Error getting employee details: {e}")
        return {}