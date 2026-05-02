# The robust importer should use lenient validation for import
# - cost_price is optional (defaults to price_workshop)
# - brand is optional
# - Sheets with insufficient data should still be imported with what's available
# - status should not be mapped to a database field

print("Key issues to fix:")
print("1. cost_price is required but should be optional (derivable from price_workshop)")
print("2. 'company' column maps to both 'name' and 'brand' - causes name field to be 'company' instead of actual product name")
print("3. Validation fails sheets instead of allowing partial imports")
print("4. 'status' field shouldn't map to a DB field")
print("\nSolutions:")
print("- Make cost_price optional in schema")
print("- Fix column priority: name > brand > category, so 'company' maps to brand, not name")
print("- Change validation: warn on missing fields, don't fail")
print("- Don't map 'status' column to any DB field")
