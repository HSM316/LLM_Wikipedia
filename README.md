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
We collect articles from the following categories: *Art*, *Biology*, *Computer Science (CS)*, *Chemistry*, *Mathematics*, *Philosophy*, *Physics*, *Sports*. Then we scrape the Wikipedia page versions from 2020 to 2025 (more accurately, the version on January 1 of each year).

<pre>
├── Get_Category.py             // Get the title of a Wikipedia page for a given category  
├── Get_Edition.py              // Get the version of given Wikipedia pages as of January 1 of each year from 2020 to 2025 
├── Clean.py                    // Cleaning Wikipedia pages into plain text  
└──  Clean_First.py             // Extract the first part of a Wikipedia page and clean it into plain text
</pre>

## Page View

<div style="background-color: rgba(245, 245, 245, 0.9); border: 2px solid #008080; border-radius: 5px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
  <p style="font-weight: bold; font-style: italic; margin-top: 0;">Finding 1:</p>
  <p>In the second half of 2024, there was a slight decline in page views across some scientific categories, and its connection to the use of LLMs requires further investigation.</p>
</div>


<pre>
├── Get_Page_Views.py           // Get Page Views  
├── Art_pageviews.csv           // Monthly page view data for the Art category from January 2020 to January 2025.
... ...
└── Sports_pageviews.csv        // Monthly page view data for the Sports category from January 2020 to January 2025.
</pre>

## Word Frequency

<div style="background-color: rgba(245, 245, 245, 0.9); border: 2px solid #008080; border-radius: 5px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
  <p style="font-weight: bold; font-style: italic; margin-top: 0;">Finding 2:</p>
  <p>While the estimation results vary, the influence of LLMs on Wikipedia is likely to become more significant over time. In some categories, the impact has exceeded 2%.</p>
</div>

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

<div style="background-color: rgba(245, 245, 245, 0.9); border: 2px solid #008080; border-radius: 5px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
  <p style="font-weight: bold; font-style: italic; margin-top: 0;">Finding 3:</p>
  <p>The trends in several linguistic metrics of these Wikipedia pages do indeed show a closer step to the characteristics of LLM outputs, although this is merely a correlation and does not necessarily imply causality.</p>
</div>

## Machine Translation

<div style="background-color: rgba(245, 245, 245, 0.9); border: 2px solid #008080; border-radius: 5px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
  <p style="font-weight: bold; font-style: italic; margin-top: 0;">Finding 4:</p>
  <p>The impact of LLMs on the benchmark could not only inflate the translation scores across different languages but also distort the comparison of translation abilities between models, making it fail to truly reflect their translation effectiveness.</p>
</div>

## RAG

<img src="figures/RAG.png">
<p align="center">

<div style="background-color: rgba(245, 245, 245, 0.9); border: 2px solid #008080; border-radius: 5px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
  <p style="font-weight: bold; font-style: italic; margin-top: 0;">Finding 5:</p>
  <p>The results suggest that LLM-generated content performs less effectively in RAG systems compared to human-created texts. If such content has impacted high-quality communities like Wikipedia, it raises concerns about the potential decline in information quality in knowledge bases.</p>
</div>

## Citation

