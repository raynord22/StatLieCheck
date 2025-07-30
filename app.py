import streamlit as st
import scipy.stats as stats
import nltk
from nltk.tokenize import word_tokenize
from io import BytesIO
import sqlite3
import datetime

# Try to import EasyOCR for camera functionality
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    easyocr = None  # Define to avoid unbound variable error

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)  # For parsing text
except Exception as e:
    st.warning("Could not download NLTK data. Text analysis will use basic word splitting.")

st.title("StatLieChecker: Spot Lies in Any Statistic")

# Initialize database for user tracking
@st.cache_resource
def init_database():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, 
                  analyses INTEGER DEFAULT 0, 
                  last_reset DATE, 
                  subscribed BOOLEAN DEFAULT 0,
                  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

# Initialize database connection
db_conn = init_database()

# User authentication section
st.subheader("🔐 Start Your Statistical Analysis")
email = st.text_input(
    "Enter your email to track usage (or use 'demo@example.com' for testing):", 
    placeholder="your.email@example.com",
    help="We use this to track your daily free analysis limit. Premium users get unlimited access."
)

# Check user usage and subscription status
if email:
    c = db_conn.cursor()
    
    # Get or create user record
    c.execute("SELECT analyses, last_reset, subscribed FROM users WHERE email=?", (email,))
    row = c.fetchone()
    today = datetime.date.today().isoformat()
    
    if row:
        analyses, last_reset, subscribed = row
        # Reset daily count if new day
        if last_reset != today:
            analyses = 0
            c.execute("UPDATE users SET analyses=0, last_reset=? WHERE email=?", (today, email))
            db_conn.commit()
    else:
        # Create new user
        analyses = 0
        subscribed = False
        c.execute("INSERT INTO users (email, analyses, last_reset, subscribed) VALUES (?, 0, ?, 0)", 
                 (email, today))
        db_conn.commit()
    
    # Display usage status
    if subscribed:
        st.success("✅ **Premium User** - Unlimited analyses")
        usage_remaining = "Unlimited"
        can_analyze = True
    else:
        free_limit = 5
        usage_remaining = max(0, free_limit - analyses)
        can_analyze = analyses < free_limit
        
        if usage_remaining > 0:
            st.info(f"🆓 **Free Plan** - {usage_remaining} analyses remaining today")
        else:
            st.error("🚫 **Daily limit reached** - Upgrade to Premium for unlimited access")
            
    # Premium upgrade prompt for free users
    if not subscribed:
        with st.expander("🚀 Upgrade to Premium - $4.99/month", expanded=(usage_remaining == 0)):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Premium Benefits:**")
                st.write("• ✅ Unlimited daily analyses")
                st.write("• 📊 Advanced statistical tools")
                st.write("• 📄 Export detailed PDF reports")
                st.write("• 🎯 Priority customer support")
                st.write("• 📚 Exclusive educational content")
            
            with col2:
                st.markdown("**Perfect for:**")
                st.write("• 🎓 Students and researchers")
                st.write("• 📰 Journalists and fact-checkers")
                st.write("• 💼 Business analysts")
                st.write("• 🏫 Educators and trainers")
                
            st.markdown("### 💳 Subscribe Now")
            st.markdown(
                "[**Subscribe for $4.99/month**](https://buy.stripe.com/test_link) | "
                "[**Annual Plan - $49.99/year**](https://buy.stripe.com/test_annual) (Save 17%)"
            )
            st.caption("Secure payment powered by Stripe. Cancel anytime.")
            
            # Demo subscription button (for testing)
            if st.button("🧪 Enable Premium (Demo)", help="For testing purposes - simulates subscription"):
                c.execute("UPDATE users SET subscribed=1 WHERE email=?", (email,))
                db_conn.commit()
                st.success("Demo premium activated! Refresh the page.")
                st.rerun()
else:
    st.warning("⚠️ Please enter your email to start analyzing statistical claims.")
    can_analyze = False
    usage_remaining = 0
    subscribed = False  # Default for when no email is provided

# Camera input for OCR (if available)
extracted_text = ""
if OCR_AVAILABLE:
    st.subheader("📱 Option 1: Use Camera to Capture Text")
    camera_image = st.camera_input("Take a photo of the statistic you want to analyze")
    
    if camera_image and easyocr:
        with st.spinner("Extracting text from image..."):
            try:
                # Extract text with EasyOCR
                reader = easyocr.Reader(['en'], gpu=False)  # English, no GPU needed
                bytes_data = camera_image.getvalue()
                result = reader.readtext(bytes_data)
                extracted_text = ' '.join([text[1] for text in result if text[1]])
                
                if extracted_text:
                    st.success(f"✅ **Extracted Text:** {extracted_text}")
                else:
                    st.warning("⚠️ No text detected—try a clearer photo or enter manually below.")
            except Exception as e:
                st.error(f"Error processing image: {e}")
                extracted_text = ""
else:
    st.info("📝 Camera OCR feature requires additional setup. Using manual text input only.")

# Manual input section
st.subheader("✍️ Option 2: Enter Statistic Manually")
claim = st.text_area(
    "Enter your statistical claim here:", 
    value=extracted_text,
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

# Analysis button - only enabled if user can analyze
analyze_button = st.button(
    "🔍 Analyze Statistical Claim", 
    type="primary", 
    use_container_width=True,
    disabled=not can_analyze,
    help="Analyze your statistical claim for potential fallacies" if can_analyze else "Upgrade to Premium or wait until tomorrow for more free analyses"
)

if analyze_button and can_analyze:
    if not claim.strip():
        st.error("Please enter or capture a statistical claim to analyze.")
    else:
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
        
        # Update user's analysis count (for free users only)
        if email and not subscribed:
            c = db_conn.cursor()
            c.execute("UPDATE users SET analyses = analyses + 1 WHERE email=?", (email,))
            db_conn.commit()
        
        # Premium features promotion
        if not subscribed:
            st.markdown("---")
            st.info(
                "🚀 **Want more features?** Premium users get unlimited analyses, "
                "PDF export, advanced statistical tools, and priority support. "
                "[Upgrade now for $4.99/month](https://buy.stripe.com/test_link)"
            )

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
    if OCR_AVAILABLE:
        st.write("1. Take a photo of statistics OR enter text manually")
    else:
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
    
    # Usage statistics for the current user
    if email:
        c = db_conn.cursor()
        c.execute("SELECT analyses, subscribed, created_date FROM users WHERE email=?", (email,))
        user_data = c.fetchone()
        if user_data:
            analyses_today, is_subscribed, created = user_data
            st.markdown("---")
            st.subheader("📊 Your Usage")
            if is_subscribed:
                st.success("✅ Premium Member")
            else:
                st.write(f"📈 Analyses today: {analyses_today}/5")
                st.write(f"📅 Member since: {created[:10] if created else 'Today'}")
                
            if not is_subscribed and analyses_today >= 3:
                st.info("💡 Consider upgrading to Premium for unlimited access!")

# Database cleanup on app close
import atexit
atexit.register(lambda: db_conn.close())
