## aPhyloGeo-Covid: Reproducible Phylogeographic Analysis Platform of SARS-CoV-2 Variation using Neo4j and Snakemake


# 📝 About the project

 This platform enables users to collect and visualize phylogeographic data related to SARS-CoV-2. Additionally, aPhyloGeo-Covid offers a scalable and reproducible workflow for investigating the relationship between geographic features and the patterns of variation in different SARS-CoV-2 variants. The integrated Neo4j database consolidates a diverse range of COVID-19 pandemic-related sequences, climate data, and metadata from public databases, allowing users to filter and organize input data for phylogeographical studies efficiently.
 
### Data
Various data sources related to SARS-CoV-2 were integrated into a Neo4j database, covering the period from January 1, 2020, to December 31, 2022. 

- Data on COVID-19 (coronavirus) by  _[Our World in Data](https://github.com/owid/covid-19-data/tree/master/public/data)_
- Pango Lineages:Latest epidemiological lineages of SARS-CoV-2 by _[Cov-Lineages](https://cov-lineages.org/lineage_list.html)_
- Daily climate data for regions of sequencing from the _[NASA/POWER](https://power.larc.nasa.gov/data-access-viewer/)_ website
- SARS-CoV-2 sequence data information from _[SARS-CoV-2 Data Hub](https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/virus?SeqType_s=Nucleotide&VirusLineage_ss=taxid:2697049)_


### Neo4j

Labels Within the Neo4j database include Lineage, Protein, Nucleotide, Location, and LocationDay. 

- The Protein and Nucleotide labels store sequencing data information such as Accession, length, collection date, and collected country. 
- The Lineage label stores lineage development information, including the most common country, latest date, and earliest date associated with each lineage. 
- The LocationDay label stores climate information such as temperature, precipitation, wind speed, humidity and sky shortwave irradiance for each location and specific day. 
- The Location label contains basic information about hospitals, health, and the economy of each country, including GDP, median age, life expectancy, population, the proportion of people aged 65 and older, proportion of smokers, proportion of extreme poverty, diabetes prevalence, human development index, and more. 
- Once input sequencing has been defined, an Input node is generated and labelled accordingly in Neo4j graph database.
- The values of the parameters are saved in the node Analysis as properties. 
- The output are saved in the node Output as properties. 
- Once the analysis is completed, the user is assigned a unique output ID, which they can use to query and visualize the results in the web platform.

<img src="./Neo4j/schema_neo.png" alt="isolated" width="700"/>

### Snakemake workflow: aPhyloGeo-pipeline

With alignment results and related environmental data as input, the Snakemake workflow will be triggered in the backend. 

aPhyloGeo-pipeline is a user-friendly, scalable, reproducible, and comprehensive workflow that can explore how patterns of variation within species coincide with geographic features, such as climatic features.

For more information about aPhyloGeo-pipeline:

[GitHub of aPhyloGeo-pipeline](https://github.com/tahiri-lab/aPhyloGeo-pipeline/blob/main/README.md)

[Wiki of aPhyloGeo-pipeline](https://github.com/tahiri-lab/aPhyloGeo-pipeline/wiki)


# 🚀  Getting started 

**1. Clone this repo.**

    git clone https://github.com/tahiri-lab/iPhyloGeo.js.git
    cd DashNeo


**2. Install dependencies.** <br><br>
***2.1 If you do not have Conda installed, then use the following method to install it. If you already have Conda installed, then refer directly to the next step (2.2).***

    # download Miniconda3 installer
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    
    # install Conda (respond by 'yes')
    bash miniconda.sh
    
    # update Conda
    conda update -y conda
    
  
 ***2.2 Create a conda environment named aPhyloGeo and install all the dependencies in that environment.***<br>
 
 
    # create a new environment with dependencies 
    conda env create -n aPhyloGeo-Covid -f environment.yaml
    
    
 ***2.3 Activate the environment***   <br>
 
    conda activate aPhyloGeo-Covid
    

**3. Run workflow**
   
    python index.py
 









