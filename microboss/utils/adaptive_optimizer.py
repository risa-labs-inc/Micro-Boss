import hashlib
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ===== Smart Cache System =====
_PROMPT_CACHE = {}
_DOMAIN_CACHE = {}
_MAX_CACHE_SIZE = 100

def get_cached_response(prompt: str) -> Optional[str]:
    """Get cached response for a prompt if available."""
    cache_key = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    
    if cache_key in _PROMPT_CACHE:
        return _PROMPT_CACHE[cache_key]["response"]
    
    # Similarity match for longer prompts
    if len(prompt) > 100:
        for k, v in _PROMPT_CACHE.items():
            stored_prompt = v.get("prompt", "")
            if len(stored_prompt) > 100 and prompt[20:100] == stored_prompt[20:100]:
                return v["response"]
    
    return None

def cache_response(prompt: str, response: str) -> None:
    """Cache an LLM response for future use."""
    cache_key = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    _PROMPT_CACHE[cache_key] = {"prompt": prompt, "response": response, "timestamp": time.time()}
    
    # Manage cache size
    if len(_PROMPT_CACHE) > _MAX_CACHE_SIZE:
        items = sorted(_PROMPT_CACHE.items(), key=lambda x: x[1]["timestamp"])
        for k, _ in items[:int(_MAX_CACHE_SIZE * 0.2)]:
            _PROMPT_CACHE.pop(k, None)

# ===== Self-Learning Domain System =====
def load_domain_knowledge():
    """Load previously discovered domain knowledge."""
    global _DOMAIN_CACHE
    
    domain_dir = Path(os.path.expanduser("~/.microboss/domains"))
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    domain_file = domain_dir / "domain_knowledge.json"
    if domain_file.exists():
        try:
            with open(domain_file, "r") as f:
                _DOMAIN_CACHE = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load domain knowledge: {e}")
            _DOMAIN_CACHE = {}

def save_domain_knowledge():
    """Save discovered domain knowledge for future use."""
    domain_dir = Path(os.path.expanduser("~/.microboss/domains"))
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    domain_file = domain_dir / "domain_knowledge.json"
    try:
        with open(domain_file, "w") as f:
            json.dump(_DOMAIN_CACHE, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save domain knowledge: {e}")

# Initialize domain knowledge
load_domain_knowledge()

def meta_analyze_domain(task: str, llm_client) -> Dict[str, Any]:
    """Use the LLM itself to analyze the task domain."""
    # Check if we've already analyzed a very similar task
    task_hash = hashlib.md5(task.encode("utf-8")).hexdigest()
    if task_hash in _DOMAIN_CACHE:
        return _DOMAIN_CACHE[task_hash]
    
    # Ask the LLM to analyze the task
    meta_prompt = f"""
    Analyze this task and provide domain information in JSON format:
    TASK: "{task}"
    
    Return ONLY a valid JSON object with these fields:
    - domain: The primary domain of this task (e.g., healthcare, web, finance, etc.)
    - complexity: A value from 1-10 indicating complexity
    - recommended_depth: Recommended decomposition depth (1-5)
    - needs_decomposition: Boolean indicating if task should be initially decomposed
    - archetype: System archetype if applicable (pipeline, monitoring, recursive, etc.)
    """
    
    try:
        response = llm_client.generate(meta_prompt)
        
        # Extract JSON from response
        json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            analysis = json.loads(json_str)
        else:
            # Fallback
            raise ValueError("Could not extract JSON from response")
        
        # Clean and standardize
        analysis = {
            "domain": analysis.get("domain", "general").lower(),
            "complexity": min(10, max(1, analysis.get("complexity", 5))),
            "recommended_depth": min(5, max(1, analysis.get("recommended_depth", 2))),
            "needs_decomposition": analysis.get("needs_decomposition", False),
            "archetype": analysis.get("archetype", "").lower()
        }
        
        # Cache for future use
        _DOMAIN_CACHE[task_hash] = analysis
        
        # Periodically save domain knowledge
        if len(_DOMAIN_CACHE) % 5 == 0:
            save_domain_knowledge()
        
        return analysis
        
    except Exception as e:
        logger.warning(f"Meta-analysis failed: {e}", exc_info=True)
        # Fallback analysis
        return {
            "domain": "general",
            "complexity": 5,
            "recommended_depth": 2,
            "needs_decomposition": len(task.split()) > 30,
            "archetype": ""
        }

def should_decompose(task: str, current_depth: int, analysis: Dict[str, Any]) -> bool:
    """Determine if a task should be decomposed based on analysis."""
    # Always respect maximum recommended depth
    if current_depth >= analysis["recommended_depth"]:
        return False
    
    # At root level, respect the analysis recommendation
    if current_depth == 0 and analysis["needs_decomposition"]:
        return True
    
    # Use complexity as a factor
    complexity = analysis["complexity"]
    complexity_threshold = 7 - current_depth  # Higher threshold at lower depths
    
    return complexity >= complexity_threshold

def get_enhanced_prompt(task: str, prompt_type: str, context: Dict[str, Any]) -> Optional[str]:
    """Get domain-aware prompt based on context."""
    domain = context.get("domain", "general")
    archetype = context.get("archetype", "")
    
    # Specialized prompts based on domain/archetype
    if prompt_type == "decomposition":
        return f"""
        Decompose this {domain} task{' with ' + archetype + ' architecture' if archetype else ''}:
        TASK: "{task}"
        
        Break this into 3-7 logical subtasks that collectively solve the problem.
        For each subtask, list its dependencies (which subtasks must be completed first).
        
        Return in format: [id, description, [dependencies]]
        """
    
    if prompt_type == "code_generation" and (domain != "general" or archetype):
        domain_desc = f"{domain}" if domain != "general" else ""
        arch_desc = f" {archetype}" if archetype else ""
        combined = f"{domain_desc}{arch_desc}".strip()
        
        return f"""
        Write Python code for this {combined} task:
        TASK: "{task}"
        
        Requirements:
        - Use appropriate design patterns for {combined} systems
        - Implement clean error handling
        - Save results to result.json
        """
    
    # Default to None for standard prompts
    return None

# ===== Wrapper functions for easy integration =====

def optimize_decomposition_decision(task: str, client, current_depth: int = 0):
    """Optimize decomposition decision - wrapper for easy integration."""
    analysis = meta_analyze_domain(task, client)
    return should_decompose(task, current_depth, analysis), analysis

def optimize_prompt(prompt: str, task: str, prompt_type: str, client, context: Dict[str, Any] = None):
    """Optimize prompt with caching and domain awareness - wrapper for easy integration."""
    context = context or {}
    
    # Try to get cached response first
    cached = get_cached_response(prompt)
    if cached:
        return cached
    
    # If the context has analysis, use it
    if "analysis" not in context and "domain" not in context:
        analysis = meta_analyze_domain(task, client)
        context["domain"] = analysis["domain"]
        context["archetype"] = analysis["archetype"]
        context["analysis"] = analysis
    
    # Check for enhanced prompt
    enhanced = get_enhanced_prompt(task, prompt_type, context)
    if enhanced:
        prompt = enhanced
    
    # Generate response
    response = client.generate(prompt)
    
    # Cache the response
    cache_response(prompt, response)
    
    return response 