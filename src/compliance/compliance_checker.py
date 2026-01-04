"""
Compliance checker module.

Ensures regulatory compliance and adds disclaimers.
"""

import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComplianceChecker:
    """Checks and enforces compliance."""

    DISCLAIMERS = [
        "This is not financial advice. Please consult a qualified financial advisor.",
        "Past performance does not guarantee future results.",
        "Investments carry risk of loss. Only invest what you can afford to lose.",
        "This information is for educational purposes only.",
        "Market conditions can change rapidly. Recommendations may become outdated.",
    ]

    HIGH_RISK_KEYWORDS = [
        "crypto", "cryptocurrency", "bitcoin", "options", "derivatives",
        "margin", "leverage", "short selling", "penny stocks"
    ]

    def add_disclaimers(
        self,
        response: str,
        include_all: bool = False,
        risk_level: str = "moderate",
    ) -> str:
        """
        Add disclaimers to response.

        Args:
            response: Response text.
            include_all: If True, include all disclaimers. Otherwise, include primary ones.
            risk_level: Risk level of the recommendation ("low", "moderate", "high").

        Returns:
            Response with disclaimers appended.
        """
        disclaimers = self.DISCLAIMERS[:2] if not include_all else self.DISCLAIMERS
        
        # Add risk-specific warnings
        if risk_level == "high":
            disclaimers.insert(0, "⚠️ HIGH RISK WARNING: This recommendation involves significant risk of loss.")

        disclaimer_text = "\n\n---\n**Disclaimer:**\n" + "\n".join(f"- {d}" for d in disclaimers)
        disclaimer_text += f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return response + disclaimer_text

    def fact_check_stock_prices(
        self,
        response: str,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fact-check stock prices mentioned in response against market data.

        Args:
            response: Response text to check.
            market_data: Dictionary of market data (symbol -> price).

        Returns:
            Fact-check results.
        """
        if not market_data:
            return {"checked": False, "errors": []}

        # Extract symbol-price pairs from response
        # Look for patterns like: "AAPL at $185", "$185 for AAPL", "AAPL is $185", "AAPL ($185)"
        symbol_price_patterns = [
            r'\b([A-Z]{2,5})\s+(?:at|is|trading\s+at|currently)\s+\$(\d+\.?\d*)',  # "AAPL at $185"
            r'\$(\d+\.?\d*)\s+(?:for|of)\s+([A-Z]{2,5})\b',  # "$185 for AAPL"
            r'\b([A-Z]{2,5})\s*\(\s*\$(\d+\.?\d*)\s*\)',  # "AAPL ($185)"
            r'\b([A-Z]{2,5})\s+is\s+trading\s+at\s+\$(\d+\.?\d*)',  # "AAPL is trading at $185"
        ]
        
        symbol_price_pairs = []
        symbols_found = []  # Initialize early to avoid NameError
        
        # Extract pairs using patterns
        for pattern in symbol_price_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 2:
                    # Pattern might capture symbol first or price first
                    if groups[0].isalpha() and groups[1].replace('.', '').isdigit():
                        symbol, price = groups[0].upper(), groups[1]
                    elif groups[1].isalpha() and groups[0].replace('.', '').isdigit():
                        symbol, price = groups[1].upper(), groups[0]
                    else:
                        continue
                    symbol_price_pairs.append((symbol, float(price)))
                    if symbol not in symbols_found:
                        symbols_found.append(symbol)
        
        # Fallback: If no pairs found, try to match symbols and prices that appear close together
        if not symbol_price_pairs:
            symbol_pattern = r'\b([A-Z]{2,5})\b'
            price_pattern = r'\$(\d+\.?\d*)'
            
            # Extract all symbols found in response
            symbols_found = re.findall(symbol_pattern, response)
            prices_found = re.findall(price_pattern, response)
            
            # Find symbols and prices that appear within 50 characters of each other
            for symbol_match in re.finditer(symbol_pattern, response):
                symbol = symbol_match.group(1)
                symbol_start = symbol_match.start()
                
                # Look for prices within 50 characters before or after the symbol
                for price_match in re.finditer(price_pattern, response):
                    price_str = price_match.group(1)
                    price_start = price_match.start()
                    
                    if abs(price_start - symbol_start) <= 50:
                        try:
                            symbol_price_pairs.append((symbol, float(price_str)))
                            break  # Match first price found near symbol
                        except ValueError:
                            pass
        else:
            # If we found pairs in the first pass, also extract all symbols for completeness
            symbol_pattern = r'\b([A-Z]{2,5})\b'
            all_symbols = re.findall(symbol_pattern, response)
            # Combine with symbols from pairs (avoid duplicates)
            for symbol in all_symbols:
                if symbol not in symbols_found:
                    symbols_found.append(symbol)
        
        errors = []
        
        # Check each symbol-price pair against market data
        for symbol, mentioned_price in symbol_price_pairs:
            if symbol in market_data:
                market_price = market_data[symbol].get("price", None)
                if market_price:
                    try:
                        diff_pct = abs(mentioned_price - market_price) / market_price * 100
                        if diff_pct > 10:  # More than 10% difference
                            errors.append(
                                f"Price mismatch for {symbol}: "
                                f"mentioned ${mentioned_price:.2f}, "
                                f"market ${market_price:.2f} ({diff_pct:.1f}% difference)"
                            )
                    except (ValueError, ZeroDivisionError):
                        pass
        
        return {
            "checked": True,
            "symbols_found": list(set(symbols_found)),
            "errors": errors,
            "compliant": len(errors) == 0
        }

    def check_compliance(
        self,
        response: str,
        user_consent: bool = False,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check response for compliance.

        Args:
            response: Response text.
            user_consent: Whether user has given consent.
            market_data: Market data for fact-checking.

        Returns:
            Compliance check result.
        """
        warnings = []
        risk_level = "moderate"

        # Check for unrealistic promises
        unrealistic_keywords = ["guaranteed", "risk-free", "always", "never lose", "sure thing"]
        for keyword in unrealistic_keywords:
            if keyword.lower() in response.lower():
                warnings.append(f"Unrealistic language detected: '{keyword}'")

        # Check for high-risk investments
        response_lower = response.lower()
        high_risk_mentions = [kw for kw in self.HIGH_RISK_KEYWORDS if kw.lower() in response_lower]
        if high_risk_mentions:
            risk_level = "high"
            warnings.append(f"High-risk investments mentioned: {', '.join(high_risk_mentions)}")

        # Fact-check against market data
        fact_check_result = self.fact_check_stock_prices(response, market_data)
        if fact_check_result.get("errors"):
            warnings.extend(fact_check_result["errors"])

        # Check user consent
        if not user_consent:
            warnings.append("User consent not obtained")

        return {
            "compliant": len(warnings) == 0,
            "warnings": warnings,
            "risk_level": risk_level,
            "disclaimers_added": True,
            "fact_check": fact_check_result,
        }

    def log_advice(
        self,
        user_id: str,
        query: str,
        response: str,
        compliance_result: Dict[str, Any],
    ) -> None:
        """
        Log advice for audit trail.

        Args:
            user_id: User identifier.
            query: User's query.
            response: Generated response.
            compliance_result: Compliance check results.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query,
            "response_preview": response[:200],
            "compliance": compliance_result,
        }
        
        # In production, this would write to a database
        # For now, log to file
        log_dir = "logs/advice_audit"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"advice_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        import json
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Advice logged for user {user_id}")

