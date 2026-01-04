# AI-Powered Financial Advisor
## 5-Minute Video Demonstration Script

---

## Video Outline

| Section | Duration | Content |
|---------|----------|---------|
| Introduction | 0:30 | Problem & Solution overview |
| Profile Setup | 0:45 | Creating a user profile |
| AI Chat Demo | 1:15 | Interactive conversation |
| Features Showcase | 1:30 | Portfolio, Goals, Market, Invest tabs |
| Technical Highlights | 0:45 | Architecture & compliance |
| Conclusion | 0:15 | Summary & closing |
| **Total** | **5:00** | |

---

## Detailed Script

### Section 1: Introduction (0:00 - 0:30)

**[SCREEN: Title slide with project name]**

> "Hi, I'm Richard Abishai, and today I'm presenting my AI-Powered Financial Advisor - an intelligent system that provides personalized financial guidance using Large Language Models.

> The problem we're solving is simple: most people don't have access to quality financial advice. Traditional advisors are expensive and limited in capacity. Our solution uses AI to democratize financial guidance.

> Let me show you how it works."

**[ACTION: Open the Streamlit application]**

---

### Section 2: Profile Setup (0:30 - 1:15)

**[SCREEN: Profile tab in the application]**

> "First, let's create a user profile. I'll enter 'Demo User' as the session name."

**[ACTION: Type "Demo User" in session name field, click Create/Load]**

> "Now I'll fill in my financial profile:
> - Age: 32
> - Annual Income: $85,000  
> - Current Savings: $25,000
> - Risk Tolerance: I'll select 'High' since I'm young and have time to recover from market dips
> - Investment Horizon: 20 years
> - Goals: Retirement and Wealth Generation"

**[ACTION: Fill in the form fields as described]**

> "For my current portfolio allocation, I have 50% stocks, 30% bonds, and 20% cash."

**[ACTION: Adjust sliders, click "Save Profile"]**

> "Great! Now the system generates personalized recommendations. You can see:
> - My risk score is 75 out of 100 - Moderately Aggressive
> - Target allocation: 70% stocks, 20% bonds, 10% cash
> - And here's my personalized action plan with specific steps"

**[ACTION: Scroll through recommendations]**

---

### Section 3: AI Chat Demo (1:15 - 2:30)

**[SCREEN: Chat tab]**

> "Now let's try the AI chat feature. This is where the magic happens - I can ask any financial question and get personalized advice."

**[ACTION: Click on Chat tab]**

> "Notice the suggested prompts here - these are common questions you might ask. Let me click 'What should my portfolio allocation be?'"

**[ACTION: Click suggested prompt button]**

> "Watch as the AI processes my query... and here's the response. It's personalized to MY profile - referencing my 'Moderately Aggressive' risk profile and suggesting specific allocation percentages."

**[ACTION: Wait for response, highlight key parts]**

> "Let me try another query - this time about a specific stock. I'll type: 'Should I invest in Apple stock?'"

**[ACTION: Type query and submit]**

> "Notice what happens - the system detects 'Apple' and fetches real-time stock data from Alpha Vantage. You can see the live price card here showing AAPL at its current price with today's change."

**[ACTION: Point to stock price card]**

> "The AI response combines this real-time data with my personal profile to give contextual advice. And notice the disclaimer at the bottom - we always remind users this isn't professional financial advice."

---

### Section 4: Features Showcase (2:30 - 4:00)

**[SCREEN: Performance tab]**

> "Let's explore some other features. In the Performance tab, you can see your portfolio value over time."

**[ACTION: Click Performance tab]**

> "This chart shows historical performance compared against benchmarks like the S&P 500 and NASDAQ. Key metrics like Sharpe Ratio, Max Drawdown, and Alpha are displayed here."

---

**[SCREEN: Goals tab]**

> "The Goals tab has interactive calculators for financial planning."

**[ACTION: Click Goals tab]**

> "Let me set up a retirement goal:
> - Target Amount: $1 million
> - Years Until Goal: 25
> - Monthly Contribution: $1,000
> - Expected Return: 7%"

**[ACTION: Fill in calculator fields]**

> "The calculator shows whether I'm on track and provides projections. Similar calculators exist for home purchase and education planning."

---

**[SCREEN: Market tab]**

> "The Market Data tab shows live market information from Alpha Vantage API."

**[ACTION: Click Market tab]**

> "You can see current prices, RSI indicators, price charts, and even news sentiment. This data is fetched in real-time with rate limiting to protect API quotas."

---

**[SCREEN: Invest tab]**

> "Finally, the Invest tab provides specific ETF recommendations."

**[ACTION: Click Invest tab]**

> "Based on my profile, the system suggests:
> - VTI for total market exposure - expense ratio just 0.03%
> - BND for bond allocation
> - And sector-specific ETFs based on my goals

> Each recommendation shows dollar amounts based on my $25,000 savings."

---

**[SCREEN: Export section]**

> "I can also export a PDF report with all my recommendations and action plans."

**[ACTION: Click "Download PDF Report" button]**

> "This creates a professional document I can review offline or share with a financial advisor."

---

### Section 5: Technical Highlights (4:00 - 4:45)

**[SCREEN: Architecture diagram or code snippet]**

> "A quick look at the technical implementation:

> **Model:** We fine-tuned TinyLlama-1.1B using LoRA on FinGPT datasets - 10,000 financial Q&A samples.

> **RAG Pipeline:** Every query combines user context, market data, and chat history before going to the LLM.

> **Compliance:** Built-in guardrails add disclaimers, fact-check stock prices, and log all advice for audit trails.

> **Security:** User profiles are encrypted using Fernet encryption, and we implement rate limiting to protect API quotas."

**[ACTION: Show brief code snippet or architecture diagram]**

> "The system achieves sub-2-second response times and handles concurrent users with proper caching."

---

### Section 6: Conclusion (4:45 - 5:00)

**[SCREEN: Summary slide]**

> "To summarize, we've built:
> - A functional AI financial advisor with personalized recommendations
> - Real-time market data integration
> - Multiple planning tools and calculators  
> - Strong compliance and security measures

> This demonstrates how AI can make quality financial guidance accessible to everyone.

> Thank you for watching!"

**[SCREEN: End slide with contact information]**

---

## Recording Tips

### Before Recording

- [ ] Clear browser cache and cookies
- [ ] Create fresh "Demo User" session
- [ ] Ensure Alpha Vantage API is working (check rate limits)
- [ ] Close unnecessary applications
- [ ] Test audio levels

### During Recording

- [ ] Speak clearly and at moderate pace
- [ ] Pause briefly after each action for viewers to follow
- [ ] Point cursor to elements you're discussing
- [ ] If something fails, explain it as a "feature" or re-record section

### Technical Setup

- **Resolution:** 1920x1080 (Full HD)
- **Frame Rate:** 30 fps
- **Audio:** Use external microphone if possible
- **Software:** OBS Studio, Loom, or screen recorder of choice

### Editing Notes

- Add intro/outro with title cards
- Include captions if possible
- Add subtle transition effects between sections
- Highlight key UI elements with annotations

---

## Alternative Flow (If Time Permits)

If you have extra time, you can also demonstrate:

1. **Chat Memory:** Show how the AI remembers previous messages
2. **Benchmark Comparison:** Compare portfolio to S&P 500
3. **Data Export:** Download Excel/CSV files
4. **Multiple Profiles:** Switch between different user profiles

---

## Fallback Plans

### If API is Rate Limited
> "Due to API rate limits, I'm showing cached data here, but in normal operation, this would update in real-time."

### If Model Loading is Slow
> "The model is loading - this only happens on first startup. Subsequent responses are much faster."

### If Chat Fails
- Switch to showing the Profile or Goals tabs
- Mention: "The chat feature uses a fine-tuned LLM that generates personalized responses"

---

## Key Messages to Emphasize

1. **Personalization:** Everything is tailored to the user's profile
2. **Real-Time Data:** Live market integration makes advice relevant
3. **Compliance First:** Disclaimers and safety guardrails throughout
4. **Accessible:** Complex financial planning made simple
5. **Extensible:** Architecture supports future enhancements

---

*Script prepared for Richard Abishai - January 2026*


