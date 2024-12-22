import subprocess
import logging

def get_last_release_tag() -> str:
    """Get the most recent release tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting last release tag: {e}")
        return None

def get_changes_since_last_release(last_release_tag: str) -> str:
    """Get the commit messages since the last release."""
    try:
        result = subprocess.run(
            ["git", "log", f"{last_release_tag}..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting changes: {e}")
        return None

def main():
    """Main function to get and print changes."""
    logging.basicConfig(level=logging.DEBUG)
    last_release_tag = get_last_release_tag()
    if not last_release_tag:
        print("Could not determine last release tag.")
        return
    
    print(f"Last release tag: {last_release_tag}")
    
    changes = get_changes_since_last_release(last_release_tag)
    if changes:
        print("\nCommit messages since last release:\n")
        print(changes)
    else:
        print("No changes found since last release.")

if __name__ == "__main__":
    main()
