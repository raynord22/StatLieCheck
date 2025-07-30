# StatLieChecker: Statistical Fallacy Detection Tool

## Overview

StatLieChecker is a Streamlit-based web application designed to analyze statistical claims and identify potential fallacies or misleading statistics. The application leverages natural language processing (NLTK) and statistical analysis (SciPy) to detect common statistical manipulation techniques as outlined in "How to Lie with Statistics." The app now includes optional camera OCR functionality for analyzing statistics from images and comprehensive chapter-by-chapter fallacy detection based on Darrell Huff's classic book.

## Recent Changes (July 30, 2025)

- Enhanced fallacy detection system with chapter-specific references to "How to Lie with Statistics"
- Improved user interface with better formatting and educational content
- Removed camera OCR functionality for cleaner user experience
- Added comprehensive sidebar with Huff's principles and questions
- Enhanced statistical significance testing with better error handling
- Implemented chapter-by-chapter fallacy categorization (Chapters 1-10)
- **MONETIZATION**: Switched to ads-based freemium model with session tracking
- **MONETIZATION**: Implemented session-based usage limits (3 free analyses per session)
- **MONETIZATION**: Added Google AdSense placeholder for ad revenue
- **MONETIZATION**: Created one-time $4.99 payment to remove ads forever
- **MONETIZATION**: Added Stripe payment integration placeholder
- **MONETIZATION**: Removed email tracking for simplified user experience

## User Preferences

Preferred communication style: Simple, everyday language.
Keep premium features honest - only promise what the app actually delivers.
Focus on core value: detecting statistical tricks and manipulation in claims.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for its simplicity in creating data science web apps with minimal code
- **UI Components**: Text areas, number inputs, columns layout, and interactive buttons
- **User Interface**: Single-page application with real-time analysis capabilities

### Backend Architecture
- **Runtime**: Python-based application running on Streamlit server
- **Processing Logic**: Synchronous processing with immediate feedback to users
- **Analysis Engine**: Rule-based fallacy detection system using keyword matching and statistical validation

## Key Components

### 1. Text Analysis Module
- **Purpose**: Processes user-input statistical claims for fallacy detection
- **Technology**: NLTK for tokenization and text processing
- **Fallback Mechanism**: Simple string splitting if NLTK fails

### 2. Statistical Validation Module
- **Purpose**: Performs significance testing when numerical data is provided
- **Technology**: SciPy.stats for statistical computations
- **Inputs**: Sample sizes, means, and standard deviations for comparative analysis

### 3. Fallacy Detection Engine
- **Purpose**: Identifies common statistical manipulation techniques
- **Approach**: Keyword-based pattern matching against known fallacy indicators
- **Output**: Categorized fallacies with explanations and lie-level ratings

### 4. User Interface Components
- **Input Section**: Text area for claims and optional numerical inputs
- **Analysis Section**: Interactive button triggering the analysis process
- **Results Section**: Dynamic display of detected fallacies and risk assessments

## Data Flow

1. **Input Collection**: User enters statistical claim and optional numerical data
2. **Text Processing**: Claim is tokenized using NLTK (with fallback to basic splitting)
3. **Pattern Matching**: Tokens are analyzed against predefined fallacy patterns
4. **Statistical Analysis**: If numerical data provided, statistical significance is calculated
5. **Risk Assessment**: Fallacies are categorized and assigned lie-level ratings
6. **Result Display**: Findings are presented with explanations and educational context

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **NLTK**: Natural language processing for text tokenization
- **SciPy**: Statistical computing library for significance testing

### Data Requirements
- **NLTK Data**: Punkt tokenizer models (downloaded automatically)
- **No External APIs**: Application runs entirely offline

## Deployment Strategy

### Development Environment
- **Platform**: Suitable for Replit deployment with Python runtime
- **Dependencies**: All requirements handled through pip installation
- **Error Handling**: Graceful degradation when NLTK data download fails

### Production Considerations
- **Scalability**: Single-user sessions with no persistent state required
- **Performance**: Lightweight processing suitable for real-time analysis
- **Reliability**: Fallback mechanisms ensure functionality even with partial failures

### Key Design Decisions

1. **Rule-Based Detection**: Chosen over ML models for transparency and educational value
2. **Keyword Matching**: Simple but effective approach for detecting statistical manipulation patterns
3. **Educational Focus**: Explanations reference "How to Lie with Statistics" for user learning
4. **Optional Numerical Input**: Allows both casual text analysis and detailed statistical validation
5. **Streamlit Framework**: Enables rapid prototyping and deployment with minimal infrastructure overhead

The application prioritizes educational value and accessibility, making statistical literacy tools available to users without requiring deep statistical knowledge.