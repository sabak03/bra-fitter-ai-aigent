"""
Fit Adjust Engine Module

This module implements a rule-based recommendation engine for bra fitting.

Key features:
- Evaluates user feedback using structured rules
- Applies weighted adjustments to band and cup sizes
- Resolves conflicting fit signals
- Generates explainable recommendations
- Provides style suggestions based on shape and comfort preferences

This is designed as a modular backend component for integration with
Streamlit (UI) fitAdjustApp.py
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set

allCups = ["AA","A","B","C","D","DD","E","F","FF","G","GG","H","HH","I","J","JJ","K","KK","L","M","N"]

@dataclass
class Rule:
    name: str
    condition: Callable[[Dict], bool]
    bandDelta: int = 0
    cupDelta: int = 0
    reason: str = ""
    confidence: int = 1
    category: str = "fit"
    styleTags: List[str] = field(default_factory=list)

@dataclass
class EngineResult:
    originalSize: str
    recommendedSize: str
    band: int
    cup: str
    bandChange: int
    cupChange: int
    totalConfidence: int
    changed: bool
    reasons: List[str]
    triggeredRules: List[str]
    styleSuggestions: List[str]

def clamp_cup_index(index: int) -> int:
    return max(0, min(index, len(allCups) - 1))

def dedupe_keep_order(items: List[str]) -> List[str]:
    seen: Set[str] = set()
    output: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output

def build_rules() -> List[Rule]:
    """
    Defines the rule set used by the fit adjust engine.

    Each rule includes:
    - a condition based on user feedback
    - band(2) and/or cup adjustments
    - explanatory reasoning
    - confidence weighting
    - style suggestions?

    Returns:
        List[Rule]: All rules used in evaluation
    """
    return [
        Rule(
            name="topSpillage",
            condition=lambda f: f["topSpillage"] in ["A little", "Yes"],
            cupDelta=1,
            reason="Top spillage suggests the cup volume may be too small (likely to go up half a cup).",
            confidence=2,
            styleTags=["full cup bras"],
        ),
        Rule(
            name="sideSpillage",
            condition=lambda f: f["sideSpillage"] in ["A little", "Yes"],
            cupDelta=1,
            reason="Side spillage suggests the cup may be cutting into breast tissue.",
            confidence=2,
            styleTags=["side-support bras", "full cup bras"],
        ),
        Rule(
            name="centreWire",
            condition=lambda f: f["centreWire"] == "No",
            cupDelta=1,
            reason="A floating centre gore can indicate that the cups are too small or too shallow.",
            confidence=2,
        ),
        Rule(
            name="bandRidesUp",
            condition=lambda f: f["bandRidesUp"] in ["A little", "Yes"],
            bandDelta=-2,
            cupDelta=1,
            reason="A band riding up often means the band is too loose, so a firmer band may help.",
            confidence=2,
        ),
        Rule(
            name="bandTight_noSpillage",
            condition=lambda f: (
                f["bandTooTight"] in ["A little", "Yes"]
                and f["sideSpillage"] == "No"
                and f["topSpillage"] == "No"
            ),
            bandDelta=2,
            cupDelta=-1,
            reason="If the band feels tight without spillage, a slightly larger band may be more comfortable.",
            confidence=1,
        ),
        Rule(
            name="cupGaping",
            condition=lambda f: (
                f["cupGaping"] in ["A little", "Yes"]
                and f["sideSpillage"] == "No"
                and f["topSpillage"] == "No"
                and f["shape"] != "Full on bottom"
            ),
            cupDelta=-1,
            reason="Cup gaping can suggest excess cup volume or a shape mismatch.",
            confidence=1,
            styleTags=["balconette", "plunge"],
        ),
        Rule(
            name="wiresDigging",
            condition=lambda f: f["wiresDigging"] in ["A little", "Yes"],
            reason="Wire discomfort may be a shape issue rather than a pure size issue.",
            confidence=1,
            category="style",
            styleTags=["softer wires", "comfort-focused styles"],
        ),
        Rule(
            name="strapsFalling",
            condition=lambda f: f["strapsFalling"] == "Yes",
            reason="Falling straps may point to strap placement or cup shape rather than size alone.",
            confidence=1,
            category="style",
            styleTags=["centred straps", "different cup shape"],
        ),
        Rule(
            name="topFull",
            condition=lambda f: f["shape"] == "Full on top",
            reason="Full on top shapes often suit more open upper cups or stretchy lace.",
            confidence=1,
            category="style",
            styleTags=["stretch lace upper cups", "balconette"],
        ),
        Rule(
            name="bottomFull",
            condition=lambda f: f["shape"] == "Full on bottom",
            reason="Full on bottom shapes can work well with lower-cut styles or plunges.",
            confidence=1,
            category="style",
            styleTags=["plunge", "lower-cut cups"],
        ),
        Rule(
            name="comfort",
            condition=lambda f: f["support"] == "Comfort",
            reason="Comfort-focused preferences may be better matched with softer or non-wired styles.",
            confidence=1,
            category="style",
            styleTags=["non-wired", "soft everyday bras"],
        ),
        Rule(
            name="lift",
            condition=lambda f: f["support"] == "Lift",
            reason="For more lift, firmer and more uplift-focused constructions are often better.",
            confidence=1,
            category="style",
            styleTags=["balconette", "side-support bras"],
        ),
    ]


def apply_conflict_logic(feedback: Dict, band_change: int, cup_change: int) -> tuple[int, int, List[str]]:
    """
    Resolves conflicting fit signals.

    Example:
    - A tight band + spillage → prioritise increasing cup over loosening band

    Returns adjusted band/cup changes and additional reasoning notes.
    """
    notes: List[str] = []
    spilling = feedback["topSpillage"] in ["A little", "Yes"] or feedback["sideSpillage"] in ["A little", "Yes"]
    tight = feedback["bandTooTight"] in ["A little", "Yes"]
    gaping = feedback["cupGaping"] in ["A little", "Yes"]

    if tight and spilling:
        if band_change > 0:
            band_change -= 2
            cup_change += 1
            notes.append("Tightness along with spillage can mean cups are too small, so a cup increase was prioritised over loosening the band.")

    if gaping and feedback["shape"] == "Full on bottom" and cup_change < 0:
        cup_change += 1
        notes.append("Gaping was not strongly reduced because full-on-bottom shapes may need a different cup shape rather than less cup volume.")

    return band_change, cup_change, notes


def evaluate_fit(band: int, cup: str, feedback: Dict) -> EngineResult:
    """
    Main evaluation for the engine.
    Evaluates user feedback against a set of predefined rules,
    aggregates band and cup adjustments, applying conflict resolution,
    and returns a structured recommendation.

    Args:
        band (int): Starting band size
        cup (str): Starting cup size
        feedback (Dict): User responses from fit form

    Returns:
        EngineResult: Final recommendation, including: size, reasons,
        triggered rules, and style suggestions
    """
    if cup not in allCups:
        raise ValueError(f"Unsupported cup size: {cup}")

    rules = build_rules()
    cupIndex = allCups.index(cup)
    bandChange = 0
    cupChange = 0
    totalConfidence = 0
    reasons: List[str] = []
    triggeredRules: List[str] = []
    styleSuggestions: List[str] = []

    for rule in rules:
        if rule.condition(feedback):
            triggeredRules.append(rule.name)
            reasons.append(rule.reason)
            # Aggregate rule confidence to reflect strength of evidence
            totalConfidence += rule.confidence 
            if rule.category == "fit":
                bandChange += rule.bandDelta
                cupChange += rule.cupDelta
            if rule.styleTags:
                styleSuggestions.extend(rule.styleTags)

    bandChange, cupChange, conflictNotes = apply_conflict_logic(feedback, bandChange, cupChange)
    reasons.extend(conflictNotes)

    newBand = band + bandChange
    if newBand < 26:
        newBand = 26
        reasons.append("Band size was fixed to the minimum supported value.")

    newCupIndex = clamp_cup_index(cupIndex + cupChange)
    newCup = allCups[newCupIndex]
    changed = (newBand != band) or (newCup != cup)
    if not changed:
        reasons.append("The feedback did not provide strong enough evidence for a size change, so the starting size was perfect.")

    return EngineResult(
        originalSize = f"{band}{cup}",
        recommendedSize = f"{newBand}{newCup}",
        band = newBand,
        cup = newCup,
        bandChange = newBand - band,
        cupChange = newCupIndex - cupIndex,
        totalConfidence = totalConfidence,
        changed = changed,
        reasons = dedupe_keep_order(reasons),
        triggeredRules = triggeredRules,
        styleSuggestions = dedupe_keep_order(styleSuggestions),
    )

def get_sister_sizes(band,cup,size):
    cupIndex = allCups.index(cup)
    sister = [(str(band+4)+allCups[cupIndex-2]),(str(band+2)+allCups[cupIndex-1]),size,(str(band-2)+allCups[cupIndex+1]),(str(band-4)+allCups[cupIndex+2])]
    return sister
