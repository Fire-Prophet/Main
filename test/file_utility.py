import os
import shutil
import datetime

class FileUtility:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            print(f"Created base directory: {self.base_dir}")

    def create_directory(self, dir_name):
        """Creates a new directory if it doesn't exist."""
        path = os.path.join(self.base_dir, dir_name)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Directory '{dir_name}' created at {path}")
                return True
            else:
                print(f"Directory '{dir_name}' already exists at {path}")
                return False
        except OSError as e:
            print(f"Error creating directory '{dir_name}': {e}")
            return False

    def create_dummy_file(self, file_name, size_kb=10, content="Dummy content line.\n"):
        """Creates a dummy file with specified size and content."""
        path = os.path.join(self.base_dir, file_name)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                num_lines = int(size_kb * 1024 / len(content.encode('utf-8'))) # Calculate lines needed for size
                for _ in range(num_lines):
                    f.write(content)
            print(f"Dummy file '{file_name}' ({size_kb}KB) created at {path}")
            return True
        except IOError as e:
            print(f"Error creating dummy file '{file_name}': {e}")
            return False

    def list_directory_contents(self, target_dir="."):
        """Lists files and directories within a specified path."""
        path = os.path.join(self.base_dir, target_dir)
        if not os.path.exists(path):
            print(f"Error: Directory '{target_dir}' not found at {path}")
            return []
        print(f"\n--- Contents of '{target_dir}' ({path}) ---")
        contents = os.listdir(path)
        if not contents:
            print("  (Empty directory)")
        for item in contents:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print(f"  [DIR] {item}")
            else:
                file_size = os.path.getsize(item_path)
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"  [FILE] {item} ({file_size} bytes, last modified: {mod_time})")
        print("----------------------------------------\n")
        return contents

    def delete_path(self, path_to_delete):
        """Deletes a file or an empty directory."""
        full_path = os.path.join(self.base_dir, path_to_delete)
        if not os.path.exists(full_path):
            print(f"Path '{path_to_delete}' does not exist.")
            return False
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
                print(f"File '{path_to_delete}' deleted.")
            elif os.path.isdir(full_path):
                # Only delete empty directories for safety, use shutil.rmtree for non-empty
                if not os.listdir(full_path):
                    os.rmdir(full_path)
                    print(f"Empty directory '{path_to_delete}' deleted.")
                else:
                    print(f"Directory '{path_to_delete}' is not empty. Use delete_recursive for full deletion.")
                    return False
            return True
        except OSError as e:
            print(f"Error deleting '{path_to_delete}': {e}")
            return False

    def delete_recursive(self, path_to_delete):
        """Deletes a directory and all its contents recursively."""
        full_path = os.path.join(self.base_dir, path_to_delete)
        if not os.path.exists(full_path):
            print(f"Path '{path_to_delete}' does not exist.")
            return False
        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
                print(f"Directory '{path_to_delete}' and its contents deleted recursively.")
                return True
            elif os.path.isfile(full_path):
                os.remove(full_path)
                print(f"File '{path_to_delete}' deleted.")
                return True
        except OSError as e:
            print(f"Error deleting '{path_to_delete}' recursively: {e}")
            return False

if __name__ == "__main__":
    # Ensure a test directory exists for operations
    test_base = "file_utility_test_dir"
    if os.path.exists(test_base):
        shutil.rmtree(test_base) # Clean up previous test run
    os.makedirs(test_base)
    print(f"Created test base directory: {test_base}")

    utility = FileUtility(test_base)

    utility.create_directory("reports")
    utility.create_directory("temp")
    utility.create_dummy_file("test_data.txt", size_kb=5)
    utility.create_dummy_file("temp/log.txt", size_kb=2)

    utility.list_directory_contents()
    utility.list_directory_contents("temp")

    utility.delete_path("test_data.txt")
    utility.list_directory_contents()

    # Clean up the test directory at the end
    # Note: Cannot delete 'temp' with delete_path because it's not empty
    print("\nCleaning up test directories...")
    utility.delete_recursive("temp")
    utility.delete_recursive("reports")
    utility.delete_recursive(".") # Delete the base test directory itself
    print("Cleanup complete.")
