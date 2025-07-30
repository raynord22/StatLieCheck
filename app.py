import streamlit as st
import scipy.stats as stats
import nltk
from nltk.tokenize import word_tokenize
import os

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)  # For parsing text
except Exception as e:
    st.error(f"Error downloading NLTK data: {e}")

st.title("StatLieChecker: Spot Lies in Any Statistic")

# User input section
claim = st.text_area(
    "Enter any statistic claim", 
    placeholder="e.g., 'This workout boosts endurance by 20% in 30 days' or 'Vaccines reduce risk by 95%'",
    help="Enter any statistical claim you want to analyze for potential fallacies"
)

# Statistical inputs for significance testing
st.subheader("Optional: Statistical Data for Significance Testing")
col1, col2 = st.columns(2)

with col1:
    sample_size = st.number_input("Sample size (n)", min_value=0, value=0, help="Total number of observations in the study")
    mean1 = st.number_input("Mean of group 1", value=0.0, help="Average value for the first group")
    sd1 = st.number_input("Standard deviation of group 1", value=0.0, help="Spread of data in the first group")

with col2:
    mean2 = st.number_input("Mean of group 2", value=0.0, help="Average value for the second group (for comparison)")
    sd2 = st.number_input("Standard deviation of group 2", value=0.0, help="Spread of data in the second group")

# Analysis button
if st.button("Analyze Statistical Claim", type="primary"):
    if not claim.strip():
        st.error("Please enter a statistical claim to analyze.")
    else:
        # Tokenize the claim for analysis
        try:
            tokens = word_tokenize(claim.lower())
        except Exception as e:
            st.error(f"Error processing text: {e}")
            tokens = claim.lower().split()  # Fallback to simple split

        # Initialize fallacy detection
        fallacies = []
        lie_level = "Low"  # Default rating

        # Comprehensive fallacy checks based on "How to Lie with Statistics"
        
        # Sample size analysis
        if sample_size > 0 and sample_size < 30:
            fallacies.append({
                "type": "Small Sample Fallacy",
                "description": f"With n={sample_size}, results might be random luck, not real trends.",
                "explanation": "Small groups exaggerate extremes—like polling 5 friends about politics and claiming it represents everyone.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Misleading averages
        if any(word in tokens for word in ["average", "mean"]):
            fallacies.append({
                "type": "Misleading Averages",
                "description": "Averages can hide important variations and outliers in the data.",
                "explanation": "'Average' income looks high if one millionaire skews the entire dataset upward.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Percentage manipulation
        if "percent" in tokens and any(word in tokens for word in ["increase", "decrease", "boost", "reduce"]):
            fallacies.append({
                "type": "Percentage Tricks",
                "description": "Percentages can sound impressive without proper context.",
                "explanation": "A 100% increase from 1 to 2 is just +1—always check the absolute numbers behind percentages.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Correlation vs causation
        if any(word in tokens for word in ["correlation", "related", "linked", "associated", "causes", "leads"]):
            fallacies.append({
                "type": "Correlation vs Causation (Post Hoc Fallacy)",
                "description": "Just because two things happen together doesn't mean one causes the other.",
                "explanation": "Roosters crow at dawn, but they don't cause the sun to rise. Correlation ≠ Causation.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Graphical manipulation
        if any(word in tokens for word in ["graph", "chart", "shows", "demonstrates"]):
            fallacies.append({
                "type": "Graphical Manipulation",
                "description": "Charts and graphs can be designed to distort reality.",
                "explanation": "Truncated axes make tiny changes look dramatic. Always check the scale and starting points.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Sampling bias
        if any(word in tokens for word in ["sample", "survey", "study", "research"]):
            fallacies.append({
                "type": "Biased Sampling",
                "description": "Results can be skewed if the sample isn't representative of the population.",
                "explanation": "Asking only wealthy people about tax policy will give biased results that don't represent everyone.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Survivorship bias
        if any(word in tokens for word in ["success", "survive", "winner", "effective"]):
            fallacies.append({
                "type": "Survivorship Bias",
                "description": "Focusing only on successes while ignoring failures creates false impressions.",
                "explanation": "WWII planes showed bullet holes on survivors—but the key was to reinforce where holes weren't found.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Base rate fallacy
        if any(word in tokens for word in ["rate", "chance", "probability"]) and "base" not in tokens:
            fallacies.append({
                "type": "Base-Rate Fallacy",
                "description": "Ignoring the overall frequency of events in the population.",
                "explanation": "A 99% accurate test for a rare disease (1/1000 people) still gives mostly false positives.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Statistical significance testing
        significance_result = ""
        if mean1 != 0 and mean2 != 0 and sd1 > 0 and sd2 > 0 and sample_size > 1:
            try:
                t_stat, p_value = stats.ttest_ind_from_stats(
                    mean1, sd1, sample_size, mean2, sd2, sample_size
                )
                significance_result = f"**P-value: {p_value:.4f}**\n\n"
                
                if p_value < 0.05:
                    significance_result += "✅ **Statistically significant** (p < 0.05) - The difference is unlikely due to chance alone, but still watch for other biases."
                else:
                    significance_result += "❌ **Not statistically significant** (p ≥ 0.05) - The difference could easily be due to random variation."
                    lie_level = "High"
                
            except Exception as e:
                significance_result = f"Error in statistical calculation: {e}"
        
        # Display results
        st.markdown("---")
        
        # Lie Level indicator with color coding
        if lie_level == "Low":
            st.success(f"### 🟢 Lie Level: {lie_level}")
        elif lie_level == "Medium":
            st.warning(f"### 🟡 Lie Level: {lie_level}")
        else:
            st.error(f"### 🔴 Lie Level: {lie_level}")
        
        # Display the claim being analyzed
        st.info(f"**Analyzing claim:** {claim}")
        
        # Show detected fallacies
        if fallacies:
            st.subheader("🚨 Potential Statistical Fallacies Detected:")
            for i, fallacy in enumerate(fallacies, 1):
                with st.expander(f"{i}. {fallacy['type']}", expanded=True):
                    st.write(f"**Issue:** {fallacy['description']}")
                    st.write(f"**Example:** {fallacy['explanation']}")
                    
                    # Severity indicator
                    if fallacy['severity'] == 'High':
                        st.error(f"Severity: {fallacy['severity']} ⚠️")
                    elif fallacy['severity'] == 'Medium':
                        st.warning(f"Severity: {fallacy['severity']} ⚠️")
                    else:
                        st.info(f"Severity: {fallacy['severity']}")
        else:
            st.success("✅ **No obvious statistical fallacies detected** - The claim appears solid, but always double-check sources and context.")
            st.info("💡 **Remember:** Always ask 'Who says so?' and 'How do they know?' when evaluating any statistical claim.")
        
        # Statistical significance results
        if significance_result:
            st.subheader("📊 Statistical Significance Analysis")
            st.markdown(significance_result)
        
        # Educational summary
        st.markdown("---")
        st.subheader("📚 Key Takeaway")
        st.info(
            "Statistics can be powerful tools for understanding the world, but they can also be used to mislead. "
            "Use this analysis to develop your statistical literacy and make better-informed decisions about "
            "health claims, news reports, marketing messages, and research findings."
        )
        
        # Call to action
        st.markdown("---")
        st.markdown(
            "💡 **Want to learn more?** This tool is based on the classic book "
            "'How to Lie with Statistics' by Darrell Huff - a must-read for anyone who wants to "
            "understand how statistics can be manipulated."
        )
        
        # Optional premium link (as in original)
        st.markdown(
            "📄 [Get Premium Detailed Report ($5 on Gumroad)](https://gumroad.com/yourproductlink) "
            "- Includes comprehensive examples and additional analysis techniques."
        )

# Footer information
st.markdown("---")
st.markdown(
    "*StatLieChecker empowers anyone to critically evaluate statistical claims in everyday life. "
    "Based on principles from 'How to Lie with Statistics' and modern statistical literacy research.*"
)

# Sidebar with additional information
with st.sidebar:
    st.header("📖 About StatLieChecker")
    st.write(
        "This tool helps you identify common statistical fallacies and misleading claims. "
        "It's designed for everyone - no advanced statistics knowledge required!"
    )
    
    st.subheader("🎯 How to Use")
    st.write("1. Enter any statistical claim in the text area")
    st.write("2. Optionally add numerical data for significance testing")
    st.write("3. Click 'Analyze' to get your results")
    st.write("4. Review the fallacies and lie level rating")
    
    st.subheader("⚠️ Common Red Flags")
    st.write("• Small sample sizes (< 30)")
    st.write("• Missing context for percentages")
    st.write("• Correlation claimed as causation")
    st.write("• Biased or unrepresentative samples")
    st.write("• Cherry-picked success stories")
    
    st.subheader("💡 Pro Tips")
    st.write("• Always ask for the sample size")
    st.write("• Look for confidence intervals")
    st.write("• Check who funded the research")
    st.write("• Verify if results were peer-reviewed")
    st.write("• Be skeptical of perfect results")
