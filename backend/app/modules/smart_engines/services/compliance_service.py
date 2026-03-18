"""
Compliance Screening Service
Sanctions screening, name matching, and KYC checks
"""

import re
from typing import Dict, Any, List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CLEARED = "cleared"


class ComplianceService:
    """Compliance and sanctions screening engine"""

    # Sample sanctions list (in production, integrate with Dow Jones, World-Check, etc.)
    SAMPLE_SANCTIONS_LIST = [
        {"name": "John Doe", "type": "individual", "list": "OFAC"},
        {"name": "Jane Smith", "type": "individual", "list": "EU"},
        {"name": "Test Corp", "type": "entity", "list": "UN"},
    ]

    # High-risk countries
    HIGH_RISK_COUNTRIES = [
        "AFGHANISTAN",
        "IRAN",
        "NORTH KOREA",
        "SYRIA",
        "VENEZUELA",
        "CUBA",
        "BELARUS",
        "MYANMAR",
        "RUSSIA",
        "ZIMBABWE",
    ]

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize name for matching"""
        # Remove special characters, lowercase
        return re.sub(r"[^a-z0-9]", "", name.lower())

    @staticmethod
    def fuzzy_match(name1: str, name2: str, threshold: float = 0.8) -> bool:
        """
        Simple fuzzy name matching

        Args:
            name1: First name
            name2: Second name
            threshold: Match threshold (0-1)

        Returns:
            True if names match
        """
        s1 = ComplianceService.sanitize_name(name1)
        s2 = ComplianceService.sanitize_name(name2)

        if not s1 or not s2:
            return False

        # Exact match
        if s1 == s2:
            return True

        # Check if one contains the other
        if s1 in s2 or s2 in s1:
            return True

        # Simple Levenshtein-like check
        # (In production, use proper fuzzy matching library)
        matches = sum(1 for c in s1 if c in s2)
        ratio = matches / max(len(s1), len(s2))

        return ratio >= threshold

    @staticmethod
    def screen_name(name: str) -> Dict[str, Any]:
        """
        Screen a name against sanctions lists

        Args:
            name: Name to screen

        Returns:
            Screening result
        """
        hits = []
        sanitized_input = ComplianceService.sanitize_name(name)

        for entry in ComplianceService.SAMPLE_SANCTIONS_LIST:
            entry_sanitized = ComplianceService.sanitize_name(entry["name"])

            if ComplianceService.fuzzy_match(sanitized_input, entry_sanitized):
                hits.append(
                    {
                        "matched_name": entry["name"],
                        "type": entry["type"],
                        "list": entry["list"],
                        "risk_level": RiskLevel.HIGH,
                    }
                )

        if hits:
            return {
                "success": True,
                "status": "HIT",
                "risk_level": RiskLevel.HIGH,
                "hits": hits,
                "message": f"Found {len(hits)} match(es) in sanctions list",
            }

        return {
            "success": True,
            "status": "CLEAR",
            "risk_level": RiskLevel.CLEARED,
            "hits": [],
            "message": "No matches found",
        }

    @staticmethod
    def screen_country(country: str) -> Dict[str, Any]:
        """
        Screen a country for geopolitical risk

        Args:
            country: Country name

        Returns:
            Country risk assessment
        """
        country_upper = country.upper()

        if country_upper in ComplianceService.HIGH_RISK_COUNTRIES:
            return {
                "success": True,
                "country": country,
                "risk_level": RiskLevel.HIGH,
                "message": f"{country} is classified as high-risk",
            }

        return {
            "success": True,
            "country": country,
            "risk_level": RiskLevel.LOW,
            "message": f"{country} is not classified as high-risk",
        }

    @staticmethod
    def screen_parties(parties: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Screen all parties in a transaction

        Args:
            parties: List of party dicts with 'name' and 'country' keys

        Returns:
            Combined screening result
        """
        results = {
            "overall_risk": RiskLevel.LOW,
            "party_results": [],
            "high_risk_parties": [],
            "high_risk_countries": [],
        }

        for party in parties:
            name = party.get("name", "")
            country = party.get("country", "")

            # Screen name
            name_result = ComplianceService.screen_name(name)

            # Screen country
            country_result = (
                ComplianceService.screen_country(country) if country else None
            )

            party_result = {
                "party_name": name,
                "country": country,
                "name_screening": name_result,
                "country_screening": country_result,
            }

            results["party_results"].append(party_result)

            # Track high risk
            if name_result.get("risk_level") == RiskLevel.HIGH:
                results["high_risk_parties"].append(party)
                results["overall_risk"] = RiskLevel.HIGH

            if country_result and country_result.get("risk_level") == RiskLevel.HIGH:
                results["high_risk_countries"].append(country)
                if results["overall_risk"] != RiskLevel.HIGH:
                    results["overall_risk"] = RiskLevel.MEDIUM

        # Summary
        results["summary"] = {
            "total_parties": len(parties),
            "high_risk_count": len(results["high_risk_parties"]),
            "high_risk_country_count": len(results["high_risk_countries"]),
            "recommendation": (
                "BLOCK"
                if results["overall_risk"] == RiskLevel.HIGH
                else (
                    "REVIEW"
                    if results["overall_risk"] == RiskLevel.MEDIUM
                    else "APPROVE"
                )
            ),
        }

        return results

    @staticmethod
    def check_pep(name: str) -> Dict[str, Any]:
        """
        Check if person is a Politically Exposed Person

        Args:
            name: Person name

        Returns:
            PEP check result
        """
        # In production, integrate with PEP databases
        # This is a placeholder implementation
        return {
            "success": True,
            "name": name,
            "is_pep": False,
            "risk_level": RiskLevel.LOW,
            "message": "Not identified as PEP (sample implementation)",
        }


# Convenience functions
def screen_name(name: str) -> Dict[str, Any]:
    """Screen a name"""
    return ComplianceService.screen_name(name)


def screen_country(country: str) -> Dict[str, Any]:
    """Screen a country"""
    return ComplianceService.screen_country(country)


def screen_parties(parties: List[Dict[str, str]]) -> Dict[str, Any]:
    """Screen all parties"""
    return ComplianceService.screen_parties(parties)


def check_pep(name: str) -> Dict[str, Any]:
    """Check PEP status"""
    return ComplianceService.check_pep(name)
