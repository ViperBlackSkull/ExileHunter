# Path of Exile 2 Trade Parser

## Overview
This Python script parses the Path of Exile 2 trade website to find items that cannot currently be filtered using the built-in search filters. It then exports the results to a file for easy manual searching and review.

## Features
- Parses the official Path of Exile 2 trade website.
- Identifies items that cannot be filtered with the current search options.
- Exports parsed data to a structured file format (CSV)

## Prerequisites
Before running the script, ensure you have the following:
- Python 3.8 or higher installed.
- Required Python libraries 

## Installation
1. Clone this repository or download the script:
   ```bash
   git clone https://github.com/ViperBlackSkull/ExileHunter
   cd ExileHunter
   ```

2. Install the dependencies as mentioned above.

## Usage
1. Run the script with:
   ```bash
   python hunter.py -s "Heroic Tragedy"
   ```

2. Follow any prompts to configure the search criteria (if applicable).

3. The script will generate an export file in the output directory (exemlpe: `Megalomaniac_2025-01-13.csv`).


## Limitations
- The script relies on the structure of the Path of Exile 2 trade website, which may change over time. Regular updates may be required.
- Advanced filtering logic depends on understanding the website's HTML and JavaScript.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer
This script is for educational purposes only. Use it responsibly and adhere to Path of Exile's terms of service.

---

## Item Supported
Currently tested with the following items
- Against the Darkness
- Megalomaniac
- Heroic Tragedy


## Improvement

Let me know in an issue if you would like the tool to support something else!

Happy hunting, Exile!
