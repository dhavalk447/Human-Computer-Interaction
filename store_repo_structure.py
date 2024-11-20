
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_urls(structure):
    """
    Recursively extract all URLs from repository structure
    
    Args:
        structure (dict): Repository structure dictionary
        
    Returns:
        list: Flat list of unique URLs
    """
    urls = set()
    
    def collect_urls(item):
        if isinstance(item, str) and item.startswith('https://'):
            urls.add(item)
        elif isinstance(item, list):
            for subitem in item:
                collect_urls(subitem)
        elif isinstance(item, dict):
            for value in item.values():
                collect_urls(value)
    
    collect_urls(structure)
    return list(urls)

def get_repository_urls(mongodb_uri, database='myDatabase', collection='repoStructures'):
    """
    Retrieve URLs for all repositories from MongoDB
    
    Args:
        mongodb_uri (str): MongoDB connection string
        database (str, optional): Database name. Defaults to 'myDatabase'
        collection (str, optional): Collection name. Defaults to 'repoStructures'
        
    Returns:
        dict: Repository names mapped to their URLs
    """
    try:
        client = MongoClient(mongodb_uri)
        db = client[database]
        repo_collection = db[collection]
        
        # Retrieve all repository documents
        repositories = repo_collection.find()
        
        # Create a dictionary to store repository URLs
        repository_urls = {}
        
        for repo_doc in repositories:
            if 'structure' in repo_doc:
                repo_name = repo_doc.get('repo', 'Unknown')
                urls = extract_urls(repo_doc['structure'])
                repository_urls[repo_name] = urls
        
        return repository_urls
    
    except Exception as e:
        print(f"Error retrieving repository URLs: {e}")
        return {}
    finally:
        client.close()

def save_urls_to_file(repository_urls, output_file='repository_urls.txt'):
    """
    Save repository URLs to a text file
    
    Args:
        repository_urls (dict): Dictionary of repository URLs
        output_file (str, optional): Output file path. Defaults to 'repository_urls.txt'
    """
    try:
        with open(output_file, 'w') as f:
            for repo, urls in repository_urls.items():
                f.write(f"Repository: {repo}
")
                for url in urls:
                    f.write(f"- {url}
")
                f.write("
")
        print(f"URLs saved to {output_file}")
    except Exception as e:
        print(f"Error saving URLs to file: {e}")

def main():
    """
    Main function to extract and save repository URLs
    """
    # Retrieve MongoDB URI from environment variable
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("Error: MONGODB_URI environment variable not set")
        return
    
    # Get repository URLs
    repository_urls = get_repository_urls(mongodb_uri)
    
    if repository_urls:
        # Print URLs to console
        for repo, urls in repository_urls.items():
            print(f"Repository: {repo}")
            for url in urls:
                print(f"- {url}")
        
        # Optional: Save URLs to a file
        save_urls_to_file(repository_urls)

if __name__ == '__main__':
    main()

