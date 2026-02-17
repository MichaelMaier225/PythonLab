import os
import shutil  # Used to copy files from one folder to another

# This is the main folder that contains all your building folders (e.g., 0461, 0505)
PARENT_DIR = r"C:\Users\Micha\OneDrive\Desktop\Work Test"

# Function to check if the folder is EXT- PHOTOS, even with spacing/case differences
def is_ext_photos_folder(name: str) -> bool:
    return name.replace(" ", "").lower() == "ext-photos"

# Function to sanitize folder names to use them safely in filenames
def sanitize_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")

# This function handles the photos in EXT- PHOTOS
def process_ext_photos(building_path: str, ext_photos_path: str):
    updated_photos_path = os.path.join(building_path, "EXT- PHOTOS UPDATED")
    os.makedirs(updated_photos_path, exist_ok=True)  # Create the updated folder if it doesn’t exist

    for root, _, files in os.walk(ext_photos_path):
        if not files:
            continue  # Skip empty folders

        subfolder_name = os.path.basename(root)  # Get the name of the current subfolder
        sanitized = sanitize_name(subfolder_name)  # Sanitize the subfolder name

        # Loop through each file in the subfolder
        for index, file_name in enumerate(sorted(files), start=1):
            file_ext = os.path.splitext(file_name)[1]  # Get the file extension (e.g., .jpg)
            base_name = os.path.splitext(file_name)[0]  # Get the name without the extension
            new_name = f"{sanitized}_{base_name}_{index}{file_ext}"  # Format the new filename

            src = os.path.join(root, file_name)  # Get the full path of the source file
            dst = os.path.join(updated_photos_path, new_name)  # Define the destination path for the renamed file

            try:
                shutil.copy2(src, dst)  # Copy the file to the new location (keeps the original intact)
                print(f"📁 Copied: {src} -> {dst}")  # Log the action
            except Exception as e:
                print(f"❌ Error copying {src}: {e}")  # If something goes wrong, show the error

# Main function that controls everything
def main():
    for building_folder in os.listdir(PARENT_DIR):
        building_path = os.path.join(PARENT_DIR, building_folder)
        if not os.path.isdir(building_path):
            continue  # Skip if it's not a folder

        ext_photos_path = None  # This will store the path to EXT- PHOTOS folder

        # Look for the EXT- PHOTOS folder (even if spacing is different)
        for item in os.listdir(building_path):
            candidate = os.path.join(building_path, item)
            if os.path.isdir(candidate) and is_ext_photos_folder(item):
                ext_photos_path = candidate
                break  # Stop looking once we find it

        if not ext_photos_path:
            print(f"⚠️ No EXT- PHOTOS folder found in: {building_folder}")
            continue  # Skip this building if no EXT- PHOTOS folder

        process_ext_photos(building_path, ext_photos_path)  # Process the photos

    print("\n✅ ALL buildings processed. Original photos are preserved in EXT- PHOTOS.")

if __name__ == "__main__":
    main()
