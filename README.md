# URL Document Downloader

A Python script that downloads documents from web pages. It can process a single URL or multiple URLs from a text file, detect documents, and allow selective downloading through an interactive interface.

## Features

- Process single URL via command line or multiple URLs from a text file
- Detect documents based on MIME types and file extensions
- Interactive document selection with checkbox interface
- Filter documents by name
- Select/deselect all documents with one click
- Configurable output directory via environment variables
- Progress feedback during downloads

## Directory Structure 

```
url_downloader/
├── document_downloader.py    # Main script
├── requirements.txt         # Python dependencies
├── urls.txt                # (Optional) List of URLs to process
├── .env                    # Environment configuration
└── output/                 # Downloaded documents directory
```

## Environment Configuration

Create a `.env` file in the project root:
OUTPUT_DIR=/path/to/your/download/folder


## Installation

1. Clone the repository:

```bash
git clone https://github.com/j-chacko/url_downloader.git
cd url_downloader
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create and configure the `.env` file with your preferred output directory

## Usage

### Single URL
```bash
python document_downloader.py "https://example.com/documents"
```

### Multiple URLs
1. Create a `urls.txt` file with one URL per line
2. Run the script:

```bash
python document_downloader.py
```

### Interactive Selection
- Use arrow keys to navigate
- Press SPACE to select/deselect documents
- Use the filter to search for specific documents
- Select "*** SELECT/DESELECT ALL ***" to toggle all documents
- Press ENTER to confirm selection and start downloading

## Requirements

- Python 3.6+
- Required packages (installed via requirements.txt):
  - requests
  - beautifulsoup4
  - python-dotenv
  - questionary

## License

This project is licensed under the MIT License - see the LICENSE file for details.