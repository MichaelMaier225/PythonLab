import os
import shutil

# Define source and destination directories
test_source_dir = r"C:\Users\Micha\OneDrive\Desktop\Work Test\EXT- PHOTOS"
test_destination_dir = r"C:\Users\Micha\OneDrive\Desktop\Work Test\EXT- PHOTOS UPDATED"

# Ensure the destination directory exists
os.makedirs(test_destination_dir, exist_ok=True)

# Iterate through each folder in the test source directory
for folder_name in os.listdir(test_source_dir):
    folder_path = os.path.join(test_source_dir, folder_name)

    if os.path.isdir(folder_path):  # Ensure it's a folder
        files = sorted(os.listdir(folder_path))  # Sort files for sequential numbering

        # Format folder name: lowercase, replace spaces/hyphens with underscores
        sanitized_folder_name = folder_name.lower().replace(" ", "_").replace("-", "_")

        for index, file_name in enumerate(files, start=1):
            file_ext = os.path.splitext(file_name)[1]  # Get file extension
            original_file_name = os.path.splitext(file_name)[0]  # Extract name without extension

            # Construct new filename: foldername_existingfilename_1.jpg
            new_file_name = f"{sanitized_folder_name}_{original_file_name}_{index}{file_ext}"

            src_file_path = os.path.join(folder_path, file_name)
            dest_file_path = os.path.join(test_destination_dir, new_file_name)

            # Move and rename the file
            try:
                shutil.move(src_file_path, dest_file_path)
                print(f"Moved: {src_file_path} -> {dest_file_path}")
            except Exception as e:
                print(f"Error moving {src_file_path}: {e}")

print("Process complete. Check the 'EXT-PHOTOS UPDATED' folder is updated.")
