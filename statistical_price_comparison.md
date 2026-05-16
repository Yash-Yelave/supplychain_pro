# Statistical Price Comparison Methods

Here are several statistical approaches to make the price comparison system more robust and realistic, rather than relying on a simple "lowest-to-highest" linear normalization. 

Currently, the linear model `(max_price - current) / (max_price - min_price)` treats prices equally across the range. However, this is vulnerable to extreme outliers (e.g., one absurdly high quote completely warps the scores for everyone else). 

Here are suggestions to improve this statistically:

### 1. Z-Score (Standardization)
Instead of comparing a price to the absolute minimum and maximum, compare it to the **average market price** using Standard Deviation. 
* **How it works:** You calculate the mean (average) price and the standard deviation of all quotes received. A supplier's score is based on how many standard deviations their price is from the average.
* **Why it's better:** It evaluates prices relative to the "normal" market rate. A price that is right at the mean gets an average score, while prices 1 or 2 standard deviations below the mean get exponentially higher scores. It handles normal market distributions beautifully.

### 2. Interquartile Range (IQR) & Median Comparison
If your quotes often have wild outliers (e.g., a supplier accidentally quoting 10x the normal price), the mean and standard deviation can be skewed. 
* **How it works:** You find the median (the exact middle price) instead of the average. You use the Interquartile Range (the middle 50% of quotes) to determine what a "normal" price difference is. You score suppliers based on their percentage deviation from the median.
* **Why it's better:** The median is highly resistant to extreme outliers. If 9 suppliers quote around AED 100 and one quotes AED 1,000, the median remains exactly where it should be, preventing the outlier from ruining the scoring scale.

### 3. Percentile Ranking
Instead of measuring the *amount* of the price difference, you measure the *rank* of the price within the distribution.
* **How it works:** If a supplier's price is cheaper than 80% of all other quotes, their score is simply 0.80 (the 80th percentile).
* **Why it's better:** It is incredibly stable and very easy to explain to users ("This supplier is cheaper than 80% of the market"). However, it ignores the magnitude of the difference (being $1 cheaper or $100 cheaper both just move you up one rank).

### 4. Market Premium/Discount Ratio
This approach creates a direct ratio against the closest competitor or the market baseline.
* **How it works:** You set a baseline (e.g., the median price or the second-lowest price). The score is calculated as `Baseline Price / Supplier Price`. 
* **Why it's better:** It naturally curves the score. If a supplier is exactly at the baseline, their score is 1.0. If they are half the price, they score 2.0 (which can be capped). If they are twice as expensive, they score 0.5. This accurately reflects the percentage savings they represent.

**Recommendation:**
For a procurement system, the **Median Comparison (Option 2)** or **Z-Score (Option 1)** usually yields the best real-world results. They identify the true "market rate" and accurately reward suppliers who offer a good deal without allowing a single ridiculous quote to break the normalization logic.
