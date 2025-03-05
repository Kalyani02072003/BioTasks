# AntiFold API Documentation

## Overview
This API provides an interface to run AntiFold, a sequence prediction tool for antibody variable domains. Users can submit PDB files and specify required parameters to generate inverse-folded sequences.

## Installation

### Prerequisites
Ensure you have Python and Flask installed:
```bash
pip install flask
```

### Running the API
Clone the repository and start the Flask server:
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000/`

## API Endpoints

### 1. Run AntiFold Prediction
**Endpoint:**
```
POST /antifold
```

**Description:**
Submits a PDB file for inverse folding using AntiFold.

**Request Parameters:**
| Parameter         | Type    | Required | Description |
|------------------|---------|----------|-------------|
| task_type        | string  | Yes      | Either "antibody" or "monobody" |
| pdb_file        | file    | Yes      | PDB file to process |
| heavy_chain      | string  | Required for antibody | Heavy chain ID |
| light_chain      | string  | Required for antibody | Light chain ID |
| nanobody_chain   | string  | Required for monobody | Nanobody chain ID |
| antigen_chain    | string  | No       | Antigen chain ID |
| num_seq_per_target | integer | No  | Number of sequences to generate (default: 10) |
| sampling_temp    | float   | No       | Sampling temperature (default: 0.2) |
| regions          | list    | No       | Regions to mutate (default: CDR1, CDR2, CDR3) |

**Example Request (cURL):**
```bash
curl -X POST http://127.0.0.1:5000/antifold \
  -F "task_type=antibody" \
  -F "pdb_file=@/path/to/file.pdb" \
  -F "heavy_chain=H" \
  -F "light_chain=L" \
  -F "num_seq_per_target=5" \
  -F "sampling_temp=0.5"
```

**Response:**
```json
{
  "message": "AntiFold run successfully.",
  "output_files": ["output1.csv", "output2.fasta"]
}
```

### 2. Download Output File
**Endpoint:**
```
GET /download/<filename>
```

**Description:**
Downloads a single output file.

**Example Request:**
```bash
curl -O http://127.0.0.1:5000/download/output.csv
```

### 3. Download All Output as ZIP
**Endpoint:**
```
GET /download_zip
```

**Description:**
Downloads all output files as a compressed ZIP archive.

**Example Request:**
```bash
curl -O http://127.0.0.1:5000/download_zip
```

## Running in Production
To deploy in production, use a WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```


