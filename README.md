.
├── LLM_Impact
│   ├── Clean.py                    // Cleaning Wikipedia pages into plain text
│   ├── Clean_First.py              // Extract the first part of a Wikipedia page and clean it into plain text
│   ├── Estimation_Diff.py          // Estimate LLM impact using different combinations of words based on different categories
│   ├── Estimation_Result           // LLM impact estimation results
│   │   ├── Featured_First_eta      // Impact estimated using the first part of the Featured Articles for LLM Simulation
│   │   │   ├── different           // Using different word combinations for different categories
│   │   │   │   ├── First           // Estimation result of the first part
│   │   │   │   └── Full            // Estimation result of the full text
│   │   │   └── same                // Using the smae word combinations
│   │   │       ├── First
│   │   │       ├── Full
│   │   │       └── words.jsonl
│   │   └── simple_First_eta        // Impact estimated using the first part of the Simple Articles for LLM Simulation
│   ├── Estimation_Same.py          // Estimating LLM impact using the same combination of words
│   ├── Frequency.py                // Calculate word frequency
│   ├── Get_Category.py             // Get the title of a Wikipedia page for a given category
│   ├── Get_Edition.py              // Get the version of given Wikipedia pages as of January 1 of each year from 2020 to 2025
│   ├── Get_Page_Views.py           // Get Page Views
│   ├── Page_Views                  // Page Views Data 
│   ├── Revise.py                   // LLM Simulation: Use GPT to revise pages
│   ├── Select_Diff.py              // Select word combinations based on thresholds
│   ├── Select_Same.py              // Select word combinations based on thresholds (different categories produce different word combinations)
│   ├── Word_Frequency              // Word Frequency Data
│   │   ├── Simulation              // Frequecy after LLM Simulation and the change rate
│   │   ├── Total_Words             // Total words for each category
│   │   ├── f_First                 // frequency data of the first part
│   │   └── f_Full                  //frequency data of the full text
│   └── unigram_freq.csv            // Google Ngram dataset
├── Linguistic_Style
│   ├── Calculate_Readability.py    // Calculate Readability Metrics of different categories
│   ├── Calculate_Style.py          // Calculate Style Metrics of different categories
│   └── Metrics                     // Metrics Data of different categories
│       ├── First
│       └── Full
├── Machine_Translation
│   ├── Facebook-NLLB
│   ├── Google-t5
│   ├── Helsinki-NLP
│   └── datasets
├── RAG
│   ├── News                        // Wikinews from 2020 to 2024
│   │   ├── GPT_Revised
│   │   ├── Gemini_Revised
│   │   └── Plain_Text
│   ├── Question                    // LLM-Generated Multiple-choice Questions (MCQs)
│   ├── gpt3.5                      // Results of questioning using gpt-3.5
│   └── gpt4omini                   // Results of questioning using gpt-4o-mini
└── README.md
