import sys
import os

# Check for filename argument
if len(sys.argv) != 2:
    print("Usage: python reorder_rows.py <filename>")
    sys.exit(1)

input_filename = sys.argv[1]

# Check if file exists
if not os.path.isfile(input_filename):
    print(f"File '{input_filename}' not found.")
    sys.exit(1)

# Step 1: Read lines from the file
with open(input_filename, "r") as file:
    lines = file.readlines()

# Step 2: Define your 1-based row mapping (can be edited)
row_mapping = {
    57: 65,
    58: 69,
    59: 67,
    60: 68,
    61: 59,
    62: 61,
    63: 64,
    64: 63,
    65: 62,
    66: 58,
    67: 57,
    68: 66,
    69: 60
}

# Step 3: Convert to 0-based indexing
mapping_0_based = {k : v for k, v in row_mapping.items()}

# Step 4: Apply the mapping to reorder rows
reordered_lines = lines.copy()
print(lines[57:])

for from_idx, to_idx in mapping_0_based.items():
    # Check if indices are within bounds
    if from_idx >= len(lines) or to_idx >= len(lines):
        print(f"Skipping invalid mapping: {from_idx+1} → {to_idx+1} (out of bounds)")
        continue
    print(lines[from_idx]," Changing to " ,reordered_lines[to_idx])

    reordered_lines[to_idx] = lines[from_idx]

# Step 5: Write output to a new file
output_filename = f"{os.path.basename(input_filename)}"
with open(output_filename, "w") as file:
    file.writelines(reordered_lines)

print(f"✅ Rows reordered and saved to '{output_filename}'")
