# CEVI Dataset Annotator

A data annotation tool for the Condition-Embedded Visible-Infrared image dataset.

## Dataset Overview

The Condition-Embedded Visible-Infrared image dataset for typical ground features is a dataset specifically designed for researching precise conversion from visible to infrared images. This dataset takes into account the significant impact of conditional information such as weather, temperature, and humidity on infrared imaging.

### Dataset Features

- **Weather Conditions**: Covers 5 weather types: cloudy, sunny, rainy, snowy, foggy
- **Ground Feature Types**: Includes 8 typical ground features: water, forest, grassland, beach, farmland, buildings, roads, bare land
- **Condition Information**: Precisely records meteorological parameters such as temperature and humidity at the time of data collection
- **Multi-Region Collection**: Data from multiple geographical regions, ensuring diversity and representativeness

## Features

### Data Annotation
- **Graphical Interface**: Intuitive web interface based on Gradio
- **Condition Annotation**: Supports annotation of condition information such as weather, temperature, humidity
- **Feature Classification**: Supports multi-label annotation for various ground feature types
- **Location Information**: Records latitude and longitude coordinates of shooting locations
- **Meteorological Parameters**: Complete meteorological data recording (wind direction, wind speed, pressure, visibility, etc.)

### Data Management
- **Format Conversion**: Supports mutual conversion between JSON and SQLite formats
- **Metadata Extraction**: Automatically extracts timestamp, weather, temperature and other information from filenames
- **Batch Processing**: Supports batch annotation and management of large-scale datasets
- **Data Validation**: Built-in data integrity and consistency checks

### Technical Features
- **Python Implementation**: Based on modern Python technology stack
- **Type Safety**: Uses type annotations to ensure code quality
- **Modular Design**: Clear code structure and module separation
- **Extensibility**: Easy to add new annotation fields and functions

## Installation and Usage

### Environment Requirements
- Python 3.10+
- Virtual environment recommended

### Installation Steps

1. Clone the project
```bash
git clone <repository-url>
cd CEVI-DatasetAnnotator
```

2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Annotation Tool

Start the graphical interface:
```bash
python gui.py
```

Access http://localhost:7860 to use the annotation tool.

### Data Format Conversion

Convert JSON data to SQLite database:
```bash
python convert.py
```

Convert SQLite database to JSON format:
```python
from convert import convert_to_json
convert_to_json(Path("./database.db"), Path("./output.json"))
```

## Project Structure

```
CEVI-DatasetAnnotator/
├── gui.py              # Main program for graphical user interface
├── get_file.py         # File processing and metadata extraction
├── convert.py          # Data format conversion tool
├── requirements.txt    # Python dependency list
├── LICENSE            # MIT License
└── README.md          # Project documentation
```

### Core Module Description

- **gui.py**: Web interface based on Gradio, providing image display and annotation functions
- **get_file.py**: Contains data model classes and file processing functions
  - `PicData`: Data model class containing all annotation fields
  - `Pair`: Image pair class for managing original and processed images
  - File traversal and metadata extraction functions
- **convert.py**: Data format conversion tool supporting JSON and SQLite interconversion

## Data Format

### JSON Format Example
```json
{
  "RECORDS": [
    {
      "original": "path/to/visible/image.jpg",
      "processed": "path/to/infrared/image.jpg",
      "time_stamp": "2023-06-15 14:30:00",
      "feature": ["water", "forest"],
      "shooting_position": [116.3974, 39.9093],
      "weather": "sunny",
      "temperature": 25,
      "humidity": 65,
      "wind_dir": "North Wind",
      "wind_scale": 3,
      "wind_speed": 15,
      "precip": 0.0,
      "pressure": 1013,
      "vis": 10000,
      "cloud": 20,
      "AS": 0.85,
      "HS": 0.92
    }
  ]
}
```

### Database Table Structure
The database contains the following fields:
- `id`: Primary key
- `original`: Original image path
- `processed`: Processed image path
- `time_stamp`: Timestamp
- `feature`: Ground feature types (JSON format)
- `shooting_position`: Shooting position (JSON format)
- Meteorological parameter fields: `weather`, `temperature`, `humidity`, `wind_dir`, `wind_scale`, `wind_speed`, `precip`, `pressure`, `vis`, `cloud`
- Other parameters: `AS`, `HS`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Issues and Pull Requests are welcome to improve this project.

## Citation

If you use this dataset or annotation tool in your research, please cite the relevant paper (to be added).

## Contact

For questions or suggestions, please contact:
- Email: 274652724@qq.com
- GitHub Issues: [Project Issues Page](https://github.com/DrChanter/CEVI-DatasetAnnotator/issues)

---

*This project aims to provide high-quality data support for visible-infrared image conversion research.*