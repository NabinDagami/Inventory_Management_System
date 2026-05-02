# Fix the _validate_sheet method - remove print from docstring
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and fix the method
for i, line in enumerate(lines):
    if 'def _validate_sheet(self, excel_file: pd.ExcelFile, sheet_name: str) -> Dict[str, Any]:' in line:
        # The docstring spans lines i+1 through i+3 (with the print in it)
        # Replace with proper docstring then add print statement
        indent = ' ' * 8
        
        # Build new lines: method def, docstring, print, then rest
        new_section = [
            '    def _validate_sheet(self, excel_file: pd.ExcelFile, sheet_name: str) -> Dict[str, Any]:\n',
            '        """\n',
            '        Validate individual sheet structure and data\n',
            '        """\n',
            f'        print(f"  [VALIDATE_SHEET] Processing: {{sheet_name}}")\n',
        ]
        
        # Find where the docstring ends and actual code starts
        # Line i+1 is '"""'
        # Line i+2 is empty
        # Line i+3 has the print
        # Line i+4 has the rest of docstring
        # Line i+5 is '"""'
        # Line i+6 is 'sheet_result = {'
        
        # Find the closing """ of the docstring
        for j in range(i+1, min(i+10, len(lines))):
            if lines[j].strip() == 'sheet_result = {':
                # Replace lines i+1 through j-1 with new_section
                new_lines = lines[:i+1] + new_section + lines[j:]
                break
        else:
            print('Could not find sheet_result line')
            new_lines = lines
        
        with open('robust_importer.py', 'w') as f:
            f.writelines(new_lines)
        
        print('Fixed _validate_sheet method')
        break
