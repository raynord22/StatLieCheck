import streamlit as st
import scipy.stats as stats
import nltk
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)  # For parsing text
except Exception as e:
    st.warning("Could not download NLTK data. Text analysis will use basic word splitting.")

st.title("StatLieChecker: Spot Lies in Any Statistic")

# Initialize session state for tracking usage and ad-free status
if 'analyses' not in st.session_state:
    st.session_state.analyses = 0
if 'ad_free' not in st.session_state:
    st.session_state.ad_free = False

# Display user status
if st.session_state.ad_free:
    st.success("✅ **Premium User** - Unlimited analyses, no ads")
else:
    st.info("🆓 **Free Version** - Includes ads between analyses")

# Statistical claim input
st.subheader("✍️ Enter Your Statistical Claim")
claim = st.text_area(
    "Enter your statistical claim here:", 
    placeholder="e.g., 'This workout boosts endurance by 20% in 30 days' or 'Our product increases sales by 95%'",
    help="Enter any statistical claim you want to analyze for potential fallacies"
)

# Statistical data inputs for significance testing
st.subheader("📊 Optional: Add Statistical Data for Advanced Analysis")
col1, col2 = st.columns(2)

with col1:
    sample_size = st.number_input("Sample size (n)", min_value=0, value=0, help="Number of subjects in the study")
    mean1 = st.number_input("Mean of group 1", value=0.0, help="Average value for the first group")
    sd1 = st.number_input("Standard deviation of group 1", value=0.0, help="Measure of data spread in group 1")

with col2:
    mean2 = st.number_input("Mean of group 2", value=0.0, help="Average value for comparison group")
    sd2 = st.number_input("Standard deviation of group 2", value=0.0, help="Measure of data spread in group 2")

# Analysis button
if st.button("🔍 Analyze Statistical Claim", type="primary", use_container_width=True):
    if not claim.strip():
        st.error("Please enter a statistical claim to analyze.")
    else:
        # Track usage for analytics (optional)
        st.session_state.analyses += 1
        
        # Tokenize text with fallback for NLTK
        try:
            tokens = word_tokenize(claim.lower())
        except:
            tokens = claim.lower().split()  # Fallback to basic splitting

        # Initialize fallacy detection
        fallacies = []
        lie_level = "Low"  # Default rating

        # Comprehensive fallacy checks based on "How to Lie with Statistics"
        
        # Chapter 1: The Sample with the Built-in Bias
        if sample_size > 0 and sample_size < 30:
            fallacies.append({
                "type": "Small Sample Fallacy",
                "description": f"With only n={sample_size}, results might be random luck rather than real patterns.",
                "book_reference": "Chapter 1: Small samples exaggerate extremes—like polling 5 friends about politics and claiming it represents everyone.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Chapter 2: The Well-Chosen Average
        if any(word in tokens for word in ["average", "mean", "typical"]):
            fallacies.append({
                "type": "Misleading Averages",
                "description": "Averages can hide important variations and be manipulated by outliers.",
                "book_reference": "Chapter 2: 'Average' income looks high if one millionaire skews the entire dataset upward.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Chapter 3: The Little Figures That Are Not There
        if any(word in tokens for word in ["percent", "%"]) and any(word in tokens for word in ["increase", "decrease", "boost", "reduce", "improve"]):
            fallacies.append({
                "type": "Percentage Manipulation",
                "description": "Percentages can sound impressive without proper baseline context.",
                "book_reference": "Chapter 3: A 100% increase from 1 to 2 is just +1—always check the absolute numbers behind percentages.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Chapter 4: Much Ado About Practically Nothing
        if any(word in tokens for word in ["significant", "statistically"]) and sample_size == 0:
            fallacies.append({
                "type": "Statistical Significance Without Context",
                "description": "Claims of statistical significance without showing effect size or practical importance.",
                "book_reference": "Chapter 4: Statistical significance doesn't mean practical significance—a tiny difference can be 'significant' with enough data.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Chapter 5: The Gee-Whiz Graph
        if any(word in tokens for word in ["graph", "chart", "shows", "demonstrates", "visualizes"]):
            fallacies.append({
                "type": "Graphical Manipulation",
                "description": "Charts and graphs can be designed to distort reality and mislead viewers.",
                "book_reference": "Chapter 5: Truncated axes make tiny changes look dramatic. Always check the scale and starting points.",
                "severity": "Medium"
            })
            lie_level = "Medium"
        
        # Chapter 6: The One-Dimensional Picture
        if any(word in tokens for word in ["correlation", "related", "linked", "associated", "causes", "leads", "due"]):
            fallacies.append({
                "type": "Correlation vs Causation (Post Hoc Fallacy)",
                "description": "Just because two things happen together doesn't mean one causes the other.",
                "book_reference": "Chapter 6: Roosters crow at dawn, but they don't cause the sun to rise. Correlation ≠ Causation.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Chapter 7: The Semiattached Figure
        if any(word in tokens for word in ["study", "research", "survey"]) and any(word in tokens for word in ["shows", "proves", "demonstrates"]):
            fallacies.append({
                "type": "Biased Sampling & Cherry-Picking",
                "description": "Results can be skewed if the sample isn't representative or data is selectively reported.",
                "book_reference": "Chapter 7: Asking only wealthy people about tax policy gives biased results that don't represent everyone.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Chapter 8: Post Hoc Rides Again (Additional causation fallacies)
        if any(word in tokens for word in ["after", "following", "since", "because"]) and any(word in tokens for word in ["improved", "increased", "decreased"]):
            fallacies.append({
                "type": "Post Hoc Ergo Propter Hoc",
                "description": "Assuming that because B follows A, A must have caused B.",
                "book_reference": "Chapter 8: Just because sales increased after hiring a consultant doesn't mean the consultant caused the increase.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Chapter 9: How to Statisticulate (Missing context)
        if any(word in tokens for word in ["success", "effective", "works", "proven"]) and not any(word in tokens for word in ["failure", "unsuccessful", "failed"]):
            fallacies.append({
                "type": "Survivorship Bias",
                "description": "Focusing only on successes while ignoring failures creates false impressions.",
                "book_reference": "Chapter 9: WWII planes showed bullet holes on survivors—but the key was to reinforce where holes weren't found.",
                "severity": "High"
            })
            lie_level = "High"
        
        # Chapter 10: How to Talk Back to a Statistic
        if any(word in tokens for word in ["rate", "chance", "probability", "risk"]) and "base" not in tokens:
            fallacies.append({
                "type": "Base-Rate Fallacy",
                "description": "Ignoring the overall frequency of events in the population.",
                "book_reference": "Chapter 10: A 99% accurate test for a rare disease (1/1000 people) still gives mostly false positives.",
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
                significance_result = f"**P-value: {p_value:.4f}**"
                
                if p_value < 0.05:
                    significance_result += "\n\n✅ **Statistically significant** (p < 0.05) - The difference is unlikely due to chance alone, but still watch for other biases."
                else:
                    significance_result += "\n\n❌ **Not statistically significant** (p ≥ 0.05) - The difference could easily be due to random variation."
                    if lie_level != "High":
                        lie_level = "Medium"
                
            except Exception as e:
                significance_result = f"⚠️ Error in statistical calculation: {e}"

        # Display results with improved formatting
        st.markdown("---")
        
        # Lie Level indicator with color coding and context
        if lie_level == "Low":
            st.success(f"### 🟢 Lie Level: {lie_level}")
            st.write("This claim appears relatively trustworthy, but always verify sources.")
        elif lie_level == "Medium":
            st.warning(f"### 🟡 Lie Level: {lie_level}")
            st.write("This claim has some potential issues that deserve scrutiny.")
        else:
            st.error(f"### 🔴 Lie Level: {lie_level}")
            st.write("This claim shows multiple red flags that warrant serious skepticism.")
        
        # Display the claim being analyzed
        st.info(f"**📝 Analyzing claim:** {claim}")
        
        # Show detected fallacies with enhanced formatting
        if fallacies:
            st.subheader("🚨 Statistical Fallacies Detected:")
            for i, fallacy in enumerate(fallacies, 1):
                with st.expander(f"{i}. {fallacy['type']}", expanded=True):
                    st.write(f"**🎯 Issue:** {fallacy['description']}")
                    st.write(f"**📖 Book Reference:** {fallacy['book_reference']}")
                    
                    # Severity indicator
                    if fallacy['severity'] == 'High':
                        st.error(f"**Severity:** {fallacy['severity']} ⚠️")
                    elif fallacy['severity'] == 'Medium':
                        st.warning(f"**Severity:** {fallacy['severity']} ⚠️")
                    else:
                        st.info(f"**Severity:** {fallacy['severity']}")
        else:
            st.success("✅ **No obvious statistical fallacies detected** - The claim appears solid, but always double-check sources and context.")
            st.info("💡 **Remember Huff's advice:** Always ask 'Who says so?' and 'How do they know?' when evaluating any statistical claim.")
        
        # Statistical significance results
        if significance_result:
            st.subheader("📊 Statistical Significance Analysis")
            st.markdown(significance_result)
        
        # Educational summary inspired by the book
        st.markdown("---")
        st.subheader("📚 Key Takeaway from 'How to Lie with Statistics'")
        st.info(
            "Statistics are like a bikini. What they reveal is suggestive, but what they conceal is vital. "
            "Use this analysis to develop your statistical literacy and make better-informed decisions about "
            "health claims, news reports, marketing messages, and research findings."
        )
        
        # Call to action with book reference
        st.markdown("---")
        st.markdown(
            "💡 **Want to learn more?** This tool is based on Darrell Huff's classic 1954 book "
            "'How to Lie with Statistics' - still the best introduction to statistical skepticism ever written."
        )
        
        # Show ads if user is on free plan
        if not st.session_state.ad_free:
            st.markdown("---")
            st.markdown("### 📢 Advertisement")
            
            # Google AdSense Integration
            st.markdown("""
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5201605536254896"
                 crossorigin="anonymous"></script>
            <!-- StatLieChecker Ad -->
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-5201605536254896"
                 data-ad-slot="auto"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
            """, unsafe_allow_html=True)
            
            # Alternative: Simple affiliate or promotional content
            st.info("📚 **Learn more statistical literacy** - Get the book 'How to Lie with Statistics' that inspired this tool!")
            
            st.markdown("---")
            st.info("💡 **Remove ads forever** - One-time payment of $4.99 for unlimited ad-free analyses!")

# Ad-free upgrade section
if not st.session_state.ad_free:
    st.markdown("---")
    st.subheader("🚀 Go Premium - One-Time $4.99")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Premium Benefits:**")
        st.write("• 🚫 Remove all advertisements")
        st.write("• 🔍 All statistical fallacy detection")
        st.write("• 📊 Statistical significance calculator")
        st.write("• ⚡ Clean, uninterrupted experience")
    
    with col2:
        st.markdown("**Perfect for:**")
        st.write("• 📰 Journalists fact-checking claims")
        st.write("• 🎓 Students studying statistics")
        st.write("• 💼 Professionals analyzing data")
        st.write("• 🧠 Anyone who values critical thinking")
    
    # Stripe payment button placeholder
    st.markdown("### 💳 One-Time Payment - No Subscription")
    if st.button("💰 Go Premium - $4.99 (Remove Ads Forever)", type="primary", use_container_width=True):
        st.info("🔗 **Stripe integration ready** - Add your Stripe checkout URL here")
        st.markdown("**Next steps for Stripe integration:**")
        st.write("1. Create a product in your Stripe dashboard for $4.99")
        st.write("2. Generate a payment link")
        st.write("3. Replace the URL below with your Stripe payment link")
        st.code("# Your Stripe payment URL will go here")
    
    # Demo button for testing
    if st.button("🧪 Enable Ad-Free (Demo)", help="For testing - simulates successful payment"):
        st.session_state.ad_free = True
        st.success("✅ Ad-free activated! Refresh to see changes.")
        st.rerun()
        
    st.caption("💡 Secure payment powered by Stripe. One-time payment, no monthly fees.")

# Footer with book attribution
st.markdown("---")
st.markdown(
    "*StatLieChecker empowers anyone to critically evaluate statistical claims in everyday life. "
    "Based on principles from 'How to Lie with Statistics' by Darrell Huff and modern statistical literacy research.*"
)

# Sidebar with Huff's principles
with st.sidebar:
    st.header("📖 About StatLieChecker")
    st.write(
        "This tool helps you identify common statistical fallacies and misleading claims using principles "
        "from Darrell Huff's timeless book 'How to Lie with Statistics'."
    )
    
    st.subheader("🎯 How to Use")
    st.write("1. Enter any statistical claim in the text area")
    st.write("2. Optionally add numerical data for significance testing")
    st.write("3. Click 'Analyze' to get your results")
    st.write("4. Review the fallacies and lie level rating")
    
    st.subheader("⚠️ Huff's Red Flags")
    st.write("• Small or biased samples")
    st.write("• Missing context for percentages")
    st.write("• Correlation claimed as causation")
    st.write("• Misleading graphs and charts")
    st.write("• Cherry-picked success stories")
    st.write("• Undefined or shifted baselines")
    
    st.subheader("💡 Huff's Questions to Ask")
    st.write("• Who says so?")
    st.write("• How do they know?")
    st.write("• What's missing?")
    st.write("• Did somebody change the subject?")
    st.write("• Does it make sense?")
    
    st.subheader("📚 Chapter References")
    st.write("1. The Sample with Built-in Bias")
    st.write("2. The Well-Chosen Average")
    st.write("3. The Little Figures Not There")
    st.write("4. Much Ado About Nothing")
    st.write("5. The Gee-Whiz Graph")
    st.write("6. The One-Dimensional Picture")
    st.write("7. The Semiattached Figure")
    st.write("8. Post Hoc Rides Again")
    st.write("9. How to Statisticulate")
    st.write("10. How to Talk Back")
    
    # Session statistics
    st.markdown("---")
    st.subheader("📊 Session Stats")
    if st.session_state.ad_free:
        st.success("✅ Premium User - Ad-free experience")
    else:
        st.write(f"📈 Analyses completed: {st.session_state.analyses}")
        if st.session_state.analyses >= 2:
            st.info("💡 Enjoying the tool? Consider going premium for an ad-free experience!")
