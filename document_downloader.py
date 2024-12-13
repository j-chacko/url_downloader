import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import os
from typing import List, Dict
import sys
from dotenv import load_dotenv
import questionary

class DocumentDownloader:
    def __init__(self, output_dir: str = None):
        """Initialize with output directory path"""
        load_dotenv()  # Load environment variables
        self.output_dir = output_dir or os.getenv('OUTPUT_DIR', 'downloaded_documents')
        self.session = requests.Session()
        
    def get_document_links(self, url: str) -> Dict[str, str]:
        """Extract document links from the given URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a')
            
            # Filter for document links and create a dictionary
            doc_links = {}
            for link in links:
                href = link.get('href')
                if href and self._is_document_link(href):
                    full_url = urljoin(url, href)
                    filename = unquote(os.path.basename(href))
                    doc_links[filename] = full_url
                    
            return doc_links
            
        except requests.RequestException as e:
            print(f"Error accessing URL {url}: {e}")
            return {}

    def _is_document_link(self, href: str) -> bool:
        """Check if the link leads to a document by making a HEAD request"""
        try:
            # Make HEAD request to check content type without downloading
            response = self.session.head(href, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '').lower()
            
            # If it's HTML, it's not a document
            if 'text/html' in content_type:
                return False
            
            # Common document MIME types (as a safeguard)
            document_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument',
                'application/vnd.ms-excel',
                'application/vnd.ms-powerpoint',
                'application/zip',
                'application/x-rar-compressed'
            ]
            
            return any(doc_type in content_type for doc_type in document_types)
            
        except requests.RequestException:
            # If we can't check the content type, fall back to extension checking
            doc_extensions = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar')
            return href.lower().endswith(doc_extensions)

    def download_documents(self, doc_links: Dict[str, str], selected_docs: List[str] = None):
        """Download selected documents"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # If no specific documents selected, download all
        if selected_docs is None:
            selected_docs = list(doc_links.keys())

        for filename in selected_docs:
            if filename not in doc_links:
                print(f"Skipping {filename} - not found in links")
                continue

            url = doc_links[filename]
            output_path = os.path.join(self.output_dir, filename)
            
            try:
                print(f"Downloading {filename}...")
                response = self.session.get(url, stream=True)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                print(f"Successfully downloaded {filename}")
                
            except requests.RequestException as e:
                print(f"Error downloading {filename}: {e}")
            except IOError as e:
                print(f"Error saving {filename}: {e}")

def main():
    # Check if URL is provided as command line argument
    if len(sys.argv) > 1:
        urls = [sys.argv[1]]
    else:
        # Check for urls.txt file
        try:
            with open('urls.txt', 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Please provide a URL as command line argument or create a urls.txt file")
            return

    downloader = DocumentDownloader()
    
    for url in urls:
        print(f"\nProcessing URL: {url}")
        doc_links = downloader.get_document_links(url)
        
        if not doc_links:
            print("No documents found at this URL")
            continue
            
        # Display available documents with checkboxes
        choices = [
            {
                'name': '*** SELECT/DESELECT ALL ***',  # Special option to toggle all
                'value': 'ALL',
                'checked': False
            }
        ] + [
            {
                'name': f"{filename} ({url})",
                'value': filename,
                'checked': False
            }
            for filename, url in doc_links.items()
        ]
        
        # Allow filtering documents
        filter_query = questionary.text(
            "Enter text to filter documents (press Enter to show all):"
        ).ask()
        
        if filter_query:
            # Keep the "SELECT ALL" option and filter the rest
            filtered_choices = [choices[0]] + [
                choice for choice in choices[1:] 
                if filter_query.lower() in choice['name'].lower()
            ]
            choices = filtered_choices
        
        selected_docs = questionary.checkbox(
            'Select documents to download (space to select, enter to confirm):',
            choices=choices,
            validate=lambda x: len(x) > 0 or 'Please select at least one document'
        ).ask()
        
        if selected_docs:
            # If 'ALL' is selected, download everything
            if 'ALL' in selected_docs:
                selected_docs = list(doc_links.keys())
            else:
                # Remove 'ALL' from selection if it exists
                selected_docs = [doc for doc in selected_docs if doc != 'ALL']
                
            downloader.download_documents(doc_links, selected_docs)

if __name__ == "__main__":
    main() 