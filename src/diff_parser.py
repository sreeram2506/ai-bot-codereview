import re
from typing import List, Dict, Tuple

class DiffParser:
    @staticmethod
    def parse(diff_text: str) -> Dict[str, List[Tuple[int, str]]]:
        """
        Parses a unified diff string and returns a dictionary where:
        - Key: File path
        - Value: List of tuples (line_number, line_content) for added/modified lines.
        
        We only care about lines added in the new version for inline comments.
        """
        changes = {}
        current_file = None
        current_line_number = 0
        
        # Regex to capture the new file path from lines like "+++ b/path/to/file.py"
        file_header_pattern = re.compile(r'^\+\+\+ b/(.*)')
        # Regex to capture chunk headers like "@@ -1,5 +1,5 @@"
        chunk_header_pattern = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@')

        lines = diff_text.split('\n')
        
        for line in lines:
            # Check for file header
            file_match = file_header_pattern.match(line)
            if file_match:
                current_file = file_match.group(1)
                changes[current_file] = []
                continue
            
            # Check for chunk header
            chunk_match = chunk_header_pattern.match(line)
            if chunk_match:
                current_line_number = int(chunk_match.group(1))
                continue
            
            # Process content lines
            if current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    # Added line
                    content = line[1:] # Remove the '+'
                    changes[current_file].append((current_line_number, content))
                    current_line_number += 1
                elif line.startswith(' ') or (line.startswith('-') and not line.startswith('---')):
                    # Context line or removed line (removed lines don't increment new file line number, 
                    # but context lines do)
                    if not line.startswith('-'):
                         current_line_number += 1
                
                # We ignore lines starting with '-' for line counting purposes in the NEW file,
                # except to note that they don't advance the new file's line counter.
                
        return changes
