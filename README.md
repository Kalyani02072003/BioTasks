BioTasks API Documentation
==========================

Overview
--------

This API provides endpoints for running various protein design and prediction tasks, including **AntiFold**, **LigandMPNN**, and **ProteinMPNN**. 
Users can submit PDB files and request different types of predictions.

Base URL
--------
`   http://your-server-ip/v1/api   `

1\. **AntiFold Prediction**
---------------------------

### **1.1 Predict Protein Structure**

**Endpoint:**POST /antifold/predict

**Description:**Starts AntiFold to predict protein structures.

**Form Data Parameters:**

ParameterTypeRequiredDescriptiontask\_typestringNoType of prediction taskheavy\_chainstringNoHeavy chain specificationlight\_chainstringNoLight chain specificationpdb\_filefileYesPDB file for the prediction

**Example Request (Postman - Form Data):**
`   {    "task_type": "folding",    "heavy_chain": "A",    "light_chain": "B",    "pdb_file": "example.pdb"  }   `

**Example Response:**
`   {    "task_id": "123e4567-e89b-12d3-a456-426614174000",    "message": "AntiFold started"  }   `

### **1.2 Check Prediction Status**

**Endpoint:**GET /antifold/check\_status/

**Description:**Check if AntiFold has finished running.

**Example Request:**
`   GET /antifold/check_status/123e4567-e89b-12d3-a456-426614174000   `

**Example Response:**
`   {    "task_id": "123e4567-e89b-12d3-a456-426614174000",    "logs": [      "AntiFold process started...",      "Processing PDB file...",      "Prediction completed successfully."    ]  }   `

2\. **LigandMPNN Protein Design**
---------------------------------

### **2.1 Design Protein with LigandMPNN**

**Endpoint:**POST /ligandmpnn/design

**Description:**Starts LigandMPNN for protein design.

**Form Data Parameters:**

ParameterTypeRequiredDescriptionpdb\_filefileYesPDB file for designchains\_to\_designstringYesChains to be designedfixed\_residuesstringNoFixed residuesresidues\_to\_designstringNoResidues to redesigntemperaturefloatNoTemperature setting (default 0.1)number\_of\_batchesintNoNumber of batches (default 8)

**Example Request (Postman - Form Data):**
`   {    "pdb_file": "protein_structure.pdb",    "chains_to_design": "A",    "fixed_residues": "",    "residues_to_design": "A1,A2,A3",    "temperature": 0.2,    "number_of_batches": 5  }   `

**Example Response:**
`   {    "message": "LigandMPNN started",    "task_id": "123e4567-e89b-12d3-a456-426614174000",    "log_file": "ligandmpnn_output/123e4567-e89b-12d3-a456-426614174000.log",    "output_folder": "ligandmpnn_output"  }   `

### **2.2 Check LigandMPNN Status**

**Endpoint:**GET /ligandmpnn/check\_status/

**Description:**Check if LigandMPNN has finished running.

**Example Request:**
`   GET /ligandmpnn/check_status/123e4567-e89b-12d3-a456-426614174000   `

**Example Response:**
`   {    "task_id": "123e4567-e89b-12d3-a456-426614174000",    "logs": [      "Designing protein from this path: /uploads/example.pdb",      "Residues redesigned: ['A1', 'A2', 'A3']",      "Design completed successfully."    ]  }   `

3\. **ProteinMPNN ddG Prediction**
----------------------------------

### **3.1 Run ProteinMPNN ddG Prediction**

**Endpoint:**POST /proteinmpnn/ddg

**Description:**Starts ProteinMPNN to predict ddG changes for mutations.

**Form Data Parameters:**

ParameterTypeRequiredDescriptionpdb\_filefileYesPDB file for ddG predictionchainstringNoChain to be analyzed (default "A")

**Example Request (Postman - Form Data):**
`   {    "pdb_file": "protein_structure.pdb",    "chain": "A"  }   `

**Example Response:**
`   {    "message": "ProteinMPNN started",    "task_id": "987e6543-e89b-12d3-a456-426614174000",    "log_file": "proteinmpnn_output/987e6543-e89b-12d3-a456-426614174000.log",    "output_folder": "proteinmpnn_output"  }   `

### **3.2 Check ProteinMPNN Status**

**Endpoint:**GET /proteinmpnn/check\_status/

**Description:**Check if ProteinMPNN has finished running.

**Example Request:**
`   GET /proteinmpnn/check_status/987e6543-e89b-12d3-a456-426614174000   `

**Example Response:**
`   {    "task_id": "987e6543-e89b-12d3-a456-426614174000",    "logs": [      "Processing PDB file...",      "Running ProteinMPNN model...",      "ddG predictions completed."    ]  }   `

4\. **List Available Tasks**
----------------------------

### **4.1 Get Available Tasks**

**Endpoint:**GET /tasks/

**Description:**Returns a list of available tasks in the API.

**Example Request:**
`   GET /tasks/   `

**Example Response:**
`   {    "available_tasks": [      {"task": "AntiFold Prediction", "endpoint": "/v1/api/antifold/predict"},      {"task": "Check AntiFold Status", "endpoint": "/v1/api/antifold/check_status/"},      {"task": "ProteinMPNN ddG Prediction", "endpoint": "/v1/api/proteinmpnn/ddg"},      {"task": "Check ProteinMPNN Status", "endpoint": "/v1/api/proteinmpnn/check_status/"}    ]  }   `

Error Handling
--------------

Error CodeMeaningPossible Causes400Bad RequestMissing required parameters404Not FoundTask ID does not exist500Internal Server ErrorUnexpected backend failure

Notes
-----

*   Make sure to send **PDB files** as **multipart/form-data** in Postman.
    
*   Some parameters have **default values**, so they are optional unless explicitly needed.
    
*   The API is **asynchronous**, so after submitting a task, check its status using the /check\_status/ endpoint.
    

This **Markdown** file is ready to use for **GitHub documentation, Postman, or API ReadMe files**. 🚀 Let me know if you need any refinements!