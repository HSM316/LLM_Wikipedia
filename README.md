<div align="center">
<h1>Wikipedia in the Era of LLMs: Evolutions and Risks</h1>

<img src="https://img.shields.io/github/last-commit/HSM316/LLM_Wikipedia?style=flat-square&color=5D6D7E" alt="git-last-commit" />
<img src="https://img.shields.io/github/commit-activity/m/HSM316/LLM_Wikipedia?style=flat-square&color=5D6D7E" alt="GitHub commit activity" />
<img src="https://img.shields.io/github/languages/top/HSM316/LLM_Wikipedia?style=flat-square&color=5D6D7E" alt="GitHub top language" />

<img src="figures/Pipeline.png">
<p align="center">

</p>
</div>

## Contents
- [Contents](#contents)
- [Data Collection](#data-collection)
- [Page View](#page-view)
- [Word Frequency](#words-frequency)
- [Linguistic Style](#linguistic-style)
- [Machine Translation](#machine-translation)
- [RAG](#rag)
- [Citation](#citation)

## Data Collection

<pre>
├── Get_Category.py             // Get the title of a Wikipedia page for a given category  
├── Get_Edition.py              // Get the version of given Wikipedia pages as of January 1 of each year from 2020 to 2025 
├── Clean.py                    // Cleaning Wikipedia pages into plain text  
└──  Clean_First.py             // Extract the first part of a Wikipedia page and clean it into plain text
</pre>

## Page View

<pre>
├── Get_Page_Views.py           // Get Page Views  
├── Art_pageviews.csv           // Monthly page view data for the Art category from January 2020 to January 2025.
... ...
└── Sports_pageviews.csv        // Monthly page view data for the Sports category from January 2020 to January 2025.
</pre>

## Word Frequency
<pre>
├── Estimation_Diff.py          // Estimate LLM impact using different combinations of words based on different categories  
├── Estimation_Result           // LLM impact estimation results  
│   ├── Featured_First_eta      // Impact estimated using the first part of the Featured Articles for LLM Simulation  
│   │   ├── different           // Using different word combinations for different categories  
│   │   │   ├── First           // Estimation result of the first part  
│   │   │   └── Full            // Estimation result of the full text  
│   │   └── same                // Using the smae word combinations  
│   │       ├── First  
│   │       ├── Full  
│   │       └── words.jsonl  
│   └── simple_First_eta        // Impact estimated using the first part of the Simple Articles for LLM Simulation  
├── Estimation_Same.py          // Estimating LLM impact using the same combination of words  
├── Frequency.py                // Calculate word frequency  
├── Revise.py                   // LLM Simulation: Use GPT to revise pages  
├── Select_Diff.py              // Select word combinations based on thresholds  
├── Select_Same.py              // Select word combinations based on thresholds (different categories produce different word combinations)  
├── Word_Frequency              // Word Frequency Data  
│   ├── Simulation              // Frequecy after LLM Simulation and the change rate  
│   ├── Total_Words             // Total words for each category  
│   ├── f_First                 // frequency data of the first part  
│   └── f_Full                  // frequency data of the full text  
└── unigram_freq.csv            // Google Ngram dataset 
</pre>

## Linguistic Style


## Machine Translation

## RAG

<img src="figures/RAG.png">
<p align="center">

## Citation

